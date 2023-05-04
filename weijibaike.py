# -*- coding:utf-8 -*-

import sys
import requests
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import time

import ssl

import socket

# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()


def download(url, local_dir):
    # 延迟一秒再下，防止请求过密集导致ip被ban
    time.sleep(1)

    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)

    content_disposition = r1.headers.get("Content-Disposition")

    # 获取文件名称
    if content_disposition:
        file_name = content_disposition.split("filename=")[1].strip('"')
    else:
        file_name = url.split("/")[-1]

    # 为每一个国家建立一个文件夹
    dir = file_name.split("wik")[0]
    if dir != '':
        local_dir += dir + "/"



    # 文件夹不存在则新建一个
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    print("当前正在下载文件：", file_name)
    file_path = local_dir + file_name

    # 获取文件的总大小
    total_size = int(r1.headers['Content-Length'])
    # 先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0

    if temp_size == total_size:
        print("该文件已经下载过了！")
    else:
        # 显示一下已经下载了多少
        print(f"续传文件大小：{temp_size},文件总大小：{total_size}")

        # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
        headers = {'Range': 'bytes=%d-' % temp_size}
        # 重新请求网址，加入新的请求头的
        with requests.get(url, stream=True, verify=False, headers=headers) as r:
            # "ab"表示追加形式写入文件
            with open(file_path, "ab") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        temp_size += len(chunk)
                        f.write(chunk)
                        f.flush()

                    ###这是下载实现进度显示####
                    done = int(50 * temp_size / total_size)
                    sys.stdout.write("    《-----------下载进度：")
                    sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    sys.stdout.flush()
    print()


# 下载一个页面的所有链接
def download_wiki(url, local_dir):
    error_url = []
    links = []

    html = urlopen(url)  # 获取下载列表网页
    bs = BeautifulSoup(html, 'html.parser')  # 解析网页
    hyperlink = bs.find_all('a')  # 获取所有超链接

    for h in hyperlink:
        href = h.get('href')
        href = str(href)
        if href.endswith('.gz') and href.startswith('zh') and href.find('NS0') != -1:  # 获取所有以.gz结尾的文件
            links.append(url + href)

    del links[0]  # 删除第一个

    for i, url in enumerate(links):
        try:
            download(url, local_dir)
        except Exception as e:
            error_url.append(url, e)
            print(f"下载出现错误 {str(e)}")
    return links, error_url

def files_size(url):
    links = []
    html = urlopen(url)  # 获取下载列表网页
    bs = BeautifulSoup(html, 'html.parser')  # 解析网页
    hyperlink = bs.find_all('a')  # 获取所有超链接
    for h in hyperlink:
        href = h.get('href')
        href = str(href)
        if href.endswith('.gz'):  # 获取所有以.gz结尾的文件
            links.append(url + href)

    del links[0]  # 删除第一个

    total_sizes = 0
    for url in links:
        r1 = requests.get(url, stream=True, verify=False)
        file_size = int(r1.headers['Content-Length'])
        total_sizes += file_size
    return  total_sizes


if __name__ == '__main__':
    links, error_url = download_wiki("https://dumps.wikimedia.org/other/enterprise_html/runs/20230201/", "D:\\23711\desktop\wiki_project\wiki_data")
    # print(error_url)
    # total = files_size("https://dumps.wikimedia.org/other/enterprise_html/runs/20230201/")
    # print(total)