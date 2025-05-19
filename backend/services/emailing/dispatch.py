from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from pydantic import EmailStr
from config.settings import get_settings
from jinja2 import Environment, PackageLoader, select_autoescape
from schemas.enums import EmailTemplate
from services.logging import init_logger
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Union, Optional
from pathlib import Path
import os
import requests


EMAILS_MAP = {
    EmailTemplate.CAMPAIGN_PUBLISHED: {
        "template_name": "campaign_published.html",
        "subject": "Your campaign has been published",
    }
}


class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.logger = init_logger()
        self.env = Environment(
            loader=PackageLoader("services.emailing"),
            autoescape=select_autoescape()
        )

    def render_to_string(self, template_name: str, **kwargs) -> str:
        """Render a template to string using Jinja2."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**kwargs, settings=self.settings)
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise Exception("Failed to render template")

    def _prepare_email_data(self, email_data: dict) -> dict:
        """Prepare common email data."""
        return {
            **email_data,
            "app_name": self.settings.app_name,
            "support_email": self.settings.support_email,
            "current_year": datetime.now().year,
            "dashboard_url": f"{self.settings.frontend_url}/dashboard",
        }

    def _create_mime_message(
        self,
        email_to: Union[List[EmailStr], EmailStr],
        subject: str,
        html_content: str,
        attachments: Optional[List[Path]] = None
    ) -> MIMEMultipart:
        """Create a MIME message with optional attachments."""
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = f"{self.settings.mail_display_name} <{self.settings.mail_username}>"
        msg['To'] = email_to if isinstance(email_to, str) else ", ".join(email_to)

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        # Handle attachments
        if attachments:
            for attachment in attachments:
                try:
                    if os.path.exists(attachment):  # Local file
                        with open(attachment, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
                            msg.attach(part)
                    elif str(attachment).startswith(("http://", "https://")):  # URL
                        response = requests.get(str(attachment), stream=True)
                        if response.status_code == 200:
                            file_name = str(attachment).split("/")[-1]
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(response.content)
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename={file_name}')
                            msg.attach(part)
                        else:
                            self.logger.error(f"Failed to download attachment from URL: {attachment}. Status code: {response.status_code}")
                    else:
                        self.logger.error(f"Attachment {attachment} is neither a valid file path nor a URL, skipping.")
                except Exception as e:
                    self.logger.error(f"Error processing attachment {attachment}: {e}")

        return msg

    async def send_email(
        self,
        email_to: Union[List[EmailStr], EmailStr],
        email_type: EmailTemplate,
        email_data: dict,
        attachments: Optional[List[Path]] = None
    ) -> bool:
        """Send an email using the configured SMTP server."""
        if email_type not in EMAILS_MAP:
            self.logger.error(f"Invalid email type {email_type}")
            raise ValueError(f"Invalid email type {email_type}")

        conf = EMAILS_MAP[email_type]
        email_data = self._prepare_email_data(email_data)

        try:
            with smtplib.SMTP(self.settings.mail_server, self.settings.mail_port) as smtp:
                smtp.starttls()
                smtp.login(self.settings.mail_username, self.settings.mail_password)

                # Render email content
                email_content = self.render_to_string(conf['template_name'], **email_data)

                # Get subject from meta or config
                subject = email_data.get("meta", {}).get("mail_subject", conf['subject'])

                # Create MIME message
                msg = self._create_mime_message(email_to, subject, email_content, attachments)

                # Send email and track failures
                failed_recipients = []
                recipients = [email_to] if isinstance(email_to, str) else email_to
                response = smtp.sendmail(self.settings.mail_username, recipients, msg.as_string())

                # Log results
                for recipient in recipients:
                    if recipient in response:
                        failed_recipients.append(recipient)
                        self.logger.error(f"Failed to send email {email_type} to {recipient}: {response[recipient]}")
                    else:
                        self.logger.info(f"Email {email_type} successfully sent to {recipient}")

                if failed_recipients:
                    self.logger.warning(f"Some emails failed to send: {failed_recipients}")
                    return False

                return True

        except Exception as e:
            self.logger.error(f"Failed to send email {email_type} to {email_to}: {str(e)}")
            return False
