# 按类别下载搜狗拼音细胞词库，用于收集自然语言处理的语料库。
import os
import random
import time

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from mini_crawler.driver import HeadlessChromeDriver
from mini_crawler.util import download_file

if __name__ == '__main__':
    driver = HeadlessChromeDriver()

    dir_name = '理财'
    dir_path = os.path.join(os.getcwd(), 'downloads', 'sogou_pinyin_dict', dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # url = 'https://pinyin.sogou.com/dict/cate/index/132'  # 医学
    url = 'https://pinyin.sogou.com/dict/cate/index/390'  # 理财

    while url:
        html = driver.get(url=url)

        soup = BeautifulSoup(html, 'html.parser')

        dict_detail_block_elems = soup.find_all('div', {'class': 'dict_detail_block'})
        for block_elem in dict_detail_block_elems:
            title = block_elem.find('div', 'detail_title').text
            download_url = block_elem.find("div", {"class": "dict_dl_btn"}).a['href']
            download_file(dir_path=dir_path, filename='{}.scel'.format(title), url=download_url)
            time.sleep(random.randint(1, 3))
            print('{}.scel'.format(title))

        dict_page_list_elem = soup.find('div', {'id': 'dict_page_list'})

        if '下一页' in dict_page_list_elem.text:
            last_child = None
            for child in dict_page_list_elem.ul.children:
                if type(child) is NavigableString:
                    continue
                last_child = child
            url = 'https://pinyin.sogou.com{}'.format(last_child.a['href'])
            print(url)
        else:
            url = None
            print('End')

    driver.quit()
