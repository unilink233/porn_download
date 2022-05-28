import os
import requests

from sys import argv
from bs4 import BeautifulSoup as bs
from selenium.webdriver import ChromeOptions
from urllib.parse import urlparse, parse_qs

from common import valid_filename, video_merge, download_ts
from constants import download_path, chrome_driver_path, cache_path, use_91porny_if_possible
from selenium_update import ChromeDriver
from download_91porny import download_91porny, get_uid_and_title



DEFAULT_CDN = "https://la.killcovid2021.com/m3u8"


def get_ts_urls(uid, cdn_url=DEFAULT_CDN):
    def valid_ts_filename(filename):
        if '.ts' in filename and filename.replace('.ts', '').isdigit():
            return True
        else:
            return False
    url = "{}/{}/{}.m3u8".format(cdn_url, uid, uid)
    r = requests.get(url)
    if r.ok:
        return ["{}/{}/{}".format(cdn_url, uid, ts_filename) for ts_filename in r.text.split('\n') if valid_ts_filename(ts_filename)]


def get_info(url, driver):
    driver.get(url)
    soup = bs(driver.page_source, "html.parser")
    video_containers = soup.find_all(name='div', attrs={'id': 'VID'})
    if video_containers:
        uid = video_containers[0].text
        # if 'thumb' in thumb_url:
        #     uid = thumb_url.split('/')[-1].split('.')[0]
        title = soup.title.text.split('\n')[0]
        driver.quit()
        return uid, valid_filename(title)
    else:
        return None, None


def check():
    chrome_options = ChromeOptions()
    chrome_options.add_argument('log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])

    chrome_version = ChromeDriver()._get_chrome_version()
    if not ChromeDriver()._check_version_exist(chrome_driver_path, version=chrome_version):
        driver = ChromeDriver().update_and_get_driver(chrome_driver_path, chrome_options=chrome_options)
    else:
        driver = ChromeDriver().get_driver(chrome_driver_path, chrome_options=chrome_options)
    return driver


def download_91porn(url):
    if use_91porny_if_possible:
        query = parse_qs(urlparse(url).query)
        porny_url = "https://91porny.com/video/view/{}".format(query['viewkey'][0])
        uid, title = get_uid_and_title(porny_url)
        if uid:
            print('Found Same version in 91porny.')
            download_91porny(porny_url)
            return

    driver = check()

    uid, title = get_info(url, driver)

    print('UID:{} TITLE: {}'.format(uid, title))
    
    ts_urls = get_ts_urls(uid)
    
    print('{} ts files found.'.format(len(ts_urls)))
    
    ts_files = download_ts(ts_urls, cache_path, uid)

    video_merge(ts_files, download_path, title)


if __name__ == '__main__':
    url = input('URL: ') if len(argv) < 2 else argv[1]

    download_91porn(url)
