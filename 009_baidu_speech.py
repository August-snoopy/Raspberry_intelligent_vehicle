# 测试百度的语音合成
# 定义百度接口的ip和密钥
from speech import AipSpeech
import pygame
import time

ID = '107260788'
api_key = 'dGmEnsUOZAWxi5ImguHAqwc9'
secret_key = 'nohkdj5oVEB8nJfQqohW6mTlZZpBWdtn'
text1 = '说道：“小心！胡栖豪不可直接触碰！哪怕你炼化了此人，也会被无穷无尽的后悔之情淹没！我已为你准备手段，你只需要……”“没有这个必要”李佩益脸色淡然，一把抓住，顷刻炼化！全场惊愕，“李佩益！你到底干了什么？！没有栖豪大人！我们要如何抗衡双尊？”姜皓晨跺脚，瞪着李佩益。李佩益谈笑一声“很简单，我成尊不就是了”帽檐遮住了面部，众人只听他忽吟道：“早岁已知世事艰，仍化星光荡云间。一路开拓身如絮，命海沉浮我独行。万众一心实为儡，几度轮回铸一剑。今朝损毁胡栖豪，破梦救人，再斩天！”'
baidu_speech = AipSpeech(ID, api_key, secret_key)   # 初始化AipSpeech对象
res = baidu_speech.synthesis(text = text1, options =  {'spd':5, 'vol':9 , 'per':1})  # 调用语音合成接口
if not isinstance(res, dict):  # 判断返回结果是否为字典
    with open('1.mp3', 'wb') as f:  # 将返回结果写入文件
        f.write(res)
else:
    print(res)


# pygame.mixer.init()  # 初始化pygame 
# track = pygame.mixer.music.load('boot1.mp3')  # 加载音频文件
# pygame.mixer.music.play()  # 播放音频文件
# time.sleep(20)  # 播放音频文件10秒
