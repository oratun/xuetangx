# coding: utf-8
"""
学堂在线公开课爬虫
需要:
      1.浏览器访问xuetangx.com, 登录后复制Cookie填写到代码中
      2.进入课程页面(如: http://www.xuetangx.com/courses/course-v1:TsinghuaX+10421094X_2015_2+sp/courseware/76976b23e6b24131a5fc9b5e3426e573/b45d1e9e41e14ff89721ede4c3547978/', 
        保存html源码为'xuetangx.html'用于解析
"""
import os
import re
from contextlib import closing
from multiprocessing import Pool
from pyquery import PyQuery as Pq
import requests

# 浏览器访问页面, F12获得Cookie后粘贴到下方对应处
headers = {
    'Cookie': 'xxxxxxx', # 此处填写浏览器network-headers处显示的cookie值
    'Host': 'www.xuetangx.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}


def download_subtitle(filename, url):
    r = requests.get(url, headers=headers)
    with open(filename, 'wb') as f:
        f.write(r.content)


def get_subtitle_url(param):
    return f'http://www.xuetangx.com{param}download'


def download_video(filename, url):
    """根据视频url下载视频"""
    with closing(requests.get(url, stream=True)) as r:
        chunk_size = 1024
        # content_size = int(r.headers.get('content-length'))
        with open(filename, 'wb') as f:
            for data in r.iter_content(chunk_size=chunk_size):
                f.write(data)
            return f'{filename} 下载完成。'


def get_video_url(source):
    """发送请求，获取视频url"""
    url = f'http://www.xuetangx.com/videoid2source/{source}'
    r = requests.get(url).json()
    video_url = r.get('sources').get('quality20')[0]
    return video_url


def get_url_param(url):
    """访问单节课程页面，获取页面中的参数用于获取视频url及字幕url"""
    url = 'http://www.xuetangx.com' + url
    r = requests.get(url, headers=headers)
    # print(r.text)
    # 9D27868BCEEB2E1A9C33DC5901307461
    video_param = re.search('data-ccsource=&#39;(.*)&#39;', r.text).group(1)
    # /course-v1:TsinghuaX+10421094X_2015_2+sp/xblock/block-v1:TsinghuaX+10421094X_2015_2+sp+type@video+block@1e960c7a5f084ebaba8714fb7bcce749/handler/transcript/
    sub_param = re.search(
        'data-transcript-translation-url=&#34;(.*)translation&#34;', r.text).group(1)
    return video_param, sub_param


def get_section(sections):
    """解析包含小节标题、url的html"""
    for section in sections:
        item = Pq(section)
        title = item('p:not(.subtitle)').text().strip()
        url = item('a').attr('href')
        yield {
            'section': title,
            'url': url,
        }


def get_chapter(filename):
    """返回各章的名称及包含若干小节的html"""
    with open(filename, encoding='utf-8') as f:
        pq = Pq(f.read())
        chapters = pq('div.chapter')
        for chapter in chapters:
            ch_name = Pq(chapter)('h3').text()
            sections = Pq(chapter)('li:not(.graded)')
            yield {
                'chapter': ch_name,
                'sections': sections,
            }


def run(name, url):
    path = os.path.dirname(name)
    if not os.path.exists(path):
        os.mkdir(path)
    video_param, sub_param = get_url_param(url)
    # video_url = get_video_url(video_param)
    # download_video(name, video_url)
    sub_url = get_subtitle_url(sub_param)
    sub_name = name.replace('.mp4', '.srt')
    download_subtitle(sub_name, sub_url)


def main():
    base_path = 'video'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    p = Pool()
    result = []
    for ch in get_chapter('xuetangx.html'):
        ch_name = ch.get('chapter')
        for se in get_section(ch.get('sections')):
            se_name = se.get('section')
            url = se.get('url')
            filename = os.path.join(base_path, ch_name, se_name+'.mp4')
            result.append(p.apply_async(run, (filename, url,)))
    p.close()
    p.join()
    print(result)

# source = get_url_param('/courses/course-v1:TsinghuaX+10421094X_2015_2+sp/courseware/8b871124eec84206a708d8251cd945f9/76a75e6c0dc3490c95e76d23b6ed9a47/')
# video_url = get_video_url(source)
# download_video('分块矩阵', video_url)


if __name__ == '__main__':
    main()
    # url = get_subtitle_url('/courses/course-v1:TsinghuaX+10421094X_2015_2+sp/xblock/block-v1:TsinghuaX+10421094X_2015_2+sp+type@video+block@1e960c7a5f084ebaba8714fb7bcce749/handler/transcript/')
