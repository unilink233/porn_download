import os
import uuid
import requests

from common import valid_filename, video_merge_ffmpeg, download_ts
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
    print(m3u8_path)
    print(cdn_url)
    print(title)
    ts_urls = [cdn_url + ts_file for ts_file in parse_m3u8(m3u8_path)]
    if not ts_urls:
        print('M3U8 {} does not have any valid row.'.format(m3u8_path))
        return

    file_list = download_ts(ts_urls, cache_path, logout=True)
    video_merge_ffmpeg(file_list, download_path, title, delete_after_merge=True)


def input_param():
    m3u8_path = input('M3U8 PATH OR URL: ')

    cdn_url = input("CDN URL: ")
    if cdn_url[-1] != '/':
        cdn_url += '/'
    title = valid_filename(input("TITLE: "))
    return m3u8_path, cdn_url, title
    

if __name__ == "__main__":
    m3u8_path, cdn_url, title = input_param()
    main(m3u8_path, cdn_url, title)
    