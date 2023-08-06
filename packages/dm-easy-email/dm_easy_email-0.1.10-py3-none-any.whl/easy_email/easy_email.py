#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   easy_email.py
@Time    :   2022/01/14 11:27:04
@Author  :   Shenxian Shi 
@Version :   
@Contact :   shishenxian@bluemoon.com.cn
@Desc    :   None
'''

# here put the import lib
import smtplib 
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, parseaddr
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import sys
import logging
import doctest


LOG_FORMAT = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(LOG_FORMAT)
logger.addHandler(sh)


class SetEmail(object):
    def __init__(self, default=None):
        self._address = default
        
    def __get__(self, instance, owner):
        return self._check_addr(self._address)
    
    def __set__(self, instance, value):
        if not isinstance(value, (str, list, tuple)):
            raise TypeError('The value must be a string, list or tuple.')
        if isinstance(value, str):
            if '@' not in value:
                raise ValueError('The string must be email address.')
        else:
            for i in value:
                if '@' not in i:
                    raise ValueError('The string must be email address.')
        self._address = self._check_addr(value)
        
        
    def _check_addr(self, addr):
        """检查邮箱地址，若为字符串带逗号，则进行分割并处理；若
        为列表或元组，则逐个进行处理

        Args:
            addr ([str, list, tuple]): 邮箱地址

        Returns:
            [str, list]:  
                a. 'xxx<aaa@example.com>'
                b. ['xxx<aaa@example.com>', 'yyy<bbb@example.com>','...']
                c. 'aaa@example.com'
                d. ['aaa@example.com', 'bbb@example.com','...']
        """
        # 处理传入空值的情况，避免传入空值后触发Assertion Error
        if addr is not None:
            if not isinstance(addr,(str, list, tuple)):
                raise AssertionError(
                    'The type of address must be str, list or tuple.'
                    )
        else:
            return addr
        
        if isinstance(addr, str):
            if ',' in addr:
                tmp_lst = addr.split(',')
                for i in range(len(tmp_lst)):
                    tmp_lst[i] = self._format_addr(tmp_lst[i])
                return ','.join(tmp_lst)
            else:
                return self._format_addr(addr)
        else:
            out_lst = []
            if len(addr) > 1:
                for i in addr:
                    out_lst.append(self._format_addr(i))
                return ','.join(out_lst)
            else:
                return self._format_addr(addr[0])
            
    def _format_addr(self, address):
        name, addr = parseaddr(address)
        return formataddr((Header(name, 'utf-8').encode(), addr))


class NormalProperty(object):
    def __init__(self, default=None):
        self.string = default
    
    def __get__(self, instance, owner):
        return self.string
    
    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError('The value must be a string.')
        self.string = value


class EasyEmail(object):
    """
    邮件推送，包含发邮件、添加附件

    Methods:
        send: 发送邮件
        add_file: 添加附件
    
    Examples:
        >>> sender = 'aaa@bluemoon.com.cn'
        >>> receiver1 = 'bbb@bluemoon.com.cn, ccc@bluemoon.com.cn'
        >>> receiver2 = ['bbb@bluemoon.com.cn', 'ccc@bluemoon.com.cn']
        >>> receiver3 = ('bbb@bluemoon.com.cn', 'ccc@bluemoon.com.cn')
        >>> cc = 'ddd@bluemoon.com.cn'
        >>> subject = 'Testing'
        >>> nickname = 'Data-mining Group'
        >>> file_path = 'conf/email.yml'
        >>> passwd = 'abcde'
        >>> email = EasyEmail(sender=sender, passwd=passwd, \
        subject=subject, nickname=nickname, receiver=receiver1, \
        cc=cc, file_path=file_path)
        >>> email.receiver
        'bbb@bluemoon.com.cn,ccc@bluemoon.com.cn'
        >>> email.receiver = receiver2
        >>> email.receiver
        'bbb@bluemoon.com.cn,ccc@bluemoon.com.cn'
        >>> email.receiver = receiver3
        >>> email.receiver
        'bbb@bluemoon.com.cn,ccc@bluemoon.com.cn'
        >>> email.nickname
        'Data-mining Group'
        >>> email.cc
        'ddd@bluemoon.com.cn'
        >>> email.passwd = 'abcd'
        >>> email.passwd
        'abcd'      
    """

    def __init__(self, 
                 sender=None, 
                 passwd=None, 
                 subject=None, 
                 nickname=None, 
                 receiver=None, 
                 cc=None,
                 server='mail.bluemoon.com.cn',
                 file_path=None):
        """
        Args:
            sender (str): 发送者邮箱地址. Defaults to None. 
            passwd (str): 发送者邮箱密码. Defaults to None.
            subject (str): 发送主题. Defaults to None.
            nickname (str): 发送者名称备注. Defaults to None.
            receiver (str): 接收人邮箱地址，可用逗号分割写入多个接收邮箱. Defaults to None.
            cc (str): 抄送人邮箱地址，可用逗号分隔写入多个抄送邮箱. Defaults to None.
            server(str): 邮件服务器地址，默认蓝月亮
            file_path(str): 附件路径，若无附件则为 None.
        """
        self.sender = SetEmail(sender)
        self.passwd = NormalProperty(passwd)
        self.subject = NormalProperty(subject)
        self.nickname = NormalProperty(nickname)
        self.receiver = SetEmail(receiver)
        self.cc = SetEmail(cc)
        self.stmp_server = NormalProperty(server)
        self.file_path = NormalProperty(file_path)
        self._email = None
    
    def __getattribute__(self, name):
        attr = super(EasyEmail, self).__getattribute__(name)
        if hasattr(attr, '__get__'):
            return attr.__get__(self, EasyEmail)
        return attr
    
    def __setattr__(self, name, value):
        try:
            if hasattr(self.__dict__[name], '__set__'):
                self.__dict__[name].__set__(EasyEmail, value)
        except KeyError:
            self.__dict__[name] = value      
    
    def send(self, body, body_type): 
        email = MIMEMultipart()
        email['subject'] = self.subject
        email['to'] = self.receiver
        if not self.nickname:
            email['From'] = self.sender
        else:
            email['From'] = formataddr([self.nickname, self.sender])
        if self.cc is not None:
            email['Cc'] = self.cc 
        if self.file_path is not None:
            email.attach(self._gen_attachment())
        email.attach(MIMEText(body, body_type, 'utf-8'))  
        self._server_send(email)
        
    def _gen_attachment(self):
        attachment = MIMEApplication(open(self.file_path, 'rb').read())
        attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename=(
                'utf-8', '',
                self.file_path.split('/')[-1]
                )
            )
        return attachment
        
    def _server_send(self, email: MIMEMultipart):
        if self.cc:
            receivers = self.receiver.split(',')
            receivers.extend(self.cc.split(','))
        else:
            receivers = self.receiver.split(',')
        try:
            logger.info('Start sending email..')
            server = smtplib.SMTP_SSL(self.stmp_server, 10500)
            server.ehlo()
            server.set_debuglevel(1)
            server.login(
                self.sender, 
                self.passwd
                )
            server.sendmail(
                self.sender, 
                receivers, 
                email.as_string()
                )
            server.quit()
            logger.info('Sending finished.')
        except Exception as e:
            logger.error('%r', e)
        
if __name__ == '__main__':
    doctest.testmod()
