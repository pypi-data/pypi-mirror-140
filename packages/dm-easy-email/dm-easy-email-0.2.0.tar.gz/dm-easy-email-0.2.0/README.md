# **邮件**
封装简单的邮件推送功能，支持发送单个或多个收件/抄送人，支持附件上传（未实现）

## **项目结构**
- easy-email
  - LISENCE.md
  - README.md
  - setup.py
  - src
    - \_\_init\_\_.py
    - easy_email.py
  - tests
    - conf
      - email_conf.yml
      - column_config.yml
    - template
      - template.html
    - \_\_init\_\_.py
    - example.py
    - table_example.py
    - test_class.py

## **使用方法**


### **配置文件模板**
#### **模板1--邮件发送**
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

#### **模板2--html列表配置参数**
    - column_code: a
      column_name: a
      align: center
      unit: '%'
      width: 50px
    - column_code: b
      column_name: b
      align: center
      unit: ''
      width: 150px
    - column_code: c
      column_name: c
      align: center
      unit: ''
      width: 100px
    - column_code: d
      column_name: d
      align: center
      unit: '%'
      width: 50px

### **示例1(body_type='plain')**

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

### **示例2(body_type='html')**
    from easy_email.easy_email import EasyEmail
    from ruamel import yaml
    import pandas as pd
    import string

    if __name__ == '__main__':
        with open('conf/email_conf.yml', 'r') as f:
            content = yaml.load(f, Loader=yaml.Loader)

        with open('conf/column_config.yml', 'r') as f_config:
            column_config = yaml.load(f_config, Loader=yaml.Loader)
        
        df = pd.DataFrame(
            {'a': [i for i in range(10)],
            'b': ['a' for _ in range(10)],
            'c': ['hello' for _ in range(10)],
            'd': [i for i in range(10, 20)]}
            )
        df.to_csv('data/data.csv', index=None)
        sender = content['sender']
        receiver = content['receiver']
        subject = content['subject']
        nickname = content['nickname']
        file_path = 'data/data.csv'
        passwd = content['passwd']
        email = EasyEmail(
            sender=sender, passwd=passwd,
            subject=subject, nickname=nickname, 
            receiver=receiver,
            file_path=file_path
            )
        emo = {
            'col': ['a', 'd'], 
            'threshold': 16, 
            'is_upper': True
            }
        table_html = email.table_to_html(
                        df=df, 
                        column_config=column_config, 
                        sort={'var': ['a', 'd'], 'ascending': False},
                        row_limit=30, 
                        emo=emo
                        )
        template_html = open('template/template.html', encoding='utf8').read()
        body = string.Template(template_html).safe_substitute(
            {
                'task1': table_html
            }
        )
        email.send(body, 'html')

## **开发日志**
2022-2-17
1. 完成邮件推送功能开发与测试，并推至仓库
2. 完成打包并发布到pypi
   
2022-2-28
1. 调整邮件发送类型，支持html
  
2022-3-2
1. 新增dataframe转化html功能
2. 补充dataframe转化示例