# report info service
import json
import time
from vaassdk.src.vaas import tools
from vaassdk.src.vaas import config


class Report():
    def __init__(self, udid):
        self.tool = tools.Tools(udid)
        self.url = config.HOST_DATA

    # 视频曝光上报
    def videoshow(self, videoid, referpage, pos):
        body = '{"videoid": "%s", "referpage": "%s", "pos": "%d"}' % (videoid, referpage, pos)
        input = {'event': 'videoshow', 'body': json.loads(body)}
        self.tool.set_input(input)
        ret = self.tool.request_report(self.url)
        return ret

    # 点击播放上报
    def videoplay(self, videoid, referpage):
        body = '{"videoid": "%s", "referpage": "%s", "taskid": "%d"}' % (
        videoid, referpage, int(round(time.time() * 1000)))
        input = {'event': 'videoplay', 'body': json.loads(body)}
        self.tool.set_input(input)
        ret = self.tool.request_report(self.url)
        return ret

    # 播放时长上报
    def videoplaytm(self, videoid, bt, et, rt):
        body = '{"videoid": "%s", "taskid": "%s", "bt": "%d", "et": "%d", "rt": "%d"}' % (
            videoid, int(round(time.time() * 1000)), bt, et, rt)
        input = {'event': 'videoplaytm', 'body': json.loads(body)}
        self.tool.set_input(input)
        ret = self.tool.request_report(self.url)
        return ret

    # 视频反馈上报
    def videofeedback(self, videoid, cpid, action):
        body = '{"videoid": "%s", "cpid": "%s", "action": "%s"}' % (videoid, cpid, action)
        input = {'event': 'videofeedback', 'body': json.loads(body)}
        self.tool.set_input(input)
        ret = self.tool.request_report(self.url)
        return ret
