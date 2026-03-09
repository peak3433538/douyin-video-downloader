# Douyin Video Downloader

抖音视频下载工具。从抖音分享链接获取视频并下载。

## 功能
- 从抖音分享链接提取视频
- 自动解析JSON数据获取视频地址
- 模拟iPhone User-Agent绕过反爬虫

## 使用方法

```bash
# 下载视频
douyin https://v.douyin.com/xxxxx

# 或使用Python脚本
python3 /path/to/douyin_download.py "抖音链接"
```

## 依赖
- requests
- BeautifulSoup4 (可选)

## 核心流程
1. 获取抖音分享链接的HTML页面
2. 从HTML中解析视频JSON数据
3. 提取video.play_addr.url_list中的播放地址
4. 使用iPhone User-Agent下载视频

## 技术要点
- 抖音有反爬虫机制，需伪装成手机浏览器
- 视频URL在HTML的JavaScript里，需解析JSON
- 推荐User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1
