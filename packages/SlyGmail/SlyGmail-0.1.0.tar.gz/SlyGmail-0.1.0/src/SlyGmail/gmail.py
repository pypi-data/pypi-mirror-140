from dataclasses import dataclass
import os.path

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from typing import cast

import aiofiles

from SlyAPI import *

class Scope:
    GMail         = 'https://mail.google.com/'
    GMailSend     = 'https://www.googleapis.com/auth/gmail.send'
    GMailReadOnly = 'https://www.googleapis.com/auth/gmail.readonly'

MIME_TYPES = {
    'text': MIMEText,
    'image': MIMEImage,
    'audio': MIMEAudio
}

EMAIL_HEADERS = {'Content-Type': 'message/rfc822'}

@dataclass
class Email:
    to: str
    sender: str
    subject: str
    body: str
    attachments: list[str] # filepath

    async def encoded(self) -> str:

        if not self.attachments:
            message = MIMEText(self.body)
            message['to'] = self.to
            message['from'] = self.sender
            message['subject'] = self.subject
        else:
            message = MIMEMultipart()
            message['to'] = self.to
            message['from'] = self.sender
            message['subject'] = self.subject

            message.attach(MIMEText(self.body))

            for path in self.attachments:
                # convert to MIME object based on path
                content_type, encoding = mimetypes.guess_type(path)
                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'
                main_type, sub_type = content_type.split('/', 1)

                async with aiofiles.open(path, 'rb') as f:
                    if main_type == 'text':
                        msg = MIMEText(str(await f.read(), encoding='utf8'), sub_type)
                    elif main_type in ['image', 'audio']:
                        mime_t = cast(type[MIMEImage] | type[MIMEAudio], MIME_TYPES[main_type])
                        msg = mime_t(await f.read(), sub_type)
                    else:
                        msg = MIMEBase(main_type, sub_type)
                        msg.set_payload(await f.read())
                
                # gmail does not like attaching .zip file names
                filename = os.path.split(path)[1].replace('.zip', '.zip.attachment')

                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(msg)

        return message.as_string()


class Gmail(WebAPI):
    base_url = "https://gmail.googleapis.com/upload/gmail/v1"

    def __init__(self, app: str | OAuth2, user: str | OAuth2User, scope: str):
        if isinstance(user, str):
            user = OAuth2User(user)

        if isinstance(app, str):
            auth = OAuth2(app, user)
        else:
            auth = app
            auth.user = user
        super().__init__(auth)
        auth.verify_scope(scope)

    async def send(self, to: str, subject: str, body: str, attachments: list[str] | None = None, from_email: str='me'):
        if attachments is None:
            attachments = []
        email = Email(to, from_email, subject, body, attachments)
        return await self._users_messages_send(email)

    async def _users_messages_send(self, email: Email):

        data = await email.encoded()

        if email.attachments:
            params = {'uploadType': 'multipart'}
        else:
            params = {}
        
        return await self.post_json(
            F"/users/{email.sender}/messages/send",
            params, data=data, headers=EMAIL_HEADERS
            )

