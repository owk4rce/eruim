from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.src.utils.exceptions import ConfigurationError
import logging

logger = logging.getLogger('backend')


def send_reset_password_email(recipient_email, reset_link):
    """
    Send password reset email with reset link.

    Sends HTML email using Gmail SMTP with service account credentials.
    Message includes a password reset link that expires in 2 hours.
    """
    try:
        # Get email settings from config
        sender_email = current_app.config["APP_SERVICE_EMAIL"]
        sender_password = current_app.config["APP_SERVICE_EMAIL_PASSWORD"]

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Password Reset Request"

        body = f"""
        You have requested to reset your password.

        Please click the following link to reset your password:
        {reset_link}

        If you did not request this password reset, please ignore this email.

        This link will expire in 2 hours.
        """

        message.attach(MIMEText(body, "plain"))

        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            logger.info("Starting SMTP session...")
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            logger.info(f"Reset password email sent to {recipient_email}")

        return True

    except Exception as e:
        raise ConfigurationError(f"Failed to send email: {str(e)}")


def send_account_activation_email(recipient_email, activation_link):
    """
    Send account activation email with confirmation link.

    Sends HTML email using Gmail SMTP with service account credentials.
    Message includes an activation link that expires in 48 hours.
    Account will be deleted if not activated within this time.
    """
    try:
        # Get email settings from config
        sender_email = current_app.config["APP_SERVICE_EMAIL"]
        sender_password = current_app.config["APP_SERVICE_EMAIL_PASSWORD"]

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Account activation"

        body = f"""
        Somebody, probably you, entered this email address during the registration.

        If it was you, please click the following link to activate your account:
        {activation_link}

        Otherwise, please ignore this email.

        This link will expire in 48 hours. After that the account associated with this email will be deleted.
        """

        message.attach(MIMEText(body, "plain"))

        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            logger.info("Starting SMTP session...")
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            logger.info(f"Activation email sent to {recipient_email}")

        return True

    except Exception as e:
        raise ConfigurationError(f"Failed to send email: {str(e)}")
