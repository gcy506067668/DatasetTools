import requests
from urllib import request
from bs4 import BeautifulSoup
from uuid import uuid4
import pymysql
import time
uuidChars = ("a", "b", "c", "d", "e", "f",
       "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
       "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
       "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
       "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
       "W", "X", "Y", "Z")
conn=pymysql.connect(host='localhost',user='root',passwd='123456',db='bookshop',port=3306,charset='utf8')
cursor = conn.cursor()

def short_uuid():
  uuid = str(uuid4()).replace('-', '')
  result = ''
  for i in range(0,8):
    sub = uuid[i * 4: i * 4 + 4]
    x = int(sub,16)
    result += uuidChars[x % 0x3E]
  return result

def gethtmltext(url):
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3650.400 QQBrowser/10.4.3341.400'
    #req = requests.Request(url, headers = head)
    req = requests.get(url, headers=head)
    req.encoding = 'gb2312'
    soup = BeautifulSoup(req.text, "html5lib")
    return soup


url = 'http://www.bookschina.com/kinder/11000000_0_0_11_0_1_2_0_0/'
soup_all = gethtmltext(url)
soup_texts = soup_all.find('div',class_='bookList')
soup_texts = soup_texts.find_all('div',class_='cover')
soup_texts_url = {}
for soup_text in soup_texts:
    soup_texts_url = soup_text.find_all('a')
    download_url = 'http://www.bookschina.com'+soup_texts_url[0].get('href')
    print(download_url)
    b_id = short_uuid()
    soup = gethtmltext(download_url)
    #封面图片
    cover = soup.find('div',class_='coverImg')
    img = cover.img.attrs['src']
    request.urlretrieve(img, '%s.jpg' % b_id)
    picture_path = 'C:\\Users\\lenovo\\Desktop\\'+b_id+str('.jpg')
    soup_texts = soup.find('div',class_='bookInfo')
    #标题
    if soup_texts !=None:
        title = soup_texts.h1.string
        print(title)
    #介绍
        if soup_texts.p!=None:
            book_intro = soup_texts.p.string
        else:
            book_intro = None
    #作者
    soup_athour = soup.find('div',class_='author')
    if soup_athour !=None:
        author = soup_athour.a.string
        author = author.replace('著','')
    #出版社
    soup_publish = soup.find('div',class_='publisher')
    if soup_publish !=None:
        publishment = soup_publish.a.string
    #出版日期
        publish_time = soup_publish.i.string
        if publish_time == '暂无':
            publish_time=None
    #评分
    soup_score = soup.find('div',class_='startWrap')
    if soup_score.em !=None:
        score = soup_score.em.string
    else:
        score = None
    #价格
    soup_price = soup.find('del',class_='price')
    if soup_price!=None:
        price = soup_price.string
    copyright_infors = soup.find('div',class_='copyrightInfor')
    if copyright_infors!=None:
        copyright_infor = copyright_infors.find_all('li')
        #ISBN号
        isbn=copyright_infor[0].string
        isbn=isbn.replace('ISBN：','')
        #条形码
        bar_code=copyright_infor[1].string
        bar_code=bar_code.replace('条形码：','')
        #装帧
        binding = copyright_infor[2].string
        binding=binding.replace('装帧：','')
        #版次
        edition = copyright_infor[3].string
        edition=edition.replace('版次：','')
        edition=edition.replace('第','')
        edition=edition.replace('版','')
        if edition=='暂无':
            edition=None
        #印刷次数
        print_num = copyright_infor[6].string
        print_num=print_num.replace('印刷次数：','')
        if print_num=='暂无':
            print_num=None
    #类别
    kind = copyright_infors.find('div',class_='crumsItem')
    if kind!=None:
        category = kind.a.string
    #图书特色
    specialty = soup.find('div',class_='specialist')
    if specialty !=None:
        specialty = specialty.find('p')
        specialty = str(specialty).replace('<p>','')
        specialty = specialty.replace('<br/>','')
        specialty = specialty.replace('</p>','')
    #图书简介
    b_abstract = soup.find('div',class_='brief')
    if b_abstract != None:
        b_abstract = b_abstract.find('p')
        b_abstract = str(b_abstract).replace('<p>','')
        b_abstract = b_abstract.replace('<br/>','')
        b_abstract = b_abstract.replace('</p>','')
    
    #作者简介
    a_abstracts = soup.find_all('div',class_='excerpt')
    a_abstract = None
    for a_abstract in a_abstracts:
        if a_abstract != None:
            if a_abstract.attrs['id']=='zuozhejianjie':   
                a_abstract = a_abstract.find('p')
                a_abstract = str(a_abstract).replace('<p>','')
                a_abstract = a_abstract.replace('<br/>','')
                a_abstract = a_abstract.replace('</p>','')
        else:
            a_abstract=None

    sql = '''insert into book(b_id,b_name,b_picture,author,publish_press,
                                publish_time,isbn_num,bar_code,b_binding,edition,
                                print_num,price,total_rating,b_intro,b_specialty,b_abstract,a_abstract,b_category) 
                                values
                          (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
 
    cursor.execute(sql,(b_id,title,picture_path,author,publishment,publish_time,isbn,bar_code,binding,edition,print_num,price,score,book_intro,specialty,b_abstract,a_abstract,category))   
    conn.commit()
    #图书评论
    reviews = soup.find_all('div',class_='listLeft')

    sql1 =  '''insert into review (b_id,u_id,b_review_time,b_review) values
                          (%s,%s,%s,%s)'''
                     
    for review_all in reviews:
        u_id = short_uuid()
        review = review_all.p.string
        review_time = review_all.span.string
        cursor.execute(sql1,(b_id,u_id,review_time,review))
        conn.commit()
    time.sleep(15)