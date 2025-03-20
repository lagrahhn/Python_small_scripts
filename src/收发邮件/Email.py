import email.header
import os
import json
import imaplib
import email
import time
import logging
from email import message_from_bytes
from dateutil import parser
from email.header import Header, make_header
from email.mime.base import MIMEBase
import smtplib
from email.utils import formataddr, parsedate_to_datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header


password = "qnyxdfvdkqlgdcjh"
Email_address = "3220135059@qq.com"

class Plugin():
    
    SLUG = "email"

    def __init__(self):
        self.load_config()
        self.sender_email = None
        self.sender_password = None
        self.current_account_index = 0 # 默认使用第一个账户
        self.update_account_info()
        
        
    def load_config(self):
        """
            读取配置文件
        """
        with open("./config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
    
    def update_account_info(self):
        """
            更新账户信息
        """
        account = self.config['accounts'][self.current_account_index]
        self.sender_email = account['sender_email']
        self.sender_password = account['sender_password']
        self.imap_server = account['imap_server']
        self.imap_port = account['imap_port']
        self.smtp_server = account['smtp_server']
        self.smtp_port = account['smtp_port']

    def switch_account(self,index):
        if 0 <= index < len(self.config['accounts']):
            self.current_account_index = index
            self.update_account_info()
            print(f"已切换到账户:{self.email}")
        else:
            print("无效的账户索引")
    
    def send_email(self, subject, message, receiver):
        msg = MIMEText(message,"plain","utf-8")
        msg['From'] = self.sender_email
        msg['To'] = Header(receiver,"utf-8")
        msg['Subject'] = Header(subject,"utf-8")
        
        server = None  # 初始化 server 变量
        try:
            print(self.smtp_server)
            print(self.smtp_port)
            print(self.sender_email)
            print(self.sender_password)
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port,timeout=10)
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, [receiver], msg.as_string())
            print("邮件发送成功！")
        except Exception as e:
            print("邮件发送失败:", e)
        finally:
            if server:  # 检查 server 是否存在
                server.quit()
    
    def send_email_with_attachment(self, subject, message, receiver, attachment_path):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = Header(receiver,"utf-8")
        msg['Subject'] = Header(subject,"utf-8")

        msg.attach(MIMEText(message,"plain","utf-8"))
        with open(attachment_path, 'rb') as f:
            mime = MIMEBase('application', 'octet-stream')
            mime.set_payload(f.read())
            from email import encoders
            encoders.encode_base64(mime)
            mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
            msg.attach(mime)
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port,timeout=10)
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, [receiver], msg.as_string())
            print("邮件发送成功！")
        except Exception as e:
            print("邮件发送失败:", e)
        finally:
            if server:  # 检查 server 是否存在
                server.quit()
    
    def group_send(self, subject, message, receivers):
        for receiver in receivers:
            self.send_email(subject, message, receiver)
            
    def search_imap_by_part_content(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        server.login(self.sender_email, self.sender_password)
        # INBOX 收件箱
        # Sent Messages 已发送
        # Drafts 草稿箱
        # Deleted Messages 已删除
        # Junk 垃圾箱
        server.select('INBOX')
        
        # 选择收件箱
        # status: OK
        status, search_data = server.search(None, search.encode("utf-8"))

        # 一个数组，里面是邮件id
        mail_list = search_data[0].split()
        print(f"总共解析了{len(mail_list)}封邮件")
        for mail_id in mail_list:
            # result和上面的status一样，仍然是OK类型
            result,data = server.fetch(mail_id,"(RFC822)")
            if result == "OK":
                email_message = message_from_bytes(data[0][1]) # 邮件内容（未解析）
                # print(email_message)
                subject = make_header(decode_header(email_message['SUBJECT']))
                mail_from = make_header(decode_header(email_message['From']))
                mail_time = parsedate_to_datetime(email_message['Date']).strftime("%Y-%m-%d %H:%M:%S")
                # email_info = {
                #     "主题": subject,
                #     "发件人": mail_from,
                #     "收件时间": mail_time
                # }
                print(subject)
                print(mail_from)
                print(mail_time)
                # print(email_info)
        server.close()
        server.logout()
        return data

    def search_imap_by_subject(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

        server.login(self.sender_email, self.sender_password)
        server.select('INBOX')
        result, data = server.search(None, 'ALL')
        if result == 'OK':
            for num in data[0].split():
                result, data = server.fetch(num, '(RFC822)')
                if result == 'OK':
                    email_message = message_from_bytes(data[0][1]) # 邮件内容（未解析）
                    # print(email_message)
                    subject = make_header(decode_header(email_message['SUBJECT']))
                    mail_from = make_header(decode_header(email_message['From']))
                    mail_time = parsedate_to_datetime(email_message['Date']).strftime("%Y-%m-%d %H:%M:%S")
                    if search in str(subject):
                        print(subject)
        server.close()
        server.logout()
        return data
    
    def search_imap_by_sender(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

        server.login(self.sender_email, self.sender_password)
        server.select('INBOX')
        result, data = server.search(None, 'ALL')
        if result == 'OK':
            for num in data[0].split():
                result, data = server.fetch(num, '(RFC822)')
                if result == 'OK':
                    email_message = message_from_bytes(data[0][1]) # 邮件内容（未解析）
                    # print(email_message)
                    subject = make_header(decode_header(email_message['SUBJECT']))
                    mail_from = make_header(decode_header(email_message['From']))
                    # mail_time = parsedate_to_datetime(email_message['Date']).strftime("%Y-%m-%d %H:%M:%S")
                    if search in str(mail_from):
                        print(subject)
        server.close()
        server.logout()
        return data
    
    
    
    # TODO 添加获取指定编号的邮件内容
    # TODO 添加删除指定邮件的操作
    # TODO 添加编辑邮件的操作
    
    

email_plugin = Plugin()        
email_subject = "22"
email_message = "33"
recipient_email = "my@qq.com"
email_plugin.search_imap_by_sender("my@qq.com")
# email_plugin.search_imap_by_subject("你好")
# email_plugin.search_imap_by_part_content("你好")
# email_plugin.send_email(email_subject,email_message,recipient_email)
# email_plugin.send_email_with_attachment(email_subject,email_message,recipient_email,r"./image.png")
# email_plugin.group_send(email_subject,email_message,[recipient_email,"my@163.com"])

