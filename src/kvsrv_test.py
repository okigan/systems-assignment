import sys

# sys.path.insert(0, '../src')

from kvsrv import *

def test_get():
    kv_service = KVServiceMock("mock_data.txt")

    kv_service.get("mock_key")

    assert True

def test():
    data_file_name = "example.data"
    for kv_service in [KVServiceBisect(data_file_name), KVServiceDict("example.data")]:
        kv_service.build_index()
        kv_service.load()

        with open(data_file_name, 'r') as f:
            for line in f:
                key, data = line.split(' ', maxsplit=1)
                data = data[:-1].encode('utf-8')
                result = kv_service.get(key)

                assert result == data

