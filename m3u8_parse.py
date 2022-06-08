import os
import uuid
import requests

from common import valid_filename, download, video_merge_ffmpeg
from constants import cache_path, download_path


class InvaildInputException(Exception):
    ...


def parse_m3u8(path):
    def valid_ts(row):
            if '.ts' in row and row[0] != '#':
                return True
            else:
                return False
    result = []
    # url
    if 'http' in path:
        r = requests.get(path)
        if r.ok:
            for row in r.content.decode('utf-8').split('\n'):
                if valid_ts(row):
                    result.append(row.replace('\n', ''))
    else:
        # local path
        if not os.path.exists(path):
            print(f'Path {path} not exist')
            raise InvaildInputException
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as txtr:
            for row in txtr:
                if valid_ts(row):
                    result.append(row.replace('\n', ''))
    return result


def main(m3u8_path, cdn_url, title):
    ts_files = parse_m3u8(m3u8_path)
    if not ts_files:
        print('M3U8 {} does not have any valid row.'.format(m3u8_path))
        return
    
    ts_urls = [cdn_url + ts_file for ts_file in ts_files]

    random_prefix = str(uuid.uuid4()).upper()[:5]
    file_list = []
    for idx, url in enumerate(ts_urls):
        filename = f'{random_prefix}_{str(idx).zfill(len(str(len(ts_urls))))}.ts'
        file_list.append(os.path.join(cache_path, filename))
        download(url, os.path.join(cache_path, filename))
        print(f'[{idx}/{len(ts_urls)}] Downloading')
    
    video_merge_ffmpeg(file_list, download_path, title, delete_after_merge=True)

def input_param():
    m3u8_path = os.path.abspath(input('M3U8 PATH OR URL: '))

    cdn_url = input("CDN URL: ")
    if cdn_url[-1] != '/':
        cdn_url += '/'
    title = valid_filename(input("TITLE: "))
    return m3u8_path, cdn_url, title
    

if __name__ == "__main__":
    m3u8_path, cdn_url, title = input_param()
    main(m3u8_path, cdn_url, title)
    