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

from matplotlib.pyplot import table


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
    
    def send(self, body: str, body_type: str='plain'): 
        """邮件发送函数

        Args:
            body (str): 邮件正文内容
            body_type (str): 邮件内容的类型，e.g 'plain', 'html' ..., 
                             defaults to plain.
        """
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
        """邮件发送内置函数

        Args:
            email (MIMEMultipart): 邮件主体
        """
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
        
    def table_to_html(self, df, column_config, sort=None, row_limit=30, emo=None):
        """若发送内容中包含表格，调用此函数对表格进行html格式转换

        Args:
            df (pd.DataFrame): 需要转化的表格
            column_config (list[dict]): 表格每一列的html配置参数
            sort (dict): {'var': [col1, col2...], 'ascending': True/False}
            row_limit (int): 邮件内容的表格展示行数限制. Defaults to 30.
            emo (dict): 
                是否需要添加表情，指定指标大于或小于某阈值显示xx. Defaults to None.
                目前仅支持两种表情。
                e.g {'col': [col1, col2..], 'threshold': xx, 'is_upper': True}
                    col--指定的列, value (list[str])
                    threshold--区分表情的阈值, value (int, float)
                    is_upper--True是大于阈值点赞，False是小于阈值点赞, value (bool)
                    阈值目前仅支持设置一个。
        
        Returns:
            html (str): html格式的字符串
        """
        # dataframe 排序
        if sort:
            try:
                df.sort_values(
                    sort['var'], 
                    ascending=sort.get('ascending', False),
                    inplace=True
                    )
            except KeyError:
                raise KeyError(
                    'Dict must have key called "var" to store \
                     target variables.'
                    )
        table_html = """
        <table>
            <thead>
            <tr style="text-align: right;">
        """
        if not isinstance(column_config, (list, type(None))):
            raise TypeError('column_config must be list[dict] or NoneType.')
        if column_config is None:
            column_config = [{'column_code': c, 'column_name': c} for c in df.columns]
        # 添加配置内容
        table_html = self._config_html_trans(table_html, column_config)
        table_html += """
        </tr>
            </thead>
            <tbody>
        """
        # 添加dataframe表格内容
        table_html = self._df_html_trans(df, table_html, column_config, row_limit, emo)
        table_html += """
        </tbody>
        </table>
        """
        return table_html

    def _config_html_trans(self, table_html: str, column_config: list[dict]):
        """内置函数，为html格式字符串增加config内容，主要包含align, width

        Args:
            table_html: (str): 需要被添加配置内容的html字符串
            column_config (list[dict]): 表格每一列的html配置参数
        """
        for col in column_config:
            style = col.get('style', '')
            if col.get('align') is not None:
                if (not style) | (style.endswith(';')):
                    style += "text-align:%s" % col.get('align')
                else:
                    style += ";text-align:%s" % col.get('align')
            if col.get('width'):
                if (not style) | (style.endswith(';')):
                    style += "width:%s" % col.get('width')
                else:
                    style += ";width:%s" % col.get('width')
            col['style'] = style
            column_name = col.get('column_name') or col.get('column_code')
            table_html += '<th style="%s">%s</th>' % (style, column_name)
        return table_html

    def _df_html_trans(self, df, table_html, column_config, row_limit=30, emo=None):
        """内置函数，以html形式添加dataframe内容到字符串中

        Args:
            df (pd.DataFrame): 需要转化的表格
            table_html (str): 需要添加的html字符串
            column_config (list[dict]): 表格每一列的config内容
            emo (dict): 
                是否需要添加表情，指定指标大于或小于某阈值显示xx. Defaults to None.
                目前仅支持两种表情。
                e.g {'col': [col1, col2..], 'threshold': xx, 'is_upper': True}
                    col--指定的列, value (list[str])
                    threshold--区分表情的阈值, value (int, float)
                    is_upper--True是大于阈值点赞，False是小于阈值点赞, value (bool)
                    阈值目前仅支持设置一个。
        """
        counter = 1
        for index in df.index:
            if counter > row_limit:
                break
            table_html += '<tr>'
            emo
            for col in column_config:
                if emo and (col['column_code'] in emo['col']):
                        style, col_substr = self._add_emo(index, df, col, emo)
                        table_html += '<td style="%s">%s</td>' % (
                            style, col_substr
                        )
                else:
                    table_html += '<td>%s%s</td>' % (
                        df.loc[index, col.get('column_code')], col.get('unit', '')
                    )
            table_html += '</tr>'
            counter += 1
        return table_html

    def _add_emo(self, index, df, col, emo):
        """内置函数，dataframe转化html过程中添加表情

        Args:
            index (pd.Index)
            df (pd.DataFrame): 转化html的dataframe
            col (dict): 需要添加表情的字典
            emo (dict): 包含阈值与正向表情判断
        """
        col_substr = str(df.loc[index, col.get('column_code')])
        style = col.get('style', '')
        try:
            threshold = emo['threshold']
            is_upper = emo['is_upper']
        except KeyError:
            logger.warning('Threshold and is_upper must be keys in dict.')
        # finally:
        #     logger.info('Skip emotion adding.')
        #     pass
        if float(col_substr) >= threshold:
            col_substr += col.get('unit', '')
            col_substr += '😊' if is_upper else '😱'
            style += ';color:red' if is_upper else ';color:green'
        else:
            col_substr += col.get('unit', '')
            col_substr += '😱' if is_upper else '😊'
            style += ';color:green' if is_upper else ';color:red'
        return style, col_substr


if __name__ == '__main__':
    doctest.testmod()
