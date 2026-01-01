from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import json
from app.core.email_service import email_service
from app.models.user import User
from app.api.v1.deps import get_current_active_user

router = APIRouter(prefix="/emails", tags=["Emails"])

class EmailRequest(BaseModel):
    to_emails: List[str]
    subject: str
    body: str
    html_body: Optional[str] = None

class EmailResponse(BaseModel):
    success: bool
    message: str

@router.post("/", response_model=EmailResponse)
async def send_email(
    email_request: EmailRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send an email
    """
    result = email_service.send_email(
        to_emails=email_request.to_emails,
        subject=email_request.subject,
        body=email_request.body,
        html_body=email_request.html_body
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return EmailResponse(**result)

@router.post("/form-data", response_model=EmailResponse)
async def send_email_form_data(
    to_emails: List[str] = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    html_body: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send an email using form data
    """
    result = email_service.send_email(
        to_emails=to_emails,
        subject=subject,
        body=body,
        html_body=html_body
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return EmailResponse(**result)

@router.post("/with-attachment", response_model=EmailResponse)
async def send_email_with_attachment(
    current_user: User = Depends(get_current_active_user),
    to_emails_str: str = Form(..., alias='to_emails'),
    subject: str = Form(...),
    body: str = Form(...),
    html_body: Optional[str] = Form(None),
    attachment: UploadFile = File(None)
):
    """
    Send an email with an attachment
    
    NOTE: This endpoint does not require LinkedIn credentials.
    Only a valid application authentication token is needed.
    """
    attachment_paths = []
    original_filenames = []
    
    try:
        # Parse the JSON string to get the list of emails
        to_emails = json.loads(to_emails_str)
        
        # Save attachment to temporary file if provided
        if attachment and attachment.filename:
            original_filenames.append(attachment.filename)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(await attachment.read())
                attachment_paths.append(tmp_file.name)
        
        result = email_service.send_email(
            to_emails=to_emails,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=attachment_paths,
            original_filenames=original_filenames
        )
        
        # Clean up temporary files immediately after sending
        for path in attachment_paths:
            if os.path.exists(path):
                os.unlink(path)
        
        return EmailResponse(**result)
        
    except json.JSONDecodeError as e:
        # Clean up temporary files in case of error
        for path in attachment_paths:
            if os.path.exists(path):
                os.unlink(path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON in to_emails field: {str(e)}"
        )
    except Exception as e:
        # Clean up temporary files in case of error
        for path in attachment_paths:
            if os.path.exists(path):
                os.unlink(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )