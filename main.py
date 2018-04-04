import requests
import re
import queue
import threading

from pymongo import MongoClient

q= queue.Queue()

def crawl():
    while True:
        if(q.empty()):
            pass;
        else:
            p = q.get()
            get_data(p.get("id"),p.get("time"))

base = u'http://music.163.com/m/video?id='
# start_id = '54B09D4407A49227ABC5659D1E92D4FD'
start_id = '891E466834691C3BD645987B80F1FE15'
start_url = base  + start_id
useragent = "JUC (Linux; U; 2.3.7; zh-cn; MB200; 900*500) UCWEB7.9.3.103/139/999"
headers={'User-Agent':useragent}

f=open(r'test.txt','r')#打开所保存的cookies内容文件
cookies={}#初始化cookies字典变量
for line in f.read().split(';'):   #按照字符：进行划分读取
    #其设置为1就会把字符串拆分成2份
    name,value=line.strip().split('=',1)
    cookies[name]=value  #为字典cookies添加内容


client = MongoClient('localhost', 27017)
db = client.nemusic
datas = db.datas

def get_data(id,time=0):
    count = datas.find({"_id": id}).count()
    print(count)
    if count != 0:
        return
    html = requests.get(base + id,headers=headers,cookies=cookies)
    html.encoding = 'utf-8'

    # print(html.text)

    reg = re.compile(u'-thide"><a href="\/video\?id=(.*?)" data-log-action=')
    # a = reg.findall(html.text)
    if (len(reg.findall(html.text)) == 0):
        a = None
    else:
        a = reg.findall(html.text)

    reg = re.compile(u'playTime&quot;:(.*?),&quot;praisedCount')
    if (len(reg.findall(html.text)) == 0):
        watch = None
    else:
        watch = reg.findall(html.text)[0]

    reg = re.compile(u'<p class="intr" id="id_video_content_desc">(.*?)</p>')
    if(len(reg.findall(html.text)) == 0):
        title = None
    else:
        title = reg.findall(html.text)[0]

    reg = re.compile(u'"s-fc4">(.*?)</p>')
    # times = reg.findall(html.text)
    if (len(reg.findall(html.text)) == 0):
        times = None
    else:
        times = reg.findall(html.text)


    reg = re.compile(u'&quot;name&quot;:&quot;(.*?)&quot;')
    # mark = reg.findall(html.text)
    if (len(reg.findall(html.text)) == 0):
        mark = None
    else:
        mark = reg.findall(html.text)



    data = {
        '_id': id,
        'watch': watch,
        'title': title,
        'mark': mark,
        'time': time
    }


    # 插入数据库
    # count = datas.find({"_id": data["_id"]}).count()
    # if count == 0:
    #     datas.insert_one(data)
    #     print(data)
    # 数据库的写入
    datas.update({'title': data['title']}, {'$setOnInsert': data}, upsert=True)
    print(data)

    if a == None:
        pass
    else:
        alen = len(a)
        for i in range(alen):
            d = {
                'id': a[i],
                'time': times[i+2]
            }
            q.put(d)


threading.Thread(target=crawl).start()

start_data = {
    'id': start_id,
    'time': 0
}

q.put(start_data)







