import os
import shutil
import requests


def num_only(string):
    return int(''.join(list(filter(str.isdigit, string))))


def valid_filename(string):
    for idx, letter in enumerate(string):
        if letter != ' ':
            break
    string = string[idx:]
    sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in string:
        if char in sets:
            string = string.replace(char, '')
    return string


def check_exist_file(dest_file_path):
    if os.path.exists(dest_file_path):
        new_dest_file_path = os.path.splitext(dest_file_path)[0] + '_{}' + os.path.splitext(dest_file_path)[1]
        idx = 1
        while os.path.exists(new_dest_file_path.format(idx)):
            idx += 1
        dest_file_path = new_dest_file_path.format(idx)
    return dest_file_path


def download(url_or_response, download_file_path):
    download_file_path = check_exist_file(download_file_path)

    if isinstance(url_or_response, str):
        r = requests.get(url_or_response, stream=True)
    else:
        r = url_or_response
    if r.ok:
        with open(download_file_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print('Invalid URL or response {}, code: {}'.format(r.url, r.status_code))
    return download_file_path


def video_merge(ts_files, output_path, output_filename, delete_after_merge=True):
    output_path = os.path.abspath(os.path.join(output_path, output_filename + '.ts'))
    output_path = check_exist_file(output_path)
    cmd = 'copy /b {} "{}"'.format(
        ' + '.join(ts_files),
        output_path
        )
    os.popen(cmd).readlines()
    if os.path.exists(output_path):
        print('OUTPUT PATH: {}'.format(output_path))
        if delete_after_merge:
            for ts_file in ts_files:
                try:
                    os.remove(ts_file)
                except Exception as e:
                    print('Error Occur when delete {}, error: {}'.format(ts_file, e))
    else:
        print('Video Merge fail, ts file list: \n{}'.format('\n'.join(ts_files)))
