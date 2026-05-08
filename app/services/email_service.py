"""
Email Service
=============
Handles all email sending functionality.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app, render_template_string
from typing import Optional, List


class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    def send_email(
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER')
            msg['To'] = to
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect and send
            server = smtplib.SMTP(
                current_app.config.get('MAIL_SERVER'),
                current_app.config.get('MAIL_PORT')
            )
            server.starttls()
            server.login(
                current_app.config.get('MAIL_USERNAME'),
                current_app.config.get('MAIL_PASSWORD')
            )
            server.sendmail(
                current_app.config.get('MAIL_USERNAME'),
                [to],
                msg.as_string()
            )
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email send error: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_email(to: str, otp_code: str, purpose: str = "verification") -> bool:
        """
        Send OTP verification email.
        
        Args:
            to: Recipient email
            otp_code: OTP code
            purpose: Purpose of OTP (verification, password_reset, etc.)
            
        Returns:
            True if sent successfully
        """
        subject = f"Torida - Your {purpose.replace('_', ' ').title()} Code"
        
        body = f"""
Your {purpose.replace('_', ' ')} code is: {otp_code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
The Torida Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; letter-spacing: 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TORIDA</h1>
                    <p>B2B Marketplace</p>
                </div>
                <div class="content">
                    <h2>{purpose.replace('_', ' ').title()}</h2>
                    <p>Hello,</p>
                    <p>Please use the following code to complete your {purpose.replace('_', ' ')}:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p style="text-align: center; color: #666;">This code will expire in 10 minutes.</p>
                    <div class="warning">
                        <p style="margin: 0;"><strong>Security Notice:</strong> If you did not request this code, please ignore this email. Never share this code with anyone.</p>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2024 Torida. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to, subject, body, html_body)
    
    @staticmethod
    def send_welcome_email(to: str, name: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            to: Recipient email
            name: User's name
            
        Returns:
            True if sent successfully
        """
        subject = "Welcome to Torida!"
        
        body = f"""
Hello {name},

Welcome to Torida, Egypt's premier B2B marketplace!

Your account has been successfully created. You can now start exploring our platform.

Here's what you can do:
- Browse products from verified suppliers
- Connect with suppliers and companies
- Place orders and track deliveries
- Manage your business profile

Get started by completing your profile and exploring our product catalog.

Best regards,
The Torida Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to TORIDA!</h1>
                </div>
                <div class="content">
                    <h2>Hello, {name}!</h2>

                    <p>Welcome to Torida, Egypt's premier B2B marketplace!</p>
                    <p>Your account has been successfully created. Here's what you can do:</p>
                    <div class="feature">📦 Browse products from verified suppliers</div>
                    <div class="feature">🤝 Connect with suppliers and companies</div>
                    <div class="feature">🚚 Place orders and track deliveries</div>
                    <div class="feature">💼 Manage your business profile</div>
                </div>
                <div class="footer">
                    <p>© 2026 Torida. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to, subject, body, html_body)
    
    @staticmethod
    def send_password_reset_email(to: str, reset_link: str, name: str = None) -> bool:
        """
        Send password reset email.
        
        Args:
            to: Recipient email
            reset_link: Password reset link
            name: User's name (optional)
            
        Returns:
            True if sent successfully
        """
        subject = "Torida - Reset Your Password"
        
        body = f"""
Hello {name or 'User'},

You have requested to reset your password.

Click the following link to reset your password:
{reset_link}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
The Torida Team
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TORIDA</h1>
                    <p>Password Reset</p>
                </div>
                <div class="content">
                    <h2>Hello, {name or 'User'}!</h2>
                    <p>You have requested to reset your password.</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p style="color: #666;">Or copy this link to your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    <p style="color: #999; font-size: 14px;">This link will expire in 1 hour.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Torida. All rights reserved.</p>
                    <p>If you did not request this, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to, subject, body, html_body)
    
    @staticmethod
    def send_order_confirmation_email(to: str, order, name: str = None) -> bool:
        """
        Send order confirmation email.
        
        Args:
            to: Recipient email
            order: Order object
            name: User's name
            
        Returns:
            True if sent successfully
        """
        subject = f"Torida - Order #{order.id} Confirmed"
        
        items_html = ""
        for item in order.items:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.product.product_name if item.product else 'N/A'}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">EGP {float(item.price):.2f}</td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #667eea; color: white; padding: 10px; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmed!</h1>
                </div>
                <div class="content">
                    <h2>Hello, {name or 'Customer'}!</h2>
                    <p>Your order has been confirmed and is being processed.</p>
                    <h3>Order #{order.id}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th style="text-align: center;">Qty</th>
                                <th style="text-align: right;">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    <div class="total">Total: EGP {float(order.total_price):.2f}</div>
                </div>
                <div class="footer">
                    <p>© 2024 Torida. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(to, subject, "", html_body)
