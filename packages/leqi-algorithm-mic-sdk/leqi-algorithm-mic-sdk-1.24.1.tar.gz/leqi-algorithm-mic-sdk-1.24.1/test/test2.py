# 安装SDK pip install git+https://github.com/panyunsuo/AlgorithmicMicroserviceSDK.git
# SDK使用文档 https://www.yuque.com/fenfendeyouzhiqingnian/algorithm/ffdma4

from algorithm_mic_sdk.algorithms.topic import Topic
from algorithm_mic_sdk.auth import AuthInfo
from algorithm_mic_sdk.tools import FileInfo
from threading import Thread

#1279 1706
host = 'http://nyasu.leqi.us:17012'  # 算法host地址
user_name = 'panso'
password = '0bdca2d8-4a3d-11eb-addb-0242c0a80006'
filename = 'src/错题本/原图.png'  # 图片文件名
corners = [[0, 0], [1279, 1706], [0, 1706], [1279, 0]]
file_info = FileInfo.for_file_bytes(open(filename, 'rb').read())  # 创建文件对象
auth_info = AuthInfo(host=host, user_name=user_name, password=password, gateway_cache=False, extranet=True)  # 初始化验证信息

def run():
    topic = Topic(auth_info, file_info, corners=corners)  # 创建算法对象
    resp = topic.synchronous_request()  # 同步请求算法
    print(resp.json)  # 输出算法响应参数
    print(topic.get_file_url(resp.json['result']['result_im_oss_name']))


def batch_run():
    for i in range(2000):
        try:
            run()
        except Exception as e:
            print(e)

th = []
for i in range(20):
    t = Thread(target=batch_run)
    t.start()
    th.append(t)

for t in th:
    t.join()