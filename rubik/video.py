# 导出 MP4 视频文件
# Source: https://stackoverflow.com/questions/52414148/turn-pil-images-into-video-on-linux
# Requires: ffmpeg

import cv2
import numpy as np
import os
from IPython.display import HTML
from base64 import b64encode

def imgs_to_video(imgs, video_name='video.mp4', fps=15):
    """调用 cv2 的 VideoWriter 工具"""
    
    video_dims = (imgs[0].width, imgs[0].height)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')    
    video = cv2.VideoWriter(video_name, fourcc, fps, video_dims)
    for img in imgs:
        tmp_img = img.copy()
        video.write(cv2.cvtColor(np.array(tmp_img), cv2.COLOR_RGB2BGR))
    video.release()
    return 

def display_video(file_path, compressed_vid_path=None, width=512):
    """用 IPython.display 的 HTML 来显示视频"""
    if compressed_vid_path is None:
        compressed_vid_path = file_path.replace('.mp4', '_compressed.mp4')
    # Compress the video
    if os.path.exists(compressed_vid_path):
        os.remove(compressed_vid_path)
    os.system(f'ffmpeg -i {file_path} -vcodec libx264 {compressed_vid_path} 2> /dev/null')

    mp4 = open(compressed_vid_path, 'rb').read()
    data_url = 'data:simul2/mp4;base64,' + b64encode(mp4).decode()
    return HTML("""
        <video width={} controls>
              <source src="{}" type="video/mp4">
        </video>
        """.format(width, data_url))