from collections import Counter

import jieba
from PIL import Image
from matplotlib.font_manager import FontProperties
from matplotlib.image import imread
from pymongo import MongoClient
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

client = MongoClient('localhost', 27017)
db = client.nemusic
datas = db.datas

def get_words_frequency(datas,stop_set):
    array = datas.find({"mark":{"$ne":None}})
    # print(array)
    num = 0
    words_list = []
    for doc in array:
        num+=1
        title = doc['mark']
        # print(doc['title'])
        t_list = jieba.lcut(str(title), cut_all=False)
        for word in t_list:  # 当词不在停用词集中出现,并且长度大于1小于5,将之视为课作为词频统计的词
            if word not in stop_set and 5 > len(word) > 1:
                words_list.append(word)
        words_dict = dict(Counter(words_list))

    return words_dict

def classify_frequenc(word_dict,minment=5):
    '''
    词频筛选,将词频统计中出现次数小于minment次的次剔除出去,获取更精确的词频统计
    :param word_dict:
    :param minment:
    :return:
    '''
    num = minment - 1
    dict = {k:v for k,v in word_dict.items() if v > num}
    return dict

def load_stopwords_set(stopwords_path):
    '''
    载入停词集
    :param stopwords_path: 文本存放路径
    :return:集合
    '''
    stop_set = set()
    with open(str(stopwords_path),'r',encoding='UTF-8') as fp:
        line=fp.readline()
        while line is not None and line!= "":
            # print(line.strip())
            stop_set.add(line.strip())
            line = fp.readline()
            # time.sleep(2)
    return stop_set

def get_wordcloud(dict,title,save=False):
    '''

    :param dict: 词频字典
    :param title: 标题(电影名)
    :param save: 是否保存到本地
    :return:
    '''
    # 词云设置
    mask_color_path = "img\img_11.jpg" # 设置背景图片路径

    # print(mask_color_path)
    font_path = 'C:\Windows\Fonts\STXINWEI.TTF'  # 为matplotlib设置中文字体路径;各操作系统字体路径不同,以mac ox为例:'/Library/Fonts/华文黑体.ttf'
    imgname1 = "img\color_by_defualut.png"  # 保存的图片名字1(只按照背景图片形状)
    imgname2 = "img\color_by_img.png"  # 保存的图片名字2(颜色按照背景图片颜色布局生成)
    width = 1000
    height = 860
    margin = 2
    # 设置背景图片
    mask_coloring = imread(mask_color_path)
    # 设置WordCloud属性
    wc = WordCloud(font_path=font_path,  # 设置字体
                   background_color="white",  # 背景颜色
                   max_words=150,  # 词云显示的最大词数
                   mask=mask_coloring,  # 设置背景图片
                   max_font_size=200,  # 字体最大值
                   random_state=42,
                   width=width, height=height, margin=margin,  # 设置图片默认的大小,但是如果使用背景图片的话,那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                   )
    # 生成词云
    wc.generate_from_frequencies(dict)

    bg_color = ImageColorGenerator(mask_coloring)
    # 重定义字体颜色
    wc.recolor(color_func=bg_color)
    # 定义自定义字体，文件名从1.b查看系统中文字体中来
    myfont = FontProperties(fname=font_path)
    plt.figure()
    plt.title(title, fontproperties=myfont)
    plt.imshow(wc)
    plt.axis("off")
    plt.show()

    if save is True:#保存到
        wc.to_file(imgname2)

stopwords_path = 'stopwords.txt'
# print(stopwords_path)
stop_set = load_stopwords_set(stopwords_path)
# print(stop_set)
#从数据库获取评论 并分好词
frequency_dict = get_words_frequency(datas,stop_set)
# 对词频进一步筛选
cl_dict = classify_frequenc(frequency_dict,5)
print(frequency_dict)
# 根据词频 生成词云
get_wordcloud(cl_dict,"网易云音乐视频词频统计")