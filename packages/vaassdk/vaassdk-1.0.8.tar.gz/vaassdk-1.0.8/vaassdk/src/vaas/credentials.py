# encoding: utf-8
# set key、token、pkg_name、platform
from vaassdk.src.vaas import config


class Credentials(object):

    def __init__(self, ak, token, pkg, platform):
        config.ACCESS_KEY = ak
        config.ACCESS_TOKEN = token
        config.PKG_NAME = pkg
        config.PLATFORM = platform