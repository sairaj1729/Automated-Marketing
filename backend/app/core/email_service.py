import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes
from typing import List, Optional
from app.config.settings import settings

class EmailService:
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.use_tls = settings.EMAIL_USE_TLS
        self.default_from = settings.DEFAULT_FROM_EMAIL
    
    def send_email(
        self, 
        to_emails: List[str], 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        original_filenames: Optional[List[str]] = None
    ):
        """
        Send an email with optional HTML body and attachments
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            attachments: Optional list of file paths to attach
            original_filenames: Optional list of original filenames for attachments
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.default_from
            message["To"] = ", ".join(to_emails)
            
            # Create text and HTML parts
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for i, file_path in enumerate(attachments):
                    if os.path.isfile(file_path):
                        # Determine MIME type based on file extension
                        mime_type, _ = mimetypes.guess_type(file_path)
                        if mime_type is None:
                            mime_type = 'application/octet-stream'
                        
                        # Split MIME type into main type and subtype
                        main_type, sub_type = mime_type.split('/', 1)
                        
                        # Get original filename - either from the parameter or from the file path
                        if original_filenames and i < len(original_filenames) and original_filenames[i]:
                            original_filename = original_filenames[i]
                        else:
                            original_filename = os.path.basename(file_path)
                        
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase(main_type, sub_type)
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {original_filename}'
                        )
                        message.attach(part)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.sendmail(self.default_from, to_emails, message.as_string())
            
            return {"success": True, "message": "Email sent successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to send email: {str(e)}"}

# Global instance
email_service = EmailService()