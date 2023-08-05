# encoding: utf-8
# 测试模块
from vaassdk.src.vaas.credentials import Credentials
from vaassdk.src.vaas.vaas import Vaas


def test_channel(vaas):
    print("\n ###获取频道数据### \n")
    video_type = 1  # 视频类型横屏1，竖屏2
    try:
        channels = vaas.getchannels(video_type)
    except Exception:
        raise
    else:
        print(channels)


def test_feed(vaas):
    print("\n ###获取视频信息流数据### \n")
    video_type = 1  # 视频类型横屏1，竖屏2
    channel_id = 10175  # 频道id
    load_type = 0  # 拉取类型0-上拉，1-下拉，2-首次刷新（非必传，默认0）
    size = 8  # 页大小，范围 1～8（非必传，默认8）
    try:
        feed = vaas.getfeed(video_type, channel_id, load_type, size)
    except Exception:
        raise
    else:
        print(feed)


def test_relation(vaas):
    print("\n ###获取相关视频数据### \n")
    id = 'Jy8nbGGXEJjR'  # 视频ID
    size = 20  # 页大小，范围 1～20（非必传，默认20）
    try:
        relation = vaas.getrelation(id, size)
    except Exception:
        raise
    else:
        print(relation)


def test_cpinfo(vaas):
    print("\n ###获取作者详情### \n")
    id = '28yJYbZwR65k'  # 视频ID
    video_type = 1  # 视频类型横屏1，竖屏2
    # video_type = 2
    try:
        cpInfo = vaas.getcpinfo(id, video_type)
    except Exception:
        raise
    else:
        print(cpInfo)


def test_detail(vaas):
    print("\n ###获取视频详情### \n")
    ids = 'gjwbEJZnV0MV,EjVx74kPNoyQ'  # 视频ID，多条用英文逗号隔开
    video_type = 1  # 视频类型横屏1，竖屏2
    # ids = 'eJMeOJN9B5KX,ZVjkOgN0WjGp'
    # video_type = 2
    try:
        detail = vaas.getvideos(ids, video_type)
    except Exception:
        raise
    else:
        print(detail)


def test_cpvideos(vaas):
    print("\n ###获取作者视频列表### \n")
    id = 'pbjDYWR0P52N'  # 作者ID
    video_type = 1  # 视频类型横屏1，竖屏2
    page = 1  # 页码（非必传，默认1）
    size = 20  # 页大小（非必传，默认20）
    # id = 'RJj017XJvx58'
    # video_type = 2
    try:
        cpVideos = vaas.getcpvideos(id, video_type)
    except Exception:
        raise
    else:
        print(cpVideos)


def test_play(vaas):
    print("\n ###获取播放数据### \n")
    id = 'njz3Dn7N1r5V'  # 视频ID
    try:
        plays = vaas.getplay(id)
    except Exception:
        raise
    else:
        print(plays)


if __name__ == '__main__':
    # 设置公共参数
    Credentials('ak', 'token', 'pkg', 'platform')
    # 设备唯一标识，客户端生成
    vaas = Vaas('udid')
    # 获取频道数据
    test_channel(vaas)
    # 获取视频信息流数据
    test_feed(vaas)
    # 获取相关视频数据
    test_relation(vaas)
    # 获取作者详情
    test_cpinfo(vaas)
    # 获取视频详情
    test_detail(vaas)
    # 获取作者视频列表
    test_cpvideos(vaas)
    # 获取播放数据
    test_play(vaas)
