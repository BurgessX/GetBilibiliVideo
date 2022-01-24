"""
爬取B站视频
2022/01/06
"""
# https://www.bilibili.com/video/BV1ZR4y1s7jU

# 思路
# 1. 用 requests 爬取视频页 HTML
# 2. 用 re 解析 HTML，获取其中的 video 和 audio 中的 baseurl
# 3. 用 requests 下载视频和音频
# 4. 合并视频和音频

# 注：
# 1. 为了减少调试时的访问次数，采用文件保存的方案保存每一步获取的数据
# 2. 直接用浏览器访问 baseurl 会返回 403，无法获取音频和视频，可能是因为请求头中没有 referer

import requests
import os
import re

def get_html(bvid):
    """获取视频页HTML"""
    url = f'https://www.bilibili.com/video/{bvid}'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    }
    html_path = f'{bvid}.html'
    try:
        with requests.get(url, headers=headers) as res:
            with open(html_path, 'wb') as f:
                f.write(res.content)
        print('HTML保存成功')
        return html_path
    except Exception as e:
        print(e)
        return None


def get_video_and_audio_urls(html_path):
    """获取视频和音频URL"""
    if not os.path.exists(html_path):
        print(f'{html_path}不存在')
        return None

    with open(html_path, 'r', encoding='utf-8') as f:
        file_string = f.read()
        video_match = re.search(r'"video":.*?"baseUrl":"(.*?)",', file_string)
        audio_match = re.search(r'"audio":.*?"baseUrl":"(.*?)",', file_string)
        video_url = video_match.group(1)
        audio_url = audio_match.group(1)

    if video_url and audio_url:
        return (video_url, audio_url)
    else:
        return None


def get_video_and_audio(video_url, audio_url, video_path, audio_path):
    """下载视频"""
    headers = {
        'referer': 'https://www.bilibili.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
    }
    try:
        with open(video_path, 'wb') as f:
            with requests.get(video_url, headers=headers) as res:
                f.write(res.content)
        print(video_path, '下载完毕')
        with open(audio_path, 'wb') as f:
            with requests.get(audio_url, headers=headers) as res:
                f.write(res.content)
        print(audio_path, '下载完毕')
        return (video_path, audio_path)
    except Exception as e:
        print(e)
        return None


def combine_video_and_audio(video_path, audio_path, output_path):
    """将音频和视频合成为有声视频"""
    if os.path.exists(video_path) and os.path.exists(audio_path):
        try:
            # 注意：需要安装ffmpeg并配置环境变量
            stat = os.system(f'ffmpeg.exe -i {video_path} -i {audio_path} -acodec copy -vcodec copy {output_path}')
            if stat:
                print(output_path, '合成失败')
            else:
                print(output_path, '合成成功')
        except Exception as e:
            print(e)
            print(output_path, '合成失败')
    else:
        print('音频或视频不存在，无法合成')



def main():
    bvid = 'BV1ZR4y1s7jU'
    html_path = f'{bvid}.html'
    video_path = f'{bvid}.mp4'
    audio_path = f'{bvid}.mp3'
    video_with_audio_path = f'{bvid}_.mp4'  # 合并后的视频

    # 获取HTML
    if not os.path.exists(html_path):
        get_html(bvid)

    # 获取音视频URL
    video_url, audio_url = get_video_and_audio_urls(html_path)
    print('video_url:', video_url)
    print('audio_url:', audio_url)

    # 下载音视频
    if not (os.path.exists(video_path) and os.path.exists(audio_path)):
        get_video_and_audio(video_url, audio_url, video_path, audio_path)

    # 合并音视频
    if not os.path.exists(video_with_audio_path):
        combine_video_and_audio(video_path, audio_path, video_with_audio_path)



if __name__ == "__main__":
    main()
