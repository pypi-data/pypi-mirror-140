# **邮件**
封装简单的邮件推送功能，支持发送单个或多个收件/抄送人，支持附件上传（未测试）

## **项目结构**
- dm-utils
  - LISENCE.md
  - README.md
  - setup.py
  - easy-email
    - \_\_init\_\_.py
    - easy_email.py
    - example.py
    - conf
      - email.yml

## **使用方法**


  ### **配置文件模板**
    
    sender:
      xxx@example.com
    passwd: 
      your_passwd
    receiver:
      - aaa@example.com
      - bbb@example.com
    subject:
      your_title
    # Params below could be None
    nickname:
      your_nickname
    cc:
      ccc@example.com


  ### **示例**

    from easy_email.easy_email import EasyEmail
    from ruamel import yaml
    import os


    if __name__ == '__main__':
        print(os.getcwd())
        with open('conf/email.yml', 'r') as f:
            content = yaml.load(f, Loader=yaml.Loader)
        sender = content['sender']
        receiver = content['receiver']
        subject = content['subject']
        nickname = content['nickname']
        # file_path = 'conf/email.yml'
        passwd = content['passwd']
        cc = content['cc']
        email = EasyEmail(
            sender=sender, passwd=passwd,
            subject=subject, nickname=nickname, 
            receiver=receiver, cc=cc
            )
        body = 'Hello world'
        email.send(body)

## **开发日志**
2022-2-17
1. 完成邮件推送功能开发与测试，并推至仓库
2. 完成打包并发布到pypi
   
