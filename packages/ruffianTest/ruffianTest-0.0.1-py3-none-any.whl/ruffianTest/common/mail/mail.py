import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMail:
    def __init__(self, server, port, email, password):
        self.smtp = smtplib.SMTP()
        self.smtp.connect(server, port)
        self.smtp.login(email, password)

    def send_mail(self, file, form_mail, to_mail, filename, subject, body):  # filename 不要用中文
        """
        :param file: 文件
        :param form_mail: The address sending this mail.
        :param to_mail: A list of addresses to send this mail to.A bare string will be treated as a list with 1 address.
        :param filename: Attachment name
        :param subject:
        :param body:
        :return:
        """

        sendfile = open(file, 'rb').read()
        att = MIMEText(sendfile, 'base64', 'utf-8')
        att['Content-Type'] = 'application/octet-stream'
        att['Content-Disposition'] = 'attachment; filename= ' + filename  # 附件名称
        msg = MIMEMultipart()
        msg['Subject'] = subject  # '主题'
        msg.attach(MIMEText(body))  # 正文
        msg.attach(att)  # 附件
        try:
            self.smtp.sendmail(form_mail, to_mail, msg.as_string())  # 参数 1: 发送的邮箱， 2 接收的邮箱
            self.smtp.quit()
            print('邮件发送成功')
        except smtplib.SMTPException:
            self.smtp.quit()
            print('邮件发送失败')


"""
    mail = SendMail('smtp.163.com', 25, 'mail', 'password')
    file1 = os.path.join('/a/b/c', 'd.xls')
    mail.send_mail(file1, 'from_mail', 'to_mail', 'd.xls', '主题', '正文')
"""
