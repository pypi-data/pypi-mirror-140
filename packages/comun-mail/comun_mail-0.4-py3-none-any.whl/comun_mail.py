import smtplib
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

FROM = 'envios@ubesol.es'


def send_mail(server, mensaje, asunto, to, file_path=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = FROM
        msg['To'] = ", ".join(to)

        msg.attach(MIMEText(mensaje))

        if file_path:
            if isinstance(file_path, list):
                for file in file_path:
                    if os.path.isfile(file):
                        with open(file, "rb") as fil:
                            part = MIMEApplication(
                                fil.read(),
                                Name=basename(file)
                            )
                        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
                        msg.attach(part)
            else:
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as fil:
                        part = MIMEApplication(
                            fil.read(),
                            Name=basename(file_path)
                        )
                    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_path)
                    msg.attach(part)

        server = smtplib.SMTP(server)
        server.sendmail(FROM, to, msg.as_string())
        server.quit()
        print('EMAIL SEND.')
    except Exception as e:
        print('Email failed to send')
        print(repr(e))
