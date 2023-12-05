import time
import requests
from bs4 import BeautifulSoup
from queue import Queue
import threading
import pymysql

# ! 待爬虫的地址
urls = [
    "https://www.enread.com/news/business/",
    "https://www.enread.com/news/politics/",
    "https://www.enread.com/news/life/",
    "https://www.enread.com/news/cultureandedu/",
    "https://www.enread.com/news/sciandtech/",
    "https://www.enread.com/news/sports/"
]

# 数据库连接配置
db_config = {
    'host': '服务器地址',
    'user': '用户名',
    'password': '密码',
    'db': '数据库名称',
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

    titles = soup.find_all("div", class_="title")[:-2] # ! 过滤掉最后两个无效数据
    detail_urls = soup.find_all("a", class_="title")
    release_times = soup.find_all("div", class_="description")
    times = [
        release_time.find("p")
        .find("span")
        .text.replace("\xa0", "")
        .replace("日期：", "")
        for release_time in release_times
    ]
    lists = [
        titles[i]
        .text.replace("'", "\\'")
        .replace("\n", "")
        .replace("\t", "")
        .replace("\r", "")
        .strip()
        for i in range(len(titles))
    ]
    conn = create_connection()
    cursor = conn.cursor()
    if(len(titles)==len(detail_urls)==len(times)):
        for i in range(len(titles)):
            sql = f"insert into newspaper(title,detail_url,release_time) values('{lists[i]}','{detail_urls[i].get('href')}','{times[i]}')"
            try:
                cursor.execute(sql)
                conn.commit()
            except:
                print(sql)
        cursor.close()
        conn.close()
        
def get_total_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    total_pages = soup.find("span", class_="pageinfo").find_all("strong")[0].text
    return total_pages
    
def worker(task_queue):
    while True:
        url = task_queue.get()  # 从队列中获取任务
        if url is None:
            break  # 如果获取到的是None，代表任务结束
        try:
            spider(url)
            # 这里可以添加解析网页和处理数据的代码
        except requests.exceptions.RequestException as e:
            print("解析错误")
        finally:
            task_queue.task_done()  # 完成一个任务
    
urls_to_crawl = []

# ! 开始时间
starttime = time.time()

for url in urls:
    pages = get_total_page(url)
    for i in range(int(pages)):
        urls_to_crawl.append(url+"list_{}.html".format(i+1))

# 创建队列并添加任务
task_queue = Queue()
for url in urls_to_crawl:
    task_queue.put(url)

# 创建线程池
threads = []
num_threads = 5  # 可以调整线程数

# 启动线程
for _ in range(num_threads):
    t = threading.Thread(target=worker, args=(task_queue,))
    t.start()
    threads.append(t)

# 阻塞主线程直到所有任务完成
task_queue.join()

# 停止工作线程
for _ in range(num_threads):
    task_queue.put(None)  # 向队列中添加None，让每个线程都能接收到并停止

# 等待所有线程完成
for t in threads:
    t.join()

# ! 结束时间
endtime = time.time()
# ! 程序运行时间
waste_time = endtime - starttime
print(f"程序耗时:{waste_time}秒")
# 耗时大概400s