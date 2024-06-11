import requests
import os
import sys
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
import datetime
import configparser

try:
    from const import *
except ImportError as e:
    curr_path = os.path.abspath(__file__)
    proj_path = os.sep.join(curr_path.split(os.sep)[:-2])
    sys.path.append(proj_path)
finally:
    from const import *

cfg = configparser.ConfigParser()
cfg.read("./check.ini", encoding="utf-8")


class CheckIn(object):

    def __init__(self):
        pass

    def checkin(self):
        try:
            req = requests.post(
                url=HTTPS, data={"token": TOKEN},
                headers={
                    "user-agent": USERAGENT, "Host": HOST, "Origin": ORIGIN, "Cookie": COOKIE
                }
            )
        except Exception as e:
            print(e)
        else:
            res = req.json()
            code = res.get("code", 999)
            checkInPoint = -1
            currPoint = -1
            lastCheckInPoint = -1
            message = res.get("message", "未知信息")
            subject = message
            if code == OTHERWISE:
                print(f"未知错误: 代码{code}, 信息{message}")
                message = res
            elif code == DENIED:
                print(f"请求头错误: 代码{code}, 信息{message}")
                message = res
            elif code in OK:
                checkInPoint = int(res.get("points", -1))
                lastMessage = res.get("list", None)
                if lastMessage is None:
                    pass
                elif isinstance(lastMessage, list):
                    lastCheckInPoint = int(lastMessage[0].get("change", "-1.").split(".")[0])
                    currPoint = int(lastMessage[0].get("balance", "-1.").split(".")[0])
                    if lastCheckInPoint == -100:
                        times = int(cfg['status'].get('100cnt')) + 1
                        cfg.set("status", "100cnt", str(times))
                        with open("./check.ini", "w+") as config:
                            cfg.write(config)

            data = {
                "subject": subject,
                "date": str(datetime.datetime.now().date()),
                "message": message,
                "checkInPoint": checkInPoint,
                "currPoint": currPoint,
                "lastCheckInPoint": lastCheckInPoint,
                "100Cnt": int(cfg['status'].get('100cnt'))
            }
            self.email(data)

    @staticmethod
    def attach_image(path, cid):
        with open(path, "rb") as date:
            image = MIMEImage(date.read())
            image.add_header("Content-ID", cid)
        return image

    def email(self, data):
        message = MIMEMultipart("related")
        message.attach(self.attach_image("../template/date.png", "date"))
        message.attach(self.attach_image("../template/qiandao.png", "qiandao"))
        message.attach(self.attach_image("../template/e.png", "e"))
        html = """
            <body style="display: flex; justify-content: center;">
                <div class="wrapper" style="width: 300px;">
                    <div class="header" style="display: flex; align-items: center; justify-content: center; box-shadow: 0px 5px 4px -1px black; background-color: rgb(145,138,129);">
                        <div style="text-align: center; width: 30px;"><img src="cid:qiandao" width="30" height="30"></div>
                        <h3 class="title" style="padding: 0px 10px 0px 10px; color: white;">GLaDOS CheckIn</h3>
                    </div>
                    <div class="content" style="background-color: #7e766e;">
                        <div class="time" style="padding: 5px; display: flex; color: white; line-height: 20px; font-size: small;"><img src="cid:date" width="20" height="20">%s</div>
                        <div class="message" style="color: white; padding: 10px; background-color: rgb(145,138,129); font-size: small;">
                            <div style="padding-bottom: 10px;">%s</div>
                            <div style="padding-bottom: 10px;">签到分数：%s</div>
                            <div style="padding-bottom: 10px;">目前分数：%s</div>
                            <div style="padding-bottom: 10px;">共 %s 次累计满100分</div>
                        </div>
                    </div>
                    <div class="footer" style="background-color: #7e766e; color: white; padding: 20px;">
                        <div class="author" style="text-align: center;"><img src="cid:e" width="30" height="30" style="vertical-align: -8px"> Make By Elone</div>
                    </div>
                </div>
            </body>
            """ % (data["date"], data["message"], data["checkInPoint"], data["currPoint"], data["100Cnt"])
        message.attach(MIMEText(html, 'html', 'utf-8'))
        message['Subject'] = Header(data["subject"], 'utf-8')
        message['From'] = f'GLaDOS {EMAIL_USER}'
        message['To'] = Header("My lord", 'utf-8')
        receives = [ELONE, EMAIL_USER, MING]
        email_server = smtplib.SMTP()
        email_server.connect(EMAIL_HOST, int(EMAIL_POST))
        email_server.login(EMAIL_USER, EMAIL_PWD)
        email_server.sendmail(EMAIL_USER, receives, message.as_string())


if __name__ == '__main__':
    CheckIn().checkin()
