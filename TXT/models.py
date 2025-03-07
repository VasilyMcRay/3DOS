from dataclasses import dataclass


@dataclass
class AccountTXT:
    """
    TXT модель аккаунта.
    """
    header = ['mail', 'mail_password', 'password', 'twitter_auth', 'proxy', 'authorization_key', 'private_key', 'referral_code', 'api_key']
    def __init__(
            self,
            mail: str,
            mail_password: str,
            password: str,
            twitter_auth: str,
            proxy: str = '',
            authorization_key: str = '',
            referral_code: str = '',
            api_key: str = '',
    ):
        self.mail = mail
        self.mail_password = mail_password
        self.password = password
        self.twitter_auth = twitter_auth
        self.proxy = proxy
        self.authorization_key = authorization_key
        self.referral_code = referral_code
        self.api_key = api_key

    def __repr__(self):
        return f'{self.mail}'