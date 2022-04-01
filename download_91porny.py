import os
import json
import uuid
import requests


from sys import argv
from bs4 import BeautifulSoup as bs

from common import num_only, download, video_merge, valid_filename
from constants import download_path, cache_path


def get_uid_and_title(url):
    r = requests.get(url)
    if r.ok:
        soup = bs(r.text, 'html.parser')
        script = soup.find_all(name='script', attrs={'type': 'application/ld+json'})
        if not script:
            print('Cannot get uid with url {}'.format(url))
            return None, None
        api_result = json.loads(script[0].text)
        if 'thumbnailUrl' in api_result:
            uid = num_only(api_result['thumbnailUrl'].split('/')[-1])
            title = soup.title.text.split(' - 91视频')[0]
            return uid, valid_filename(title)
    return None, None


def check_hd(uid):
    url = 'https://v100.wktfkj.com/hls/{}/index0.ts'.format(uid)
    r = requests.get(url)
    if r.ok:
        return True
    else:
        return False


def download_with_uid(uid, download_path, hd=False):
    if hd:
        url = 'https://v100.wktfkj.com/hls/{}'.format(uid) + "/index{}.ts"
    else:
        url = "https://cdn3.jiuse.cloud/hls/{}".format(uid) + "/index{}.ts"
    idx = 0
    file_list = []
    r = requests.get(url.format(idx), stream=True)
    while r.ok:
        print('downloading {}\r'.format(idx), end='')
        download_file_path = os.path.abspath(os.path.join(download_path, '{}_{}.ts'.format(uid, idx)))
        
        download(r, download_file_path)

        if os.path.exists(download_file_path):
            file_list.append(download_file_path)
        idx += 1
        r = requests.get(url.format(idx), stream=True)
    return file_list



def get_sorted_ts_filelist(file_names):
    file_names = sorted(file_names, key=lambda k: num_only(k))
    return file_names


def generate_concat_file(file_names):
    concat_path = os.path.abspath('./{}.txt'.format(str(uuid.uuid4()).replace('-', '').upper()[:10]))
    txtw = open(concat_path, 'w', encoding='utf-8', errors='ignore')
    for file_name in file_names:
        txtw.write("file '{}'\n".format(file_name))
    txtw.close()
    return concat_path


def download_91porny(url):
    uid, title = get_uid_and_title(url)

    if not uid:
        print('cannot parse {}'.format(uid))
        exit()

    print('UID: {}, TITLE: {}'.format(uid, title))

    hd = check_hd(uid)

    if hd:
        print('UID:{} has HD version'.format(uid))

    file_list = download_with_uid(uid, cache_path, hd=hd)

    file_names = get_sorted_ts_filelist(file_list)
    
    video_merge(file_names, download_path, title)


if __name__ == "__main__":
    url = input('URL: ') if len(argv) < 2 else argv[1]

    download_91porny(url)
