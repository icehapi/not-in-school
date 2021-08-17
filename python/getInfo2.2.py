import time
import requests
import json
import pymysql
import smtplib
from email.mime.text import MIMEText  # 邮件文本
from itertools import chain

unsign = -10
register_success = 0
undefineError = -100


url = "https://student.wozaixiaoyuan.com/my/getStudentSecretInfo.json"
headers = {
   "content-length": "0",
   "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
   "content-type": "application/x-www-form-urlencoded",
   "jwsession": "",
   "referer": "https://servicewechat.com/wxce6d08f781975d91/176/page-frame.html",
   "accept-encoding": "gzip, deflate, br",
}
query = 'insert into stu_info(sno, email, name, token, sendemail, state) values(%s, %s, %s, %s, %s, %s)'
locationQuery = 'insert into stu_location(sno, province, city, district, township, street, areacode, lng, lat) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'


def log(printsrt):
    strtime = time.strftime('%H:%M:%S', time.localtime(time.time()))
    strday = "RUNLOG-" + time.strftime('%Y-%m-%d', time.localtime(time.time())) + ".txt"
    print(strtime + "  " + str(printsrt))
    with open("/home/src/notinschool/datalog/" + strday, "a", encoding='utf-8') as logg:
        logg.write("[getInfo]: " + strtime + "  " + str(printsrt) + "\n")


def postFormNightlocate(mysql_token):
    headers['jwsession'] = mysql_token
    try:
        res = requests.get(url=url, headers=headers)
        info_dict = json.loads(res.text)
        return info_dict
    except Exception as e:
        log(e)
        # print(e)

def sendemail2(receiver, content):
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
    text = "有新的人加入了, "
    # 填入 mysql 用户名和密码
    db_config = {
        'user': '',
        'password': '',
        'db': 'book',
        'charset': 'utf8'
    }
    # 填入 mysql 用户名和密码
    info_config = {
        'user': '',
        'password': '',
        'db': 'book',
        'charset': 'utf8'
    }
    # 填入 mysql 用户名和密码
    location_config = {
        'user': '',
        'password': '',
        'db': 'book',
        'charset': 'utf8'
    }
    # 连接mysql数据库
    con = pymysql.connect(**db_config)
    # 创建游标 ， 利用游标来执行sql语句
    cur = con.cursor()
    # 连接mysql数据库
    con_info = pymysql.connect(**info_config)
    # 创建游标 ， 利用游标来执行sql语句
    cur_info = con_info.cursor()
    tmpcur = con_info.cursor()

    con_location = pymysql.connect(**location_config)
    cur_location = con_location.cursor()
    try:
        # 执行sql语句，不会返回结果，返回其影响的行数
        cur.execute("select * from user")
        # 获取结果
        values = cur.fetchall()
        # 白名单机制，不需要则注释相应位置
        cur.execute("select sno from whitelist")
        whitelist = list(chain.from_iterable(cur.fetchall()))

        flag = False
        for value in values:
            # print(value)
            info_dict = postFormNightlocate(value[0])
            # 检测是否在白名单内
            if(info_dict["data"]["number"] not in whitelist):
                log("id: " + info_dict["data"]["number"] + ", name: " + info_dict["data"]["name"] + " 不在白名单")
                continue
            log("name: " + info_dict["data"]["name"] + " 上传了数据")
            # log(info_dict)
            try:
                if (info_dict['code'] == -10):
                    cur.execute("delete from user where token =" + "'" + value[0] + "'")
                    continue
            except:
                pass
            tmpcur.execute("select * from stu_info where sno =" + "'" + info_dict["data"]["number"] + "'")
            res = tmpcur.fetchall()
            if (len(res)):
                cur_info.execute(
                    "update stu_info set token=" + "'" + value[0] + "'" + "where sno=" + "'" + info_dict["data"][
                        "number"] + "'")
                cur_info.execute(
                    "update stu_info set email=" + "'" + info_dict["data"]["email"] + "'" + "where sno=" + "'" +
                    info_dict["data"]["number"] + "'")
                cur_info.execute(
                    "update stu_info set sendemail=" + "'" + "1" + "'" + "where sno=" + "'" + info_dict["data"][
                        "number"] + "'")
                if(value[9] == "1"):
                    cur_info.execute(
                        "update stu_location set province=" + "'" + value[1] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set city=" + "'" + value[2] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set district=" + "'" + value[3] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set township=" + "'" + value[4] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set street=" + "'" + value[5] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set areacode=" + "'" + value[6] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set lng=" + "'" + value[7] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                    cur_info.execute(
                        "update stu_location set lat=" + "'" + value[8] + "'" + "where sno=" + "'" + info_dict["data"][
                            "number"] + "'")
                cur.execute("delete from user where token =" + "'" + value[0] + "'")
                log(info_dict["data"]["name"] + "已更新")
            else:
                # continue
                email = info_dict["data"]["email"]
                # 判断是否上传过地理信息
                if(value[9] == "0"):
                    sendemail2(email, "第一次上传请上传位置信息，请重新运行程序并选择另外两种方案。")
                    cur.execute("delete from user where token =" + "'" + value[0] + "'")
                    continue
                flag = True
                sno = info_dict["data"]["number"]
                name = info_dict["data"]["name"]
                token = value[0]
                sendemail = "1"
                state = "1"
                infoValues = (sno, email, name, token, sendemail, state)
                sendemail2(email, "温馨提示:请勿乱传。token过期后会有邮件提示，需重新运行我不在校园V2.exe，重新提交后若还在时间段内无需手动补签。")
                text += name + ", "
                log(name + "已加入")
                cur_info.execute(query, infoValues)
                province = value[1]
                city = value[2]
                district = value[3]
                township = value[4]
                street = value[5]
                areacode = value[6]
                lng = value[7]
                lat = value[8]
                locationValues = (sno, province, city, district, township, street, areacode, lng, lat)
                cur_info.execute(locationQuery, locationValues)
                cur.execute("delete from user where token =" + "'" + value[0] + "'")
        if(flag):
            # 填入邮箱用于接收推送
            sendemail2("*****@qq.com", text + "已加入")
        # 提交到数据库，真正把数据插入或者更新到数据
        con.commit()
        con_info.commit()
        con_location.commit()
    except Exception as e:
        log(e)
        # 发生了异常，回滚
        con.rollback()
        con_info.rollback()
        con_location.rollback()
    finally:
        # 在最后使用完关闭游标和连接
        # 关闭游标
        cur.close()
        # 关闭连接
        con.close()
        # 关闭游标
        cur_info.close()
        # 关闭连接
        con_info.close()
        cur_location.close()
        con_location.close()
        


main()
