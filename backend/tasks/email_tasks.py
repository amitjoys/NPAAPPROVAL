from tasks.celery_app import celery_app
from core.config import settings
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_email_async(
        to_email: str,
        subject: str,
        body: str,
        attachment_path: str = None
    ):
        """Send email asynchronously"""
        try:
            message = MIMEMultipart()
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "html"))
            
            # Add attachment if provided
            if attachment_path:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment_path.split('/')[-1]}",
                    )
                    message.attach(part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_USERNAME,
                password=settings.EMAIL_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"Email sent to: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

@celery_app.task(name="tasks.send_approval_notification")
def send_approval_notification(nfa_id: str, approver_email: str, approver_name: str, nfa_details: dict):
    """Send approval notification email"""
    subject = f"NFA Approval Required - {nfa_details.get('subject', 'N/A')}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>NFA Approval Request</h2>
        <p>Dear {approver_name},</p>
        <p>You have a new NFA approval request:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">NFA ID:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Requestor:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_details.get('requestor_name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Department:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_details.get('department', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Amount:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_details.get('currency', 'INR')} {nfa_details.get('amount', 0):,.2f}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Subject:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_details.get('subject', 'N/A')}</td>
            </tr>
        </table>
        <p style="margin-top: 20px;">
            <a href="https://docuauto.preview.emergentagent.com/approvals/{nfa_id}" 
               style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                Review & Approve
            </a>
        </p>
        <p style="color: #666; margin-top: 20px;">Please review and take action at your earliest convenience.</p>
        <hr style="margin-top: 30px;">
        <p style="color: #999; font-size: 12px;">This is an automated email from HCIL NFA Automation System.</p>
    </body>
    </html>
    """
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(EmailService.send_email_async(approver_email, subject, body))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in send_approval_notification: {e}")
        return False

@celery_app.task(name="tasks.send_coordinator_notification")
def send_coordinator_notification(nfa_id: str, coordinator_email: str):
    """Send notification to coordinator after Section 1 approval"""
    subject = f"NFA Ready for Section 2 Processing - {nfa_id}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>NFA Section 2 Processing Required</h2>
        <p>Dear Coordinator,</p>
        <p>Section 1 approvals are complete for NFA: <strong>{nfa_id}</strong></p>
        <p>Please proceed with vendor selection and Section 2 processing.</p>
        <p style="margin-top: 20px;">
            <a href="https://docuauto.preview.emergentagent.com/coordinator/{nfa_id}" 
               style="background-color: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                Process Section 2
            </a>
        </p>
        <hr style="margin-top: 30px;">
        <p style="color: #999; font-size: 12px;">This is an automated email from HCIL NFA Automation System.</p>
    </body>
    </html>
    """
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(EmailService.send_email_async(coordinator_email, subject, body))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in send_coordinator_notification: {e}")
        return False

@celery_app.task(name="tasks.send_final_nfa_notification")
def send_final_nfa_notification(nfa_id: str, requestor_email: str, nfa_number: str, pdf_path: str = None):
    """Send final NFA notification with PDF"""
    subject = f"NFA Approved - {nfa_number}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>NFA Approval Complete</h2>
        <p>Dear User,</p>
        <p>Your NFA request has been <strong style="color: green;">APPROVED</strong>.</p>
        <table style="border-collapse: collapse; margin-top: 20px;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">NFA Number:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_number}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">NFA ID:</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{nfa_id}</td>
            </tr>
        </table>
        <p style="margin-top: 20px;">Please find the approved NFA document attached.</p>
        <hr style="margin-top: 30px;">
        <p style="color: #999; font-size: 12px;">This is an automated email from HCIL NFA Automation System.</p>
    </body>
    </html>
    """
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            EmailService.send_email_async(requestor_email, subject, body, pdf_path)
        )
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in send_final_nfa_notification: {e}")
        return False
