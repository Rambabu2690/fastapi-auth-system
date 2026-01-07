import smtplib
from email.message import EmailMessage

EMAIL = "rambabu.v@swarnasky.com"
PASSWORD = "bumqsvkjwablixid"

def send_email(to, subject, content):
    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
