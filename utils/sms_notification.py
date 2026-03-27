from twilio.rest import Client
import os
import logging


def send_sms_notification(opponent: str = "", game_datetime: str = ""):
    """
    Sends an SMS confirming the check-in was successful.
    Requires the following environment variables:
        TWILIO_ACCOUNT_SID  — found at twilio.com/console
        TWILIO_AUTH_TOKEN   — found at twilio.com/console
        TWILIO_FROM_NUMBER  — Twilio phone number (e.g. +1415XXXXXXX)
        TWILIO_TO_NUMBER    — your verified phone number (e.g. +5541XXXXXXXXX)
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    to_number = os.environ.get("TWILIO_TO_NUMBER")

    client = Client(account_sid, auth_token)

    body = f"Check-in realizado para o próximo jogo. Coritiba x {opponent} {game_datetime}"

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to_number
    )

    logging.info(f"SMS de confirmação enviado com sucesso! SID: {message.sid}")
