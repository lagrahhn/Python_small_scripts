import email.header
import os
import json
import imaplib
import email
from email.header import Header
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Plugin():
    
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
    
    # TODO 待测试     
    def search_imap_by_part_content(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        server.login(self.sender_email, self.sender_password)
        server.select('INBOX')
        # 将search设置为utf-8编码
        search = search.encode('utf-8')
        result, data = server.search(None, search)
        if result == 'OK':
            for num in data[0].split():
                print(num)
                result, data = server.fetch(num, '(RFC822)') #  使用邮件编号从服务器获取邮件内容，'(RFC822)'表示获取完整的邮件内容
                if result == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    # print(msg['From'], msg['Subject'])
        server.close()
        server.logout()
        return data

    # TODO 待测试
    def search_imap_by_subject(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

        server.login(self.sender_email, self.sender_password)
        server.select('INBOX')
        result, data = server.search(None, '(SUBJECT "{}")'.format(search))
        if result == 'OK':
            for num in data[0].split():
                result, data = server.fetch(num, '(RFC822)')
                if result == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    print(msg['From'], msg['Subject'])
        server.close()
        server.logout()
        return data
    
    # TODO 待测试
    def search_imap_by_sender(self,search):
        server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)

        server.login(self.sender_email, self.sender_password)
        server.select('INBOX')
        result, data = server.search(None, '(FROM "{}")'.format(search))
        if result == 'OK':
            for num in data[0].split():
                result, data = server.fetch(num, '(RFC822)')
                if result == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    print(msg['From'], msg['Subject'])
        server.close()
        server.logout()
        return data
    
    # TODO 待测试
    def group_send(self, subject, message, receivers):
        for receiver in receivers:
            self.send_email(subject, message, receiver)
    
    # TODO 待添加获取指定编号的邮件内容
    
    

email_plugin = Plugin()        
email_subject = "22"
email_message = "33"
recipient_email = "3220135059@qq.com"
email_plugin.search_imap_by_part_content("你好")
# email_plugin.send_email(email_subject,email_message,recipient_email)
# email_plugin.send_email_with_attachment(email_subject,email_message,recipient_email,r"./image.png")

