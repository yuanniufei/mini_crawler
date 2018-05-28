import os

import requests


# filename 带上格式后缀
def download_file(dir_path, filename, url):
    file_path = os.path.join(dir_path, filename)
    r = requests.get(url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
