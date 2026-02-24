from flask_mail import Message
from flask import render_template_string, current_app
from app import mail


def send_email(to, subject, body, html=None):
    """Simple helper used by various services for generic messages."""
    msg = Message(subject, recipients=[to])
    msg.body = body
    if html:
        msg.html = html

    try:
        mail.send(msg)
        return True
    except Exception as e:
        # In production replace prints with proper logging
        print(f"Failed to send email to {to}: {e}")
        return False


class MailService:
    @staticmethod
    def send_otp_email(to_email, otp):
        """
        Sends an OTP verification email using a professional HTML template.
        """
        subject = "StudyTrackr Verification Code"
        
        # Professional/Academic HTML Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 25px; background-color: #f9fafb; }}
                .otp-box {{ background-color: #ffffff; border: 2px dashed #1e3a8a; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e3a8a; margin: 20px 0; border-radius: 4px; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>StudyTrackr</h2>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Referencing your request for account verification, please use the One-Time Password (OTP) below to complete your registration.</p>
                    
                    <div class="otp-box">
                        {otp}
                    </div>
                    
                    <p><strong>Note:</strong> This code is valid for <strong>5 minutes</strong>. If you did not request this code, please ignore this email.</p>
                    <p>Secure your academic journey.</p>
                </div>
                <div class="footer">
                    &copy; 2026 StudyTrackr. All rights reserved.<br>
                    Automated Security Notification.
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(subject, recipients=[to_email])
        msg.html = html_content
        msg.body = f"Your Verification Code is: {otp}. Valid for 5 minutes." # Fallback
        
        try:
            mail.send(msg)
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            # In prod, log this properly
            return False
