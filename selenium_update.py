from genericpath import exists
import os
import shutil
import zipfile
import requests

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException


class NetworkException(Exception):
    pass


class DriverUpdateException(Exception):
    pass


class ChromeDriver(object):
    def _get_latest_version(self):
        """ get latest driver version """
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        r = requests.get(url)
        if not r.ok:
            print('unable to get latest driver version.')
            raise NetworkException
        return r.content.decode('utf-8')

    def _get_latest_version_of_major_version(self, major_version):
        """ get latest version of a major version """
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}".format(major_version)
        r = requests.get(url)
        if not r.ok:
            return
        return r.content.decode('utf-8')

    def _check_version_exist(self, chrome_driver_path, version):
        """ Check if a specific or latest version in driver path """
        for file_name in os.listdir(chrome_driver_path):
            return True if f'chromedriver{version}' in file_name else False
    
    def _get_chrome_version(self):
        """
            Get minor version
        """
        import winreg
        try:
            # 从注册表中获得版本号
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, type = winreg.QueryValueEx(key, 'version')
            return version
        except WindowsError as e:
            print('check Chrome failed:{}'.format(e))

    def _download_file(self, url, download_path):
        r = requests.get(url, stream=True)
        if not r.ok:
            print('Download Webdriver fail, status code {} with url {}'.format(r.status_code, url))
        with open(download_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    def _unzip_file(self, zip_path, unzip_path, delete_zip=False):
        # unzip file
        if not os.path.exists(unzip_path):
            os.mkdir(unzip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)
        if delete_zip:
            os.remove(zip_path)

    def _update(self, chrome_driver_path, version):
        # if major version
        if '.' not in str(version):
            version = self._get_latest_version_of_major_version(version)
        # minor version
        else:
            version = self._get_latest_version_of_major_version(version.split('.')[0])

        webdriver_path = os.path.join(chrome_driver_path, 'chromedriver{}.exe'.format(version))
        if os.path.exists(webdriver_path):
            print('version: {} driver already exist.'.format(version))
            return

        # download webdriver
        driver_url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(version)
        
        temp_path = os.path.join(chrome_driver_path, 'tmp')
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        download_path = os.path.abspath((os.path.join(temp_path, '{}.zip'.format(version))))
        
        self._download_file(driver_url, download_path)
        
        self._unzip_file(download_path, temp_path, delete_zip=True)

        os.rename(os.path.join(temp_path, 'chromedriver.exe'), webdriver_path)

        print('version: {} as been download to {}'.format(version, webdriver_path))
        return webdriver_path

    def update(self, chrome_driver_path, version=False, raise_error=False):
        """ download driver into local path
        Param:
            chrome_driver_path:
                local driver path
            version:
                major version or None, if it is None will update to latest version. 
                major version will be like '92', '94'
        Return:
            driver path or None
        """
        if raise_error:
            self._update(chrome_driver_path, version=version)
        else:
            try:
                self._update(chrome_driver_path, version=version)
            except Exception as e:
                print('Update chrome driver fail: {}'.format(e))

    def _get_driver_file(self, chrome_driver_path):
        """ get driver file abs path from chrome_driver_path"""
        chrome_version = self._get_chrome_version()
        drivers_match_chrome_version, drivers_not_match_chrome_version = [], []
        for key in os.listdir(chrome_driver_path): 
            if 'chromedriver' in key:
                # match current chrome version
                if "chromedriver{}".format(chrome_version) in key:
                    drivers_match_chrome_version.append(os.path.abspath(
                        os.path.join(chrome_driver_path, key)
                    ))
                # not match current version
                else:
                    drivers_not_match_chrome_version.append(os.path.abspath(
                        os.path.join(chrome_driver_path, key)
                    ))
        drivers_not_match_chrome_version.sort(reverse=True)
        return drivers_match_chrome_version + drivers_not_match_chrome_version

    def get_driver(self, chrome_driver_path, **kargs):
        """ Search available webdriver in path"""
        chrome_driver_filenames = self._get_driver_file(chrome_driver_path)

        for chrome_driver_filename in chrome_driver_filenames:
            try:
                driver = webdriver.Chrome(chrome_driver_filename, **kargs)
                return driver
            except SessionNotCreatedException as e:
                continue
            except Exception as e:
                continue

    def update_and_get_driver(self, chrome_driver_path, chrome_options=None, raise_error=True, **kargs):
        """ update driver then get webdriver """
        # check version
        chrome_version = self._get_chrome_version()
        if not self._check_version_exist(chrome_driver_path, version=chrome_version):
            print('Downloading Chrome Version: {} webdriver.'.format(chrome_version))
            self.update(chrome_driver_path, version=chrome_version, raise_error=raise_error)

        driver = self.get_driver(chrome_driver_path, chrome_options=chrome_options, **kargs)
        if driver:
            return driver
        else:
            raise DriverUpdateException('Cannot find available chrome driver, please download it to {}'.format(chrome_driver_path))
        

if __name__ == "__main__":
    ChromeDriver().update_and_get_driver('.')
