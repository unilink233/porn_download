import os

def check(*paths):
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)


base = os.path.dirname(__file__)
download_path = os.path.abspath(os.path.join(base, 'download'))
cache_path = os.path.abspath(os.path.join(base, 'cache'))
chrome_driver_path = os.path.abspath(os.path.join(base, 'chrome_drivers'))
check(download_path, cache_path, chrome_driver_path)

# Convert to mp4 after download
convert_after_download = False
ext = '.mp4' if convert_after_download else '.ts'

# use 91porny cdn instead of 91porn to increase download speed.
use_91porny_if_possible = False
