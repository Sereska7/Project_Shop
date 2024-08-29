import smtplib
from email.message import EmailMessage

from pydantic import EmailStr

from app.config import settings
from app.tasks.conf_celery import celery_app


def create_order_confirmation_template(
    order: dict,
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USERNAME
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Вы совершили покупку в нашем магазине</h1>
            Общая сумма: {order["total_price"]}
            Способ оплаты: {order["payment_method"]}
            Статус оплаты: {order["status"]}            
        """,
        subtype="html",
    )
    return email


@celery_app.task
def send_order_confirmation_email(
    order: dict,
    email_to: EmailStr,
):
    msg_content = create_order_confirmation_template(order, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg_content)
