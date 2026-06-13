import smtplib
from email.mime.text import MIMEText
from src.config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

def send_email(subject, body):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("Notificaciones por email no configuradas, saltando.")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"Email enviado: {subject}")
    except Exception as e:
        print(f"Error enviando email: {e}")

def notify_trade(trade):
    modo = trade["mode"]
    subject = f"[Bot DCA] Compra ejecutada ({modo})"
    body = (
        f"Modo: {modo}\n"
        f"Fecha: {trade['timestamp']}\n"
        f"Precio BTC: ${trade['price']:,.2f}\n"
        f"USDT gastados: ${trade['usdt_spent']:.2f}\n"
        f"BTC comprados: {trade['btc_bought']:.8f}\n"
    )
    send_email(subject, body)
