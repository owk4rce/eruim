from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.src.utils.exceptions import ConfigurationError
import logging

logger = logging.getLogger('backend')


def send_test_email(recipient_email):
    """
    Send test email to verify SMTP configuration

    Args:
        recipient_email: Email address to send test message to

    Raises:
        ConfigurationError: If email configuration is invalid
    """
    try:
        # Get email settings from config
        sender_email = current_app.config["APP_SERVICE_EMAIL"]
        sender_password = current_app.config["APP_SERVICE_EMAIL_PASSWORD"]

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Test Email"

        body = "This is a test email sent from your Flask application!"
        message.attach(MIMEText(body, "plain"))

        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            logger.info("Starting SMTP session...")
            server.starttls()
            logger.info("Attempting login...")
            server.login(sender_email, sender_password)
            logger.info("Login successful, sending email...")
            server.send_message(message)
            logger.info("Email sent successfully!")

        return True

    except Exception as e:
        raise ConfigurationError(f"Failed to send email: {str(e)}")


def send_reset_password_email(recipient_email, reset_link):
    """
    Send password reset email with link

    Args:
        recipient_email: User's email address
        reset_link: Password reset link with token

    Raises:
        ConfigurationError: If email configuration is invalid
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