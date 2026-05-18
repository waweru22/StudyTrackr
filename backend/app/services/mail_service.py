from flask_mail import Message
from flask import render_template_string, current_app
from app import mail
import traceback

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
            print(f"[MAIL] Successfully sent OTP to {to_email}")
            return True
        except Exception as e:
            print(f"[MAIL] FAILED to send OTP to {to_email}")
            print(f"[MAIL] Error type: {type(e).__name__}")
            print(f"[MAIL] Error details: {str(e)}")
            traceback.print_exc()
            raise

    @staticmethod
    def send_verification_email(to_email, verification_link):
        """Sends an email verification link to complete registration."""
        subject = "Verify your StudyTrackr account"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 25px; background-color: #f9fafb; }}
                .btn {{ display: inline-block; background-color: #1e3a8a; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-weight: bold; font-size: 16px; margin: 20px 0; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
                .note {{ font-size: 13px; color: #888; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>StudyTrackr</h2>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Welcome to StudyTrackr! Click the button below to verify your email address and activate your account.</p>

                    <div style="text-align: center;">
                        <a href="{verification_link}" class="btn">Verify My Email</a>
                    </div>

                    <p class="note">This link expires in <strong>24 hours</strong>. If you did not create this account, you can safely ignore this email.</p>
                    <p class="note">If the button above doesn't work, copy and paste this link into your browser:<br><small>{verification_link}</small></p>
                </div>
                <div class="footer">
                    &copy; 2026 StudyTrackr. All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """

        msg = Message(subject, recipients=[to_email])
        msg.html = html_content
        msg.body = f"Verify your StudyTrackr account by visiting this link: {verification_link}\n\nThis link expires in 24 hours."

        try:
            mail.send(msg)
            print(f"[MAIL] Successfully sent verification email to {to_email}")
            return True
        except Exception as e:
            print(f"[MAIL] FAILED to send verification email to {to_email}")
            print(f"[MAIL] Error type: {type(e).__name__}")
            print(f"[MAIL] Error details: {str(e)}")
            traceback.print_exc()
            raise

    @staticmethod
    def send_verification_approved_email(to_email):
        """Sends a notification that the student's account has been verified."""
        subject = "StudyTrackr — Account Verified ✅"
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; }
                .header { background-color: #16a34a; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { padding: 25px; background-color: #f9fafb; }
                .footer { font-size: 12px; color: #666; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h2>Account Verified</h2></div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Your StudyTrackr account has been <strong>verified</strong> by an administrator. You can now access your personalized study schedule and all platform features.</p>
                    <p>Log in to get started!</p>
                </div>
                <div class="footer">&copy; 2026 StudyTrackr. All rights reserved.</div>
            </div>
        </body>
        </html>
        """
        msg = Message(subject, recipients=[to_email])
        msg.html = html_content
        msg.body = "Your StudyTrackr account has been verified. You can now access your study schedule."
        try:
            mail.send(msg)
            print(f"[MAIL] Successfully sent approval email to {to_email}")
            return True
        except Exception as e:
            print(f"[MAIL] FAILED to send approval email to {to_email}")
            print(f"[MAIL] Error type: {type(e).__name__}")
            print(f"[MAIL] Error details: {str(e)}")
            traceback.print_exc()
            raise

    @staticmethod
    def send_broadcast_email(to_email, title, message_body):
        """Sends an admin broadcast notification email."""
        subject = f"StudyTrackr — {title}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 25px; background-color: #f9fafb; }}
                .message-box {{ background: #fff; border-left: 4px solid #1e3a8a; padding: 15px; margin: 15px 0; border-radius: 4px; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h2>StudyTrackr Announcement</h2></div>
                <div class="content">
                    <h3>{title}</h3>
                    <div class="message-box">{message_body}</div>
                </div>
                <div class="footer">&copy; 2026 StudyTrackr. All rights reserved.</div>
            </div>
        </body>
        </html>
        """
        msg = Message(subject, recipients=[to_email])
        msg.html = html_content
        msg.body = f"{title}\n\n{message_body}"
        try:
            mail.send(msg)
            print(f"[MAIL] Successfully sent broadcast to {to_email}")
            return True
        except Exception as e:
            print(f"[MAIL] FAILED to send broadcast to {to_email}")
            print(f"[MAIL] Error type: {type(e).__name__}")
            print(f"[MAIL] Error details: {str(e)}")
            traceback.print_exc()
            raise
