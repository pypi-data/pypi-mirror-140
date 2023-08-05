# encoding: utf-8

# 联系一览获取access_key、access_token
ACCESS_KEY = ''  # 一览提供的渠道ak
ACCESS_TOKEN = ''  # 一览提供的渠道token
PKG_NAME = ''  # 应用包名
PLATFORM = 1  # 接入方式

# 请求url
FEED = '/video/feed'  # feed流
CHANNELS = '/video/channels'  # 频道
RELATION = '/video/relation'  # 频道相关
DETAIL = '/video/getvideos'  # 视频详情
CPINFO = '/video/cpinfo'  # 作者详情
CPVIDOES = '/video/cpvideos'  # 作者视频
PLAY = '/vaas/video/play'  # 播放

# 以下常量不需要修改
HOST_PROD = 'http://api.yilanvaas.cn'  # 线上正式域名(播放接口除外)
HOST_PROD_PLAY = 'http://play.yilanvaas.cn'  # 线上正式域名(播放接口)
HOST_DATA = 'http://data.1lan.tv/log?ts=%d&access_key=%s&udid=%s&m=%s'  # 上报相关域名
DATA_BEGION = '13149876'
DATA_END = '98761314'
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 10
DEFAULT_MAX_RETRY_TIMES = 2