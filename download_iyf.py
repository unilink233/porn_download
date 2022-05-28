import json
import requests

from sys import argv
from uuid import uuid4
from bs4 import BeautifulSoup as bs

from common import valid_filename, download_ts, video_merge_ffmpeg
from constants import download_path, chrome_driver_path, cache_path, use_91porny_if_possible

from selenium_update import ChromeDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def get_key(page_source):
    soup = bs(page_source, "html.parser")
    key_container = soup.find_all(name='div', attrs={"class":"vg-b"})
    if key_container:
        key = key_container[0]['style'].split('pub=')[-1]
        for idx in range(len(key)):
            if not key[idx].isdigit() and not key[idx].isalpha():
                break
        key = key[:idx]
        return key
    return 

def parse_m3u8(url):
    r = requests.get(url)
    base_url = url.split('chunklist.m3u8')[0]
    if r.ok:
        urls = []
        lines = r.content.decode('utf-8').split('\n')
        for line in lines:
            if len(line) >= 1 and line[0] != '#' and '.ts' in line:
                urls.append(base_url + line)
    return urls

def get_json_key(j, key):
    if not j:
        return
    return j[key] if key in j else None


def get_m3u8(logs):
    """
        get m3u8 url from chromedriver logs
    """
    for log in logs:
        try:
            if 'message' in log:
                message = json.loads(log['message'])
                message_body = get_json_key(message, 'message')
                params = get_json_key(message_body, 'params')
                request = get_json_key(params, 'request')
                url = get_json_key(request, 'url')
                if url and '.m3u8' in url:
                    return url
        except Exception as e:
            # print('Error Occur, error: {}'.format(e))
            pass

def get_title(title):
    title = title.split('在线观看')[0]
    if title[-1] == '-':
        title = title[:-1]
    return title


def download_iyf(url, try_times=3):
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = ChromeDriver().update_and_get_driver(chrome_driver_path, desired_capabilities=caps)

    driver.get(url)
    m3u8_url = get_m3u8(driver.get_log('performance'))
    
    if not m3u8_url and try_times > 0:
        try_times -= 1
        print('Parse Fail with url: {}, try: {}'.format(url, try_times))
        driver.quit()
        download_iyf(url, try_times=try_times)
        return
    ts_urls = parse_m3u8(m3u8_url)
    title = valid_filename(get_title(driver.title))

    uid = str(uuid4()).replace('-', '').upper()[:10]
    ts_files = download_ts(ts_urls, cache_path, uid)

    driver.quit()

    video_merge_ffmpeg(ts_files, download_path, title)
    


if __name__ == '__main__':
    url = input('URL: ') if len(argv) < 2 else argv[1]
    download_iyf(url)