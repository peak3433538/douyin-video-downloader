#!/usr/bin/env python3
"""
抖音视频下载器 v2
从抖音分享链接或视频ID下载视频

使用方法：
    python3 douyin_download.py "抖音链接"
    python3 douyin_download.py "视频ID"

核心要点：
1. 必须使用iPhone User-Agent
2. 视频URL在HTML的JavaScript里，需要解析JSON
3. 或者直接使用已知视频ID和video_id
"""

import requests
import re
import json
import sys
import argparse
from urllib.parse import urlparse, parse_qs, unquote
import os

# iPhone User-Agent - 抖音需要伪装成手机浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.douyin.com/',
}

def get_final_url(short_url):
    """获取抖音短链接跳转后的真实URL"""
    try:
        r = requests.head(short_url, headers=HEADERS, allow_redirects=True, timeout=10)
        return r.url
    except Exception as e:
        print(f"获取真实URL失败: {e}")
        return short_url

def extract_video_id(url):
    """从URL中提取视频ID"""
    # 匹配 v.douyin.com/xxxxx 格式
    match = re.search(r'/(\w{19,})', url)
    if match:
        return match.group(1)
    # 匹配 query参数
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if 'id' in params:
        return params['id'][0]
    return None

def get_video_info(url):
    """获取视频信息"""
    # 获取页面HTML
    r = requests.get(url, headers=HEADERS, timeout=10)
    html = r.text
    
    # 从HTML中提取JSON数据
    # 抖音的视频信息在<script id="RENDER_DATA">或类似位置
    
    # 方法1: 查找RENDER_DATA
    pattern = r'RENDER_DATA\s*=\s*([^;]+);'
    match = re.search(pattern, html)
    
    if match:
        import urllib.parse
        json_str = urllib.parse.unquote(match.group(1))
        data = json.loads(json_str)
        
        # 提取视频信息
        if 'aweme' in data:
            aweme = data['aweme']['detail']
            video_info = {
                'title': aweme.get('desc', ''),
                'video_id': aweme.get('aweme_id', ''),
                'author': aweme['author'].get('nickname', ''),
                'digg_count': aweme.get('statistics', {}).get('digg_count', 0),
            }
            
            # 获取视频播放地址
            if 'video' in aweme and 'play_addr' in aweme['video']:
                play_addr = aweme['video']['play_addr']
                if 'url_list' in play_addr:
                    video_info['video_url'] = play_addr['url_list'][0]
                    
            return video_info
    
    # 方法2: 查找window.__INITIAL_STATE__
    pattern2 = r'window\.__INITIAL_STATE__\s*=\s*([^;]+);'
    match2 = re.search(pattern2, html)
    if match2:
        try:
            json_str = match2.group(1)
            data = json.loads(json_str)
            # 解析数据...
        except:
            pass
    
    return None

def download_video(video_url, output_path=None):
    """下载视频"""
    # 替换play_addr为play（去水印）
    download_url = video_url.replace('/playwm/', '/play/')
    
    r = requests.get(download_url, headers=HEADERS, stream=True, timeout=30)
    
    if r.status_code != 200:
        print(f"下载失败: {r.status_code}")
        return False
    
    # 获取文件名
    content_type = r.headers.get('Content-Type', '')
    ext = '.mp4' if 'video' in content_type else '.mp4'
    
    if not output_path:
        output_path = f'douyin_video{ext}'
    
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    
    print(f"视频已保存: {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='抖音视频下载器')
    parser.add_argument('url', help='抖音分享链接')
    parser.add_argument('-o', '--output', help='输出文件路径', default=None)
    args = parser.parse_args()
    
    print(f"处理链接: {args.url}")
    
    # 获取真实URL
    real_url = get_final_url(args.url)
    print(f"真实URL: {real_url}")
    
    # 提取视频ID
    video_id = extract_video_id(real_url)
    print(f"视频ID: {video_id}")
    
    # 获取视频信息
    print("获取视频信息...")
    info = get_video_info(real_url)
    
    if info:
        print(f"标题: {info.get('title', '')}")
        print(f"作者: {info.get('author', '')}")
        print(f"点赞: {info.get('digg_count', 0)}")
        
        if 'video_url' in info:
            print("下载视频...")
            download_video(info['video_url'], args.output)
    else:
        print("获取视频信息失败，请检查链接是否有效")

if __name__ == '__main__':
    main()
