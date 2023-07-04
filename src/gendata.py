#!/usr/bin/env python

import argparse
import uuid
import os
import random
import string

from tqdm import tqdm

def main(size):
    file_name = f'./data/data-{size}M.data'
    file_name = os.path.abspath(file_name)
    count = size * 1000 * 1000

    data_len = 128 - 40 - 10
    data = ''.join(random.choices(' ' + string.ascii_lowercase + string.digits, k=data_len))

    print(f'Creating {file_name} with {count:,} records')

    with tqdm(total=count, desc='Creating data' ) as pbar:
        with open(file_name, 'w') as f:
            for i in range(count):
                uuid_str = str(uuid.uuid4())

                f.write(uuid_str)
                f.write(' ')
                f.write(f'{i:010} ')
                f.write(data)
                f.write('\n')
                pbar.update(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=10, help='Size in megabytes')
    args = parser.parse_args()

    main(args.size)
