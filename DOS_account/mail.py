import imaplib
import email
from bs4 import BeautifulSoup

class Email:
    """
    Класс для работы с почтой.
    """
    def __init__(self, mail: str, mail_password: str, host: str = 'imap.rambler.ru'):
        self.mail = mail
        self.mail_password = mail_password
        if 'rambler' in mail:
            self.host = 'imap.rambler.ru'
        elif 'firstmail' in mail:
            self.host = 'imap.firstmail.ltd:993'

    def get_verify_url(self):
        """
        Функция получения ссылки из письма для верификации аккаунта.
        :return:
        """
        mail = imaplib.IMAP4_SSL(self.host)
        mail.login(self.mail, self.mail_password)

        mail.select("INBOX")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        for e_id in email_ids[-5:]:
            res, msg = mail.fetch(e_id, "(RFC822)")
            msg = email.message_from_bytes(msg[0][1])

            links = []

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        links = [a['href'] for a in soup.find_all('a', href=True)]

            if links:
                for link in links:
                    if 'api.dashboard' in link:
                        return link

        return 'Не обнаружено нужной ссылки.'
