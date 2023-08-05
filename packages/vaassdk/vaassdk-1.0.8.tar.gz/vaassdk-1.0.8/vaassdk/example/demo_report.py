# encoding: utf-8
import sys
# 测试模块
from vaassdk.src.vaas.report import Report
from vaassdk.src.vaas.credentials import Credentials


def test_videoshow(report):
    print("\n ###视频曝光上报### \n")
    videoid = 'gjwbEJZnV0MV'  # 视频ID
    referpage = 'channel_100'  # 展现来源，channel_xxx-feed页，vplaypage-相关页
    pos = 1  # 视频在信息流或者相关页出现的位置，从1开始计算
    try:
        ret = report.videoshow(videoid, referpage, pos)
    except Exception:
        raise
    else:
        print(ret)


def test_videoplay(report):
    print("\n ###点击播放上报### \n")
    videoid = 'gjwbEJZnV0MV'  # 视频ID
    referpage = 'channel_100'  # 展现来源，channel_xxx-feed页，vplaypage-相关页
    try:
        ret = report.videoplay(videoid, referpage)
    except Exception:
        raise
    else:
        print(ret)


def test_videoplaytm(report):
    print("\n ###播放时长上报### \n")
    videoid = 'gjwbEJZnV0MV'  # 视频ID
    bt = 1622527513  # 播放开始时间点，单位：秒
    et = 1622527523  # 播放结束时间点，单位：秒
    rt = 0  # 上报原因 0-正常结束 1-提前停止播放
    try:
        ret = report.videoplaytm(videoid, bt, et, rt)
    except Exception:
        raise
    else:
        print(ret)


def test_videofeedback(report):
    print("\n ###视频反馈上报### \n")
    videoid = 'gjwbEJZnV0MV'  # 视频ID
    cpid = 'nJ5vdO8kr8MV'  # 作者ID
    action = 'like'  # 反馈动作：like喜欢，dislike取消喜欢，follow关注
    try:
        ret = report.videofeedback(videoid, cpid, action)
    except Exception:
        raise
    else:
        print(ret)


if __name__ == '__main__':
    # 设置公共参数
    Credentials('ak', 'token', 'pkg', 'platform')
    # 设备唯一标识，客户端生成
    report = Report('udid')
    # 视频曝光上报
    test_videoshow(report)
    # 点击播放上报
    test_videoplay(report)
    # 播放时长上报
    test_videoplaytm(report)
    # 视频反馈上报
    test_videofeedback(report)
