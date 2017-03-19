#经浏览器抓包分析，爱词霸的每日一句有个api接口，只需更换日期即可获取对应的json字符串。解析json后对应存入mysql

import requests,datetime,json,pymysql,winsound

#从浏览器copy的headers
headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
            "Cache-Control": "max-age=0",
            "Host": "sentence.iciba.com",
            "Referer": "http//news.iciba.com/views/dailysentence/daily.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
            }

#建立一个数据库连接，我用的navicat for mysql，所以表已在可视化界面建好，这里省略建表sql语句
coon = pymysql.connect(host='127.0.0.1', user='root', password='123456',
                        port=3306, db='aiciba', charset='utf8')
#生成数据库游标
cur = coon.cursor()

#定义一个生成格式化时期的函数从开始日期到结束日期，日期格式如2015-08-01
def dateRange(beginDate,endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate,"%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates


def get_date(date,retries=3):#retries限制再次访问的次数
    url = 'http://sentence.iciba.com/index.php?&c=dailysentence&m=getdetail&title=%s'%date
    print(url)
    try:
        response = requests.get(url,headers=headers,timeout=3).content.decode('utf-8')
        jsonData = json.loads(str(response))
        content = jsonData.get("content")
        note = "".join(jsonData.get("note"))
        translation = jsonData.get("translation")

        #清洗格式化处理tags中的多项tag
        tags_temp = jsonData.get("tags")
        tags = ''
        for i in range(len(tags_temp)):
            tag = tags_temp[i].get("tagname")
            tags = tags + ' ' + tag
        for i in range(7):
            if jsonData.get('week_info')[i].get("flag")=="cur":
                week = jsonData.get('week_info')[i].get("week")
        tts = jsonData.get("tts")
        tts_size = jsonData.get("tts_size")
        love = jsonData.get("love")
        comment_count = jsonData.get("comment_count")
        #有的日期pic属性为空，用try...进行筛选
        try:
            pic = jsonData.get("picture2")
        except:
            pic = jsonData.get("picture")
        sql = "insert into aiciba(日期,英文句子,中文翻译,详解,标签,星期,tts地址,tts大小,点赞,评论数,大图地址) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        print(date,'提取数据成功')
        try:
            cur.execute(sql,
                        [date, content, note, translation, tags, week, tts, tts_size, love,comment_count, pic])
            coon.commit()
            print('插入数据库成功')
        except:
            winsound.Beep(400,600)
            print('插入数据库——失败——')
            pass
    except:
        if retries>0:
            print("再次访问")
            # time.sleep(1 + random.random())
            get_date(date,retries-1)
        else:
            #重试三次后无法获取数据就警报提醒，winsound模块使电脑扬声器发出警报
            winsound.Beep(400, 600)
            print(date,url,"无法访问！")


if __name__ == '__main__':
    #生成日期列表
    dates = dateRange('2017-01-01', '2017-3-10')
    for date in dates:
        # time.sleep(1+random.random())
        get_date(date)
