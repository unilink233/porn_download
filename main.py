from sys import argv
from download_91porn import download_91porn
from download_91porny import download_91porny


if __name__ == "__main__":
    if len(argv) < 2:
        url = input("URL: ")
    else:
        url = argv[1]
    
    if '91porny.com' in url:
        download_91porny(url)
    elif '91porn.com' in url:
        download_91porn(url)
    else:
        print('{} is not in supported sites.'.format(url))