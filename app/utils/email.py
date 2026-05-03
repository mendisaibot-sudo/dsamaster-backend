"""Email utility for sending verification and password reset emails."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
BASE_URL = os.environ.get("FRONTEND_BASE_URL", "https://dsamaster.de")


def _send_email(to_email: str, subject: str, html_body: str):
    """Send an HTML email via SMTP."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError("Email credentials not configured")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"DSAMaster <{EMAIL_ADDRESS}>"
    msg["To"] = to_email

    html_part = MIMEText(html_body, "html")
    msg.attach(html_part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [to_email], msg.as_string())


def _verification_email_html(verification_link: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f97316; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .header h1 {{ color: white; margin: 0; font-size: 24px; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #f97316; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .link {{ word-break: break-all; color: #f97316; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to DSAMaster!</h1>
            </div>
            <div class="content">
                <h2>Verify Your Email</h2>
                <p>Thank you for creating an account. Please click the button below to verify your email address:</p>
                <center><a href="{verification_link}" class="button">Verify Email</a></center>
                <p>Or copy and paste this link into your browser:</p>
                <p class="link">{verification_link}</p>
                <p><strong>This link expires in 48 hours.</strong></p>
            </div>
            <div class="footer">
                <p>If you didn't create this account, please ignore this email.</p>
                <p>&copy; 2025 DSAMaster. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def _password_reset_email_html(reset_link: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f97316; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .header h1 {{ color: white; margin: 0; font-size: 24px; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #f97316; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .link {{ word-break: break-all; color: #f97316; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset</h1>
            </div>
            <div class="content">
                <h2>Reset Your Password</h2>
                <p>You requested a password reset. Click the button below to set a new password:</p>
                <center><a href="{reset_link}" class="button">Reset Password</a></center>
                <p>Or copy and paste this link into your browser:</p>
                <p class="link">{reset_link}</p>
                <p><strong>This link expires in 24 hours.</strong></p>
                <p>If you didn't request this reset, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 DSAMaster. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def send_verification_email(to_email: str, token: str):
    """Send an email verification link."""
    link = f"{BASE_URL}/verify-email?token={token}"
    subject = "Verify Your DSAMaster Account"
    html = _verification_email_html(link)
    _send_email(to_email, subject, html)


def send_password_reset_email(to_email: str, token: str):
    """Send a password reset link."""
    link = f"{BASE_URL}/reset-password?token={token}"
    subject = "Reset Your DSAMaster Password"
    html = _password_reset_email_html(link)
    _send_email(to_email, subject, html)
