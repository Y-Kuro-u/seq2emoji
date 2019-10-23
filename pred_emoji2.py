import re
import json
import numpy as np
from googletrans import Translator

def make_data():
    text_path = "./top10_text.txt"
    emoji_path = "./top10_emoji.txt"

    data_dic = []
    emoji_dic = {}
    emoji_list = []
    data = []

    #文章,絵文字をlistに収納
    for i in open(text_path):
        if i == "\n":
            continue
        data_dic.append(i)

    for i in open(emoji_path):
        if i == "\n":
            continue
        i = i.replace("\n","")
        emoji_list.append(i[-1])
    
    #print(len(data_dic),len(emoji_list))
    cn =  0
    for i,j in zip(data_dic,emoji_list):
        data.append([i,j])
        cn += 1

    #print(data[0:10])
    data_dic_ = []
    for i in data:
        i[0] = i[0].replace("\n","")
        i[0] = re.sub(r"[™-🧀]","",i[0])
        data_dic_.append(i)
    
    #絵文字のタグ付け
    tag_count = 0
    for i in data_dic_:
        if i[1] not in emoji_dic:
            emoji_dic[i[1]] = int(tag_count)
            tag_count += 1

    #print(emoji_dic)
    tc = [0] * 10
    for i,j in enumerate(data_dic_):
        data_dic_[i][1] = emoji.index(j[1])
    
    for i in data_dic_:
        tc[i[1]] += 1

    #print(tc)
    tc_ = [0]*10
    tc__ = [0]*10

    rt_data=[]
    rt_test_data = []

    for i in data_dic_:
        if tc_[i[1]] < 3997:
            rt_data.append(i)
            tc_[i[1]] += 1
        else:
            rt_test_data.append(i)
            tc__[i[1]] += 1

    return rt_data,rt_test_data

def sentence2words(sentence):
    stopwords = [i for i in open("./stopwords.txt")]
    for i in range(len(stopwords)):
        stopwords[i] = stopwords[i].replace("\n","")
    sentence = sentence.lower() # 小文字化
    sentence = sentence.replace("\n", "") # 改行削除
    sentence = re.sub(re.compile(r"[!-\/:-@[-`{-~]"), " ", sentence) # 記号をスペースに置き換え
    sentence = sentence.split(" ") # スペースで区切る
    sentence_words = []
    for word in sentence:
        if (re.compile(r"^.*[0-9]+.*$").fullmatch(word) is not None): # 数字が含まれるものは除外
            continue
        if word in stopwords: # ストップワードに含まれるものは除外
            continue
        sentence_words.append(word)        
    return sentence_words

def make_words_dir(x):
    words_dic = {}
    for i in x:
        words = [j for j in sentence2words(i) if j]
        for k in words:
            if k not in words_dic:
                words_dic[k] = len(words_dic)
    return words_dic

def split_data(x):
    data_text = []
    data_tag = []
    for i in data:
        data_text.append(i[0])
        data_tag.append(i[1])
    return data_text,data_tag

def training_probability(data_text,data_tag):
    word_probability = [[0] * 10 for i in range(len(words_dic))]
    for i,j in zip(data_text,data_tag):
        words = [j for j in sentence2words(i) if j]
        for k in words:
            word_id = words_dic[k]
            word_probability[int(word_id)][int(j)] += 1
    return word_probability

def predict_emoji(seq):
    words = [j for j in sentence2words(seq) if j]
    pred_emoji = [0]*10
    for i in words:
        if i not in words_dic:
            continue
        ids = words_dic[i]
        lis_prob = soft_max_word_prob[ids]
        for j,k in enumerate(lis_prob):
            pred_emoji[j] += k
        #print(pred_emoji)
    emoji_index =pred_emoji.index(max(pred_emoji))

    return emoji[emoji_index]

def load_dict():
    with open("./word_dic.json","r") as wd:
        words_dic = json.load(wd)
    return words_dic

def soft_max_func(x):
    max_fac = np.max(x)
    exp_ = np.exp(x-max_fac)
    sum_exp = np.sum(exp_)
    y = exp_/sum_exp
    return y

emoji = ['😭','😒','🙃','😊','😔','😩','😂','😍','🙄','🤔']

#data,test_data = make_data()
#text_data,tag_data = split_data(data)
#test_text_data,test_tag_data = split_data(test_data)
words_dic = load_dict()

"""
学習用

words_dic = make_words_dir(text_data)
word_probability = training_probability(text_data,tag_data)
word_probability = np.array(word_probability)
np.save("word_probability",word_probability)
"""

#学習済データの読み込み
word_probability = np.load("./word_probability.npy")
soft_max_word_prob = []

for i in word_probability:
    smf = soft_max_func(i)
    soft_max_word_prob.append(smf)

print("please input \"exit\" if you finish")
while 1:
    seq = input()
    translator = Translator()
    trans = translator.translate(seq,dest="en")
    if trans.src == "ja":
        print(predict_emoji(trans.text))
        print("------------------------------------------")
        continue
    if seq == "exit":
        print("Bye!")
        break
    print(predict_emoji(seq))
    print("------------------------------------------")
