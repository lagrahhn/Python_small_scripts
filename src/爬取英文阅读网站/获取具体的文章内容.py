import time
import requests
from bs4 import BeautifulSoup
import pymysql
from tqdm import tqdm
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header


prefix = "https://www.enread.com"

def close_window():
    os.system("shutdown -s -t 0")

# 数据库连接配置
db_config = {
    'host': '服务器地址',
    'user': '用户名',
    'password': '密码',
    'db': '数据库名',
    'port': 3306,
    'charset': 'utf8'
}


def create_connection():
    return pymysql.connect(**db_config)


def spider(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find(id="dede_content").text
    return content.replace("\r", "").replace("\n", "").replace("\t", "").replace("'","\\'")
     
def send_qq_mail():
    # 发件人和收件人
    sender = '发件人地址@qq.com'
    receiver = '收件人地址@qq.com'

    # 邮件内容
    subject = '爬虫程序运行完毕'
    body = '这是一封测试邮件，发送自Python程序。'

    # SMTP服务器（这里是QQ邮箱的SMTP服务器）
    smtp_server = 'smtp.qq.com'

    # 发件人邮箱的SMTP授权码
    password = '请自行获取授权码'

    # 创建一个MIMEText对象（还有其他类型，例如可以附带附件等）
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header(subject, 'utf-8')

    try:
        # 创建SMTP对象
        server = smtplib.SMTP_SSL(smtp_server, 465) # QQ邮箱的SSL端口是465
        # server.set_debuglevel(1) # 可以开启调试模式，会打印与SMTP服务器的交互信息

        # 登录SMTP服务器
        server.login(sender, password)

        # 发送邮件
        server.sendmail(sender, [receiver], message.as_string())

        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("邮件发送失败", e)
    finally:
        # 关闭与SMTP服务器的连接
        server.quit()   
    
try:
    # ! 开始时间
    starttime = time.time()
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("select detail_url from newspaper where content is null")
    urls = cursor.fetchall()
    count = 0
    for url in tqdm(urls):
        target_url = prefix + url[0]
        try:
            content = spider(target_url)
            sql = f"update newspaper set content = '{content}' where detail_url = '{url[0]}'"
            # print(sql)
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)
        count += 1
        if(count % 20 == 0):
            time.sleep(2)
        if(count % 200 == 0):
            time.sleep(5)



    # ! 结束时间
    endtime = time.time()
    # ! 程序运行时间
    waste_time = endtime - starttime
    print(f"程序耗时:{waste_time}秒")
    # 耗时大概
    cursor.close()
    conn.close()
    send_qq_mail() # ! 完成爬虫后向邮箱发送消息，告知完成爬虫程序
finally:
    print("finish")
    # ! 注意，下面的是执行完爬虫后关机的命令，请谨慎使用
    # close_window()