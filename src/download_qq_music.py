import os

# --------------------------------------获取歌单----------------------------------


# 这个文件目录建议用everything查找，找到  QQMusicCache\QQMusicLyricNew，将目录copy下来，放到file_path中
file_path= "E:\QQMusicCache\QQMusicLyricNew" # 该目录下存放着你的音乐的链接
save_file_path = r"歌单保存的地方" # 自行填写地址

# file_path 目录下的文件样式，每个类别使用 - 分割
# 前面为歌手名，当然也可以为一群歌手，一群歌手的情况下，每个歌手以_进行分割
# 然后是歌曲名称
# 330 并不知道详细含义，也许是歌曲列表里的编号？
# 然后是专辑名称
# Aimer (エメ) - 茜さす (夕晖) - 330 - 茜さす_everlasting snow (夕晖_everlasting snow)_qmRoma.qrc


with open(save_file_path, "w",encoding="utf-8") as f:
    lists = os.listdir(file_path)
    for i in lists:
        # file_path 目录下有几种结尾后缀，但是前面的内容都差不多，这里使用_qm.qrc，因为基本上这个后缀是都有的
        if i.endswith("_qm.qrc"):
            items = i.split("-")
            author = items[0] 
            song_name = items[1] 
            f.write(song_name + " | " + author + "\n")



# --------------------------------------下载歌曲----------------------------------
# 采用网页自动化的方式下载
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pyperclip
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


def download(name,url):
    save_path = r"保存歌曲的路径"
    html = requests.get(url)
    file_path = save_path + "\\" + name + ".mp3"
    if os.path.exists(file_path):
        pass
    else:
        with open(file_path,"wb") as f:
            f.write(html.content)
        
        
        
with open(save_file_path,'r',encoding="utf-8") as f:
    contents = f.readlines()

options = Options()
options.add_experimental_option("detach",True)

wait_timeout = 10 # 设置最长等待时间

driver = webdriver.Chrome(options=options)


for content in contents:
    song = content.split("|")[0]
    print(song)
    try:
        driver.get(f'https://www.myfreemp3.com.cn/?page=audioPage&type=netease&name={song}')
        
        try:
            close_button = WebDriverWait(driver, wait_timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "a.layui-layer-ico.layui-layer-close.layui-layer-close2")))
            close_button.click()
        except:
            pass
        download_button = WebDriverWait(driver, wait_timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.aplayer-list-download.iconfont.icon-xiazai")))
        download_button.click()
        copy_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#m-download > div > div > div.modal-body > div:nth-child(3) > div.input-group-append > a.btn.btn-outline-secondary.copy > i")))
        copy_button.click()
        content = pyperclip.paste()
        download(song,content)
    except:
        pass
    

driver.quit()