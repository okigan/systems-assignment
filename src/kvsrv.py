import argparse
import bisect
import mmap
import logging
import os
import random
import sys
import time

from tqdm import tqdm
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
import uvicorn


class SupportsLenAndGetItem:
    def __init__(self, mmapped_file, value_size, width=None, prefix=0, offset=0):
        if width is None:
            width = value_size

        self.mapped_file = mmapped_file
        self.value_size = value_size
        self.width_in_bytes = width
        self.prefix_in_bytes = prefix
        self.offset_in_bytes = offset

    def __len__(self):
        return (self.mapped_file.size() - self.offset_in_bytes) // self.width_in_bytes

    def __getitem__(self, index):
        offset = (
            self.offset_in_bytes + index * self.width_in_bytes + self.prefix_in_bytes
        )
        value_bytes = self.mapped_file[offset : offset + self.value_size]
        return int.from_bytes(value_bytes)


OFFSET_SIZE = 5
UUID_STRING_SIZE = 36


def get_uuid_int(mm, offset: int):
    uuid_str = get_uuid_str(mm, offset)
    return UUID(uuid_str).int


def get_uuid_str(mm, offset: int):
    uuid_str = mm[offset : offset + UUID_STRING_SIZE].decode()
    return uuid_str


class KVServiceBisect:
    def __init__(self, data_file_name):
        self.data_file_name = data_file_name
        self.index_file_name = data_file_name + ".index"

    def get(self, key):
        uuid_key = UUID(key)

        key_int = uuid_key.int

        index = bisect.bisect_left(
            self.wrap_index, key_int, key=lambda x: get_uuid_int(self.mmap_data, x)
        )
        if get_uuid_int(self.mmap_data, self.wrap_index[index]) != key_int:
            raise KeyError(f"Key {key} not found")

        offset = self.wrap_index[index]

        end = self.mmap_data.find(b"\n", offset + UUID_STRING_SIZE + 1)

        return self.mmap_data[offset + UUID_STRING_SIZE + 1 : end]

    def build_index(self):
        data_file = self.data_file_name
        index_file_name = self.index_file_name

        if os.path.exists(index_file_name):
            return index_file_name

        print("KVServiceBisect building index...")
        st = time.time()

        index = []
        with tqdm(total=os.path.getsize(data_file)) as pbar:
            with open(data_file, "r") as f:
                mmap_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                offset = 0
                for line in f:
                    index.append(offset)
                    offset += len(line)
                    pbar.update(len(line))

        print("Sorting index...")
        index.sort(key=lambda x: get_uuid_int(mmap_data, x))

        with open(index_file_name, "wb") as f:
            for pos in index:
                f.write(pos.to_bytes(OFFSET_SIZE))

        print(
            f"KVServiceBisect index built: {len(index):,} entries in {time.time() - st}s"
        )

        return index_file_name

    def load(self):
        print("Loading data...")
        st = time.time()

        with open(self.data_file_name, "rb") as f:
            self.mmap_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        with open(self.index_file_name, "rb") as f:
            self.mmap_index = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        self.wrap_index = SupportsLenAndGetItem(self.mmap_index, OFFSET_SIZE)

        print(
            f"KVServiceBisect index loaded: {len(self.wrap_index):,} entries in {time.time() - st}s"
        )

    def head_keys(self):
        result = []
        for idx, offset in enumerate(self.wrap_index):
            if idx > 1000:
                break
            uuid_int = get_uuid_int(self.mmap_data, offset)
            result.append(str(UUID(int=uuid_int)))

        return result


