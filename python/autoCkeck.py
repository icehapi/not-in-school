import time
import requests
import json
import pymysql
import smtplib #smtp服务器
from email.mime.text import MIMEText #邮件文本
import datetime
import random
import urllib3

urllib3.disable_warnings()
unsign = -10
check_success = 0
undefineError = -100

url = "https://student.wozaixiaoyuan.com/health/getToday.json"
headers={\
"Host": "student.wozaixiaoyuan.com",
"Content-Type": "application/x-www-form-urlencoded",
"Accept-Encoding": "gzip, deflate, br",
"Connection": "keep-alive",
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
"Referer": "https://servicewechat.com/wxce6d08f781975d91/147/page-frame.html",
"jwsession": "",
"Content-Length": "374",
}
headers_info={\
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
"content-type": "application/json",
"Referer":  "https://servicewechat.com/wxce6d08f781975d91/175/page-frame.html",
"jwsession" : ""
}

def checkTime():
    time = datetime.datetime.now()
    hour = time.hour
    min = time.minute
    if(0 <= hour and hour <= 22):
        if(hour == 22 and min == 30):
            return False
        return True


def log(printsrt):
    strtime = time.strftime('%H:%M:%S', time.localtime(time.time()))
    strday = "RUNLOG-"+time.strftime('%Y-%m-%d', time.localtime(time.time()))+".txt"
    print(strtime + "  " + str(printsrt))
    with open ("/home/src/notinschool/datalog/"+strday,"a",encoding='utf-8') as logg:
        logg.write("[autoCheck]: "+strtime+"  "+str(printsrt)+"\n")

def postFormNightlocate(token):
    headers_info['jwsession']=token
    try:
        res = requests.get(url=url, headers=headers_info, verify=False)
        info_dict = json.loads(res.text)
        return info_dict
    except Exception as e:
        log(e)
        # print(e)

def sendemail2(receiver,content):
    # 邮件标题
    subject = "我不在校园"  
    # 发送方: 邮箱地址
    sender = ""  
    # 接收方
    recver = receiver  
    # 密码(不是邮箱登录密码)
    password = ""
    message = MIMEText(content, "plain", "utf-8")
    # content 发送内容     "plain"文本格式   utf-8 编码格式
    message['Subject'] = subject  # 邮件标题
    message['To'] = recver  # 收件人
    message['From'] = sender  # 发件人
    smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
    smtp.login(sender, password)  # 发件人登录
    smtp.sendmail(sender, [recver], message.as_string())  # as_string 对 message 的消息进行了封装
    smtp.close()

def main():
    # 填入 mysql 用户名和密码
    db_config = {
        'user': '',
        'password': '',
        'db': 'book',
        'charset':'utf8'
    }
    # 填入 mysql 用户名和密码
    info_config = {
        'user': '',
        'password': '',
        'db': 'book',
        'charset': 'utf8'
    }
    # 连接mysql数据库
    con = pymysql.connect(**db_config)
    # 创建游标 ， 利用游标来执行sql语句
    cur = con.cursor()
    # 连接数据库
    infoCon = pymysql.connect(**info_config)
    infoCur = infoCon.cursor()
    try:
        # 执行sql语句，不会返回结果，返回其影响的行数
        cur.execute("select sno,token,email,sendemail,name,state from stu_info")
        # 获取结果
        values = cur.fetchall()
        # 获取定位信息
        for value in values:
            #print('1')
            if(value[5] == "1"):
                info_dict = postFormNightlocate(value[1])
                if(str(info_dict['code'])=='-10'):
                    # log("id:" + value[0] + " status: token outdated")
                    if(value[3]=='1'):
                        sendemail2(value[2],r"Token信息已过期，请及时更新, 注意上传token时等待脚本自动退出，否则可能上传失败。")
                        log("id:" + value[0] + " status: sendemail succeed")
                        cur.execute("update stu_info set sendemail="+"'"+"0"+"'"+"where sno="+"'"+value[0]+"'")
                    else:
                        # log("name: "+ value[4]+"senemail=0")
                        pass
                    continue
                if(str(info_dict['code'])!='0' and str(info_dict['code'])!='-10'):
                    log(value[4]+str(info_dict['code']))
                    # 填入邮箱用于接收推送
                    sendemail2("*****@qq.com","autoCheck出现错误")
                    continue
                #print('2')
                userType = info_dict['data']['titles'][0]['healthOptions'][0]['select']
                # print(userType)
                if(checkTime() and userType == 0):
                    #print('3')
                    infoCur.execute("select province, city, district, township, street, areacode, lng, lat from stu_location where sno=" + "'" + value[0] + "'")
                    location = infoCur.fetchone()
                    data = createData(location)
                    # print(data)
                    status = postFormCheck(value[1], data)
                    if(status == undefineError):
                        # 填入邮箱用于接收推送
                        sendemail2("*****@qq.com",str(value[0])+"出现未知错误")
                        log("id:" + value[0] + ", status: undefineError")
                    elif(status == check_success):
                        cur.execute("update stu_info set sendemail="+"'"+"1"+"'"+"where sno="+"'"+value[0]+"'")
                        log("id: "+value[0]+", status: check success")
                        
        # 提交到数据库，真正把数据插入或者更新到数据
        con.commit()
        infoCon.commit()
    except Exception as e:
        log(e)
        # print(e)
        # 填入邮箱用于接收推送
        sendemail2("*****@qq.com","autoEnroll出现错误")
        # 发生了异常，回滚
        con.rollback()
        infoCon.rollback()
    finally:
        # 在最后使用完关闭游标和连接
        # 关闭游标
        cur.close()
        # 关闭连接
        con.close()

        infoCur.close()
        infoCon.close()

def postFormCheck(token, data):
    headers['jwsession'] = token
    # print(data)
    # realdata = data.replace("seq=xxxxx","seq="+ctime)
    try:
        res = requests.post(url="https://student.wozaixiaoyuan.com/health/save.json", data=data, headers=headers)
        dict_json = json.loads(res.text)
        if(dict_json['code']==-10):
            return unsign
        elif(dict_json['code']==0):
            return check_success
        else:
            log(res.text)
            return undefineError
    except Exception as e:
        log(e)
        # print(e)

def createData(location):

    data = {
        "answers" : '["0","3","1","无","无","0"]',
        "latitude" : location[7],
        "longitude" : location[6],
        "country" : "中国",
        "city" : location[1],
        "district" : location[2],
        "province" : location[0],
        "township" : location[3],
        "street" : location[4],
        "areacode" : location[5]
    }
    return data

main()
