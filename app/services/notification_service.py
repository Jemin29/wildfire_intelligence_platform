from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Iterable, List


@dataclass
class EmailNotifier:
    host: str
    port: int
    username: str
    password: str
    sender: str
    use_tls: bool

    def send(self, recipients: Iterable[str], subject: str, body: str) -> None:
        if not self.host or not self.sender:
            raise ValueError("SMTP host and sender must be configured")

        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            if self.use_tls:
                smtp.starttls()
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(message)


@dataclass
class SmsGateway:
    provider: str
    sender: str

    @property
    def enabled(self) -> bool:
        return bool(self.provider and self.sender)

    def queue(self, recipients: Iterable[str], message: str) -> None:
        _ = recipients
        _ = message
        if not self.enabled:
            return
        # TODO: Integrate SMS provider (Twilio, AWS SNS, etc.).
