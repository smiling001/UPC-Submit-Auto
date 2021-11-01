import os
import requests
import json
import lxml.html
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header


signIn = {'username': os.environ["USERNAME"], #学号
          'password': os.environ["PASSWORD"]} #登陆密码

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Mobile Safari/537.36',
}

conn = requests.Session()
signInResponse= conn.post(
    url="https://app.upc.edu.cn/uc/wap/login/check",
    headers=headers,
    data= signIn, 
    timeout=10
)

historyResponse = conn.get(
    url="https://app.upc.edu.cn/ncov/wap/default/index?from=history",
    headers=headers,
    data={'from': 'history'},
    timeout=10
)
historyResponse.encoding = "UTF-8"

html = lxml.html.fromstring(historyResponse.text)
JS = html.xpath('/html/body/script[@type="text/javascript"]')
JStr = JS[0].text
default = re.search('var def = {.*};',JStr).group()
oldInfo = re.search('oldInfo: {.*},',JStr).group()

firstParam = re.search('sfzgsxsx: .,',JStr).group()
firstParam = '"' + firstParam.replace(':','":')
secondParam = re.search('sfzhbsxsx: .,',JStr).group()
secondParam = '"' +  secondParam.replace(':','":')
lastParam = re.search('szgjcs: \'(.*)\'',JStr).group()
lastParam = lastParam.replace('szgjcs: \'','').rstrip('\'')

newInfo = oldInfo
newInfo = newInfo.replace('oldInfo: {','{' + firstParam + secondParam).rstrip(',')

defaultStrip = default.replace('var def = ','').rstrip(';')
defdic = json.loads(defaultStrip)

dic = json.loads(newInfo)
dic['ismoved'] = '0'
for j in ["date","created","id","gwszdd","sfyqjzgc","jrsfqzys","jrsfqzfy"]:
    dic[j] = defdic[j]
dic['szgjcs'] = lastParam

saveResponse = conn.post(
    url="https://app.upc.edu.cn/ncov/wap/default/save",
    headers=headers,
    data = dic,
    timeout=10
)

saveJson = json.loads(saveResponse.text)

# 第三方 SMTP 服务
mail_host = "smtp.qq.com"  # 设置服务器
mail_user = "2819237058@qq.com"  # 用户名
mail_pass = "lyimhkqaudcudfbd"  # 口令

sender = '2819237058@qq.com'
receivers = ['3492720037@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

message = MIMEText(saveJson['m'], 'plain', 'utf-8')
message['From'] = Header("疫情防控通填报通知", 'utf-8')
message['To'] = Header("测试", 'utf-8')

subject = '疫情防控通'
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")
print(saveJson['m'])
