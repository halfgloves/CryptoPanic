import json, requests, bs4, time
from urllib.parse import urlencode
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import urllib.request
import urllib.parse
import random, hashlib, itchat
from threading import Timer


def translate(text):

    salt =  random.randint(32768, 65536)
    secretKey = 'SEoo2jv2qbyG227BBRqj'
    appid = '20181001000214831'
    temp = appid+text+str(salt)+secretKey
    sign = hashlib.md5()
    sign.update(temp.encode(encoding='utf-8'))

    params = {
        'q':str(text),
        'from':'en',
        'to':'zh',
        'appid':appid,
        'salt':salt,
        'sign':sign.hexdigest()
    }
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate?' + urlencode(params)
    response = requests.get(url)
    translate_json = response.json()
    return translate_json.get('trans_result')[0].get('dst')

def get_news():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)
    wait = WebDriverWait(browser, 300)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    params = {
            'auth_token':'f2a2abfbc10960f9edafe488471a0d9c91f8b223',
            'public': 'true'
            #'regions': 'en'
        }
    url = 'https://cryptopanic.com/api/posts/?' + urlencode(params)
    #print(url)

    response = requests.get(url, headers=headers)
    web_json = response.json()
    #print(len(webjson.get('results')))
    webjson = ''
    if web_json.get('results')[0].get('kind') == 'news':
        webjson = web_json.get('results')[0]
    else:
        return None
    #print(webjson)
    cryptos = []
    if webjson.get('currencies') is not None:
        for i in webjson.get('currencies'):
            cryptos.append(i.get('code'))
    else:
        pass
        #print(news.get('content_url'))
    crypto = ''
    for i in cryptos:
        crypto = crypto + i + ' '
    #crypto.strip()
    start = time.time()
    browser.get(webjson.get('url'))
    #time.sleep(60)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'description-body')))
    end = time.time()
    #print(round(end - start, 2))
    html = browser.page_source
    doc = bs4.BeautifulSoup(html, 'lxml')
    real_url = doc.find('h1', {'class':'post-title'})
    #print(real_url)
    real_url = bs4.BeautifulSoup(str(real_url), 'lxml')
    publish_time = real_url.find('time')['datetime']
    real_url = real_url.findAll('a')[1]['href']
        #print(real_url)
    content = doc.find('div', {'class':'description-body'})
    #print(content)
    content = bs4.BeautifulSoup(str(content), 'lxml')
    content = content.find('p').get_text()
    content_zh = translate(content)
    news = {
        'title':webjson.get('title'),
        'title_zh':translate(webjson.get('title')),
        'publish_time':publish_time,
        'id':webjson.get('id'),
        'real_url':real_url,
        'crypto':crypto,
        'content':content,
        'content_zh':content_zh
    }
    return news

#print(get_news())
def send_news():
    text = get_news()

    info = itchat.get_chatrooms(update=True)
    news = text.get('title') + ' (' + str(text.get('crypto')).strip() +')\n' + text.get('publish_time') + '\n' + text.get('content') + '\n原文链接:' + text.get('real_url') + '\n以下为百度翻译：\n' + text.get('title_zh') + '\n' + text.get('content_zh')
    itchat.get_chatrooms()
    # 查找特定群聊
    time.sleep(10)
    # 通过群聊名查找
    #chat_rooms = itchat.search_chatrooms(name='英特智投 第一期（看公告）')
    chat_rooms = itchat.search_chatrooms(name='币小龙自媒体研究室')
    if len(chat_rooms) > 0:
        itchat.send_msg(news, chat_rooms[0]['UserName'])
'''
def loop_send():
    global count
    itchat.send('防掉线发送', toUserName='fi')
    count += 1
    if count < 10000:
    Timer(1800, loop_send).start()
'''
if __name__ == '__main__':
    #itchat.auto_login(enableCmdQR = 1, hotReload=True)
    itchat.auto_login(hotReload=True)
    #itchat.run()
    send_news()





#itchat.send(news, toUserName='Intelligent Investor')
# 'UserName': '@@81b150c459b573ab4e9f74b9d910f021c39203bef28aeaf5b1d1377b49ba07ef', 'NickName': 'IIHQ app dev'
# 'UserName': '@@c862df8465270dc91277743a5088704bd7fb38d2ba2da7ae888abafe32a22824', 'NickName': '英特智投 第一期（看公告）'