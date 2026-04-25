"""
OTP Service
===========
Handles OTP generation and verification.
"""
from datetime import datetime, timedelta
from flask import current_app
from app.database import db
from app.models import OTP, User
from app.utils.helpers import generate_otp
from app.services.email_service import EmailService


class OTPService:
    """Service for OTP operations."""
    
    @staticmethod
    def generate_and_send_otp(user: User, purpose: str = "verification") -> tuple:
        """
        Generate and send OTP to user.
        
        Args:
            user: User object
            purpose: Purpose of OTP
            
        Returns:
            Tuple of (success, otp_object_or_error_message)
        """
        try:
            # Invalidate previous unused OTPs
            OTP.query.filter_by(user_id=user.id, is_used=False).update({'is_used': True})
            
            # Generate new OTP
            otp_length = current_app.config.get('OTP_LENGTH', 6)
            expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
            
            otp_code = generate_otp(otp_length)
            expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
            
            # Create OTP record
            otp = OTP(
                user_id=user.id,
                otp_code=otp_code,
                expires_at=expires_at
            )
            db.session.add(otp)
            db.session.commit()
            
            # Send OTP via email
            EmailService.send_otp_email(user.email, otp_code, purpose)
            
            return True, otp
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def verify_otp(user_id: int, otp_code: str) -> tuple:
        """
        Verify an OTP code.
        
        Args:
            user_id: User's ID
            otp_code: OTP code to verify
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Find the OTP
            otp = OTP.query.filter_by(
                user_id=user_id,
                otp_code=otp_code,
                is_used=False
            ).first()
            
            if not otp:
                return False, "Invalid OTP code"
            
            if not otp.is_valid():
                return False, "OTP has expired"
            
            # Mark as used
            otp.mark_used()
            db.session.commit()
            
            return True, "OTP verified successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def resend_otp(user: User, purpose: str = "verification") -> tuple:
        """
        Resend OTP to user.
        
        Args:
            user: User object
            purpose: Purpose of OTP
            
        Returns:
            Tuple of (success, message)
        """
        # Check rate limiting (prevent spam)
        last_otp = OTP.query.filter_by(user_id=user.id).order_by(OTP.created_at.desc()).first()
        
        if last_otp:
            time_diff = datetime.utcnow() - last_otp.created_at
            if time_diff.total_seconds() < 60:  # 1 minute cooldown
                return False, "Please wait before requesting a new OTP"
        
        return OTPService.generate_and_send_otp(user, purpose)
