import os
import uuid
import shutil
import requests
import subprocess


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


def download_ts(urls, download_path, uid):
    paths = []
    for idx, url in enumerate(urls):
        print('\rDownloading [{}/{}] videos'.format(idx + 1, len(urls)), end='')
        download_file_path = download(
            url, 
            os.path.abspath(os.path.join(download_path, "{}_{}.ts".format(uid, idx)))
        )

        if os.path.exists(download_file_path):
            paths.append(download_file_path)
    print('\n')
    return paths


def video_merge_ffmpeg(file_list, output_path, output_filename, delete_after_merge=True, use_origin_ext=True, ext='.ts'):
    """
    Param:
        file_list: List of input files
        output_path: Directory output path
        output_filename: output filename without extension
        delete_after_merge: will try to delete input file after merge
        use_origin_ext: will use same ext of first inputfile
        ext: if use_origin_ext is False, will use this.
    Return:
        
    """
    input_file = os.path.abspath(
        os.path.join(
            '.',
            '{}.txt'.format(str(uuid.uuid4()).replace('-', '').upper()[:10]))
        )
    if use_origin_ext:
        ext = os.path.splitext(file_list[0])[1]
    with open(input_file, 'w', encoding='utf-8', errors='ignore') as txtw:
        for file_name in file_list:
            txtw.write("file '{}'\n".format(file_name))
    output_path = os.path.join(output_path, output_filename + ext)
    base_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
    cmd = f'{base_path} -f concat -safe 0 -i "{input_file}" -c copy {output_path}'

    subprocess.run(cmd, timeout=float(3600), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.remove(input_file)
    if delete_after_merge:
        for file_name in file_list:
            try:
                os.remove(file_name)
            except Exception as e:
                print('delete file {} fail:{}'.format(file_name, e))
    print("{}'s video has been processed.".format(output_path))