class KVServiceDict:
    def __init__(self, data_file_name):
        self.data_file_name = data_file_name

    def get(self, key):
        key_int = UUID(key).int

        index = self.offset_dict.get(key_int)
        if index is None:
            raise KeyError(f"Key {key} not found")

        offset = index

        self.mmap_data.seek(offset + UUID_STRING_SIZE + 1)
        data = self.mmap_data.readline()

        return data[:-1]

    def build_index(self):
        print("KVServiceDict building index...")
        st = time.time()

        data_file = self.data_file_name

        offset_dict = {}
        with tqdm(total=os.path.getsize(data_file)) as pbar:
            with open(data_file, "r") as f:
                offset = 0
                for line in f:
                    uuid_str, _ = line.split(" ", maxsplit=1)
                    uuid_num = UUID(uuid_str).int
                    offset_dict[uuid_num] = offset
                    offset += len(line)
                    pbar.update(len(line))

        self.offset_dict = offset_dict

        print(
            f"KVServiceDict index built: {len(offset_dict):,} entries in {time.time() - st:,}s"
        )
        size_of_offset_dict = sys.getsizeof(offset_dict)

        print(f"KVServiceDict index size: {size_of_offset_dict:,} bytes")

    def load(self):
        with open(self.data_file_name, "rb") as f:
            self.mmap_data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    def head_keys(self):
        result = []
        for idx, uuid_int in enumerate(self.offset_dict.keys()):
            if idx > 100:
                break
            result.append(str(UUID(int=uuid_int)))

        return result


class KVServiceMock:
    def __init__(self, data_file_name):
        self.data_file_name = data_file_name

    def get(self, _):
        return "mock data"

    def build_index(self):
        pass

    def load(self):
        pass

    def head_keys(self):
        result = ["mock_key"]

        return result


app = FastAPI()
kv_service = None


@app.get("/get/")
async def get(key: str):
    if kv_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        return kv_service.get(key)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/head_keys/")
async def head_keys():
    keys = kv_service.head_keys()
    return {"keys": keys}


def minibench(kv_service: KVServiceBisect, request_count=200 * 1000):
    non_present_keys = [str(uuid4()) for _ in range(1000)]
    present_keys = kv_service.head_keys()
    random.shuffle(present_keys)

    st = time.time()
    st_ops = 0

    for i in range(request_count):
        key = non_present_keys[i % len(non_present_keys)]
        try:
            kv_service.get(key)
        except KeyError:
            pass

        key = present_keys[i % len(present_keys)]
        kv_service.get(key)

        ops_count = 2 * i

        if ops_count % (100 * 1000) == 0:
            elapsed_time = time.time() - st
            elapsed_ops = ops_count - st_ops
            print("Test pass execution time:", elapsed_time, "s")
            print(f"Average time per query: {elapsed_time / (elapsed_ops + 1)}s")
            print(f"RPS: {elapsed_ops / elapsed_time:,}")
            st = time.time()
            st_ops = ops_count

    print("\n\n")


def main(uvicorn_run, data_file_name, kvservice_type=dict, key=None):
    global kv_service

    if kvservice_type == "bisect":
        kv_service = KVServiceBisect(data_file_name)
    elif kvservice_type == "dict":
        kv_service = KVServiceDict(data_file_name)
    elif kvservice_type == "mock":
        kv_service = KVServiceMock(data_file_name)
    else:
        raise ValueError("Invalid kvservice_type")

    kv_service.build_index()
    kv_service.load()

    if key is not None:
        print(kv_service.get(key))
        return

    minibench(kv_service)

    # logging.disable(logging.CRITICAL) # uncomment for benchmarking

    if uvicorn_run:
        uvicorn.run(app, host="0.0.0.0", port=5000, timeout_keep_alive=60)


if __name__ == "kvsrv":
    print(f"kvsrv sys.argv={sys.argv}")

    if len(sys.argv) >= 1 and sys.argv[0].find("uvicorn") != -1:
        print("here")
        main(False, "./data/data-1M.data", "dict")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file_name", help="Data file name")
    parser.add_argument(
        "--kvservice_type",
        choices=["bisect", "dict", "mock"],
        default="dict",
        help="KVService type",
    )
    parser.add_argument("--key", help="Key to retrieve")
    print(f"args={sys.argv}")
    args = parser.parse_args()

    main(True, args.data_file_name, args.kvservice_type, args.key)
