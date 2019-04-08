'''
Connects to Botzone
'''
import urllib.request
import time


class Match:
    has_request = False
    has_response = False
    current_request = None
    current_response = None
    matchid = None

    def new_request(self, request):
        self.has_request = True
        self.has_response = False
        self.current_request = request


# TODO：定义一种特化的对局数据类，比如存储棋盘状态等
class SomeKindOfMatch(Match):
    def __init__(self, matchid, first_request):
        self.has_request = True
        self.current_request = first_request
        self.matchid = matchid


matches = {}


# 从 Botzone 上拉取新的对局请求
def fetch(matchClass):
    req = urllib.request.Request(
        "https://www.botzone.org.cn/api/576dea8e28a77f3c04a22ec3/qianqian/localai"
    )
    for matchid, m in matches.items():
        if m.has_response and m.has_request and m.current_response:
            print('> Response for match [%s]: %s' % (matchid,
                                                     m.current_response))
            m.has_request = False
            req.add_header("X-Match-" + matchid, m.current_response)
    while True:
        try:
            res = urllib.request.urlopen(req, timeout=None)
            botzone_input = res.read().decode()
            lines = botzone_input.split('\n')
            request_count, result_count = map(int, lines[0].split(' '))
            for i in range(0, request_count):
                # 新的 Request
                matchid = lines[i * 2 + 1]
                request = lines[i * 2 + 2]
                if matchid in matches:
                    print('Request for match [%s]: %s' % (matchid, request))
                    matches[matchid].new_request(request)
                else:
                    print('New match [%s] with first request: %s' % (matchid,
                                                                     request))
                    matches[matchid] = matchClass(matchid, request)
            for i in range(0, result_count):
                # 结束的对局结果
                matchid, slot, player_count, scores = lines[
                    request_count * 2 + 1 + i].split(' ')
                if player_count == "0":
                    print("Match [%s] aborted:\n> I'm player %s" % (matchid,
                                                                    slot))
                else:
                    print(
                        "Match [%s] finished:\n> I'm player %s, and the scores are %s"
                        % (matchid, slot, scores))
                matches.pop(matchid)
        except (urllib.error.URLError, urllib.error.HTTPError):
            # 此时可能是长时间没有新的 request 导致连接超时，再试即可
            print(
                "Error reading from Botzone or timeout, retrying 2 seconds later..."
            )
            time.sleep(2)
            continue
        break


if __name__ == '__main__':
    while True:
        fetch(SomeKindOfMatch)
        for mid, m in matches.items():
            # 使用 m.current_request 模拟一步对局状态，然后产生动作

            # 将自己的动作存入 m.current_response，同样进行一步模拟
            m.has_response = True