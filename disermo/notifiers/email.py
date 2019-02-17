"""
Email notifier
"""
from email.mime.text import MIMEText
import smtplib
from typing import TYPE_CHECKING, List, Tuple

from .base import Notifier

if TYPE_CHECKING:
    from ..checks import Check
    from ..node import Node


class Email(Notifier):
    to_addr: str
    from_addr: str

    template_subject = '''[Disermo] {name} => {status}'''
    template_body = '''{summary}'''
    template_body_summary = '''{check}: {status}'''

    def __init__(self, to_addr: str, from_addr: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.to_addr = to_addr
        self.from_addr = from_addr

    def send(self, node: 'Node', checks: 'List[Check]') -> None:
        subject = self.template_subject.format(
            name=node.label,
            status=node.status,
        )

        # Generate full labels
        searching: List[Tuple[Check, List[str]]] = [(node, [node.label])]
        found: List[Tuple[Check, List[str]]] = []
        while searching:
            # Look at next and search its children
            check, label = searching.pop()
            searching.extend([
                (subcheck, label + [subcheck.label])
                for subcheck in check.subchecks
            ])

            # See if we've found one
            if check in checks:
                found.append((check, label))

        # Render summary
        summary = '\n'.join([
            self.template_body_summary.format(
                check=' > '.join(label),
                status=check.status
            )
            for check, label in found
        ])

        body = self.template_body.format(
            summary=summary,
        )

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = self.to_addr
        msg['From'] = self.from_addr

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
