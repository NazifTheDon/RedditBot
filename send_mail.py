import smtplib, ssl
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_email(subject, body, file):
    sender_email = "testadennaaccen@gmail.com"
    receiver_email = "nazif.kadiroglu1@gmail.com"

    content = f"""
        {body}
        """
    msg = MIMEMultipart()


    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    body = MIMEText(content, "plain")
    msg.attach(body)

    filename = file
    with open(filename, "r", encoding="utf8") as f:
        attachment = MIMEApplication(f.read(), Name=basename(filename))
        attachment["Content-Dispositiob"] = 'attachment; filename="{}"'.format(basename(filename))
    msg.attach(attachment)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, "etafpuxedtlpknug")
        server.send_message(msg, from_addr=sender_email, to_addrs=[receiver_email])
