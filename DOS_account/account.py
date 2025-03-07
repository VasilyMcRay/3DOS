import asyncio

from curl_cffi.requests import Cookies, Response
from loguru import logger
import twitter

from Request import Request
from mail import Email
from utils.methods import Methods
from utils.utils import is_token_expired, initialise_headers


class Account(Request):
    BASE_URL = 'https://api.dashboard.3dos.io/api/'
    """
    Класс аккаунта.
    """
    def __init__(
            self,
            id: int,
            mail: str,
            password: str,
            mail_password: str,
            twitter_auth: str,
            host: str = 'imap.rambler.ru',
            referral_code: str = 'c8a883',
            proxy: str | None = None,
            headers: dict | None = None,
            cookies: dict | None = None,
            authorization_key: str | None = None,
            api_key: str | None = None,
            is_registered: bool = False,
            is_email_verified: bool = False,
            is_twitter_connected: bool = False,
            sui_wallet: str | None = None,
            total_points: int | None = None,
            is_twitter_locked: bool = False,
    ):
        super().__init__(proxy=proxy, headers=headers, cookies=cookies)
        self.id = id
        if not cookies:
            self.cookies = {}
        if headers:
            self.headers = headers
        else:
            self.headers = initialise_headers()
        if authorization_key:
            if is_token_expired(authorization_key):
                self.authorization_key = ''
            else:
                self.headers['authorization'] = f'Bearer {authorization_key}'
                self.session.headers['authorization'] = f'Bearer {authorization_key}'
                self.authorization_key = authorization_key
        self.mail = mail
        self.mail_password = mail_password
        self.password = password
        self.referral_code = referral_code
        self.email = Email(host=host, mail=self.mail, mail_password=self.mail_password)
        self.tw_account = twitter.Account(auth_token=twitter_auth)
        self.api_key = api_key
        self.is_registered = is_registered
        self.is_email_verified = is_email_verified
        self.is_twitter_connected = is_twitter_connected
        self.sui_wallet = sui_wallet
        self.total_points = total_points
        self.is_twitter_locked = is_twitter_locked

    def __repr__(self):
        return f'''
        id: {self.id}
        mail: {self.mail}
        mail_password: {self.mail_password}
        password: {self.password}
        ref_code: {self.referral_code}
        tw_account: {self.tw_account}
        api_key: {self.api_key}
        is_registered: {self.is_registered}
        is_email_verified: {self.is_email_verified}
        sui_wallet: {self.sui_wallet}
        auth_key: {self.authorization_key}
'''

    async def get_session_cookie(self) -> None:
        """
        Функция добавления особого cookie, необходимого для некоторых запросов.
        :return:
        """
        url = f'{self.BASE_URL}leader-board'
        response = await self.request(Methods.GET, url=url, is_verify_twitter=True)

        cookies: Cookies = response.cookies
        self.cookies["3dosnetwork_session"] = cookies.get("3dosnetwork_session")
        self.session.cookies["3dosnetwork_session"] = cookies.get("3dosnetwork_session")

    async def get_account_info(self) -> dict:
        """
        Функция получения информации об аккаунте.
        :return:
        """
        url = f'{self.BASE_URL}profile/me'
        json_data = {}
        response = await self.request(Methods.POST, url=url, json=json_data)
        if response.get('error') == 'Unauthenticated.':
            await self.login()
            await self.get_account_info()
        else:
            data = response.get('data', {})
            api_key = data.get('api_secret')
            if api_key:
                self.api_key = api_key
            self.total_points = data.get('loyalty_points')
            self.sui_wallet = data.get('sui_address')
            logger.info(f'[{self.mail}] has {self.total_points}')
            return response

    async def register_account(self) -> dict:
        """
        Функция регистрации аккаунта.
        :return:
        """
        url = f'{self.BASE_URL}auth/register'
        json_data = {
            'email': self.mail,
            'password': self.password,
            'acceptTerms': True,
            'country_id': '233',
            'referred_by': self.referral_code,
        }
        # todo: Добавить авторизационный key после регистрации.
        response = await self.request(Methods.POST, url=url, json=json_data)
        if response.get('message') == 'Registration Successful':
            self.is_registered = True
            logger.info(f'[{self.mail}] Registration Successful')
        return response

    async def login(self) -> dict:
        """
        Функция входа в аккаунт.
        :return:
        """
        url = f'{self.BASE_URL}auth/login'
        json_data = {
            'email': self.mail,
            'password': self.password,
        }
        response = await self.request(Methods.POST, url=url, json=json_data)
        if response.get('message') == 'Login Successful':
            logger.info(f'[{self.mail}] Login Successful')
            authorization_key = response.get('data', {}).get('access_token')
            self.authorization_key = authorization_key
            self.session.headers['authorization'] = f'Bearer {authorization_key}'
        return response

    async def claim_daily_reward(self) -> dict:
        """
        Функция получения ежедневной награды.
        :return:
        """
        url = f'{self.BASE_URL}claim-reward'
        json_data = {
            'id': 'daily-reward-api',
        }
        response = await self.request(Methods.POST, url=url, json=json_data)
        if response.get('error') == 'Unauthenticated.':
            await self.login()
            await self.claim_daily_reward()
        elif response.get('flag'):
            logger.info(f'[{self.mail}] Успешно получил ежедневную награду')
        elif response.get('message') == 'Limit reached.':
            logger.info(f'[{self.mail}] You can only claim a reward once every 24 hours.')
        return response

    async def verify_mail(self) -> Response:
        """
        Функция проверки привязки почты.
        :return:
        """
        for _ in range(5):
            url = self.email.get_verify_url()
            if url == 'Не обнаружено нужной ссылки.':
                await asyncio.sleep(10)
            else:
                break

        response = await self.request(Methods.GET, url=url, is_verify_twitter=True)
        if response.status_code == 200:
            self.is_email_verified = True
            logger.info(f'[{self.mail}] Почта успешно подтверждена')
        return response

    async def get_twitter_connect_link(self) -> str:
        """
        Функция получения ссылки для привязки аккаунта твиттер.
        :return:
        """
        url = f'{self.BASE_URL}auth/twitter/connect'
        response = await self.request(Methods.GET, url=url)
        if response.get('error') == 'Unauthenticated.':
            await self.login()
            await self.get_twitter_connect_link()
        link = response.get('data', {}).get('url')
        return link

    async def link_twitter(self) -> tuple[str, str]:
        """
        Привязка твиттер.
        :return:
        """
        connection_link = await self.get_twitter_connect_link()
        connection_link = connection_link.split('&')
        code_challenge = ''
        state = ''
        for param in connection_link:
            param = param.split('=')
            if param[0] == 'state':
                state = param[1]
            elif param[0] == 'code_challenge':
                code_challenge = param[1]
        logger.info(f'state: {state}')
        oauth2_data = {
            'client_id': 'aFF2WUtxb0JWOUp2d01VbFVobGg6MTpjaQ',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'redirect_uri': 'https://api.dashboard.3dos.io/api/auth/twitter/callback',
            'response_type': 'code',
            'scope': 'tweet.read users.read follows.write offline.access',
            'state': state, # HmpN755SAOSeKZ1wMVZbGnEaaRMQOfpxNxnfGQKU kgr0faumzXAzsUIrZaYtBbvYMytsmDaWtMsFw6qi
        }
        try:
            async with twitter.Client(
                    self.tw_account,
                    proxy=self.proxy,
            ) as twitter_client:
                auth_code = await twitter_client.oauth2(**oauth2_data)
        except twitter.errors.AccountLocked:
            self.is_twitter_locked = True
            logger.info(f'[{self.mail}] Twitter {self.tw_account.auth_token} is locked')

        return state, auth_code

    async def verify_twitter(self) -> Response:
        """
        Привязка твиттер к аккаунту.
        :return:
        """
        url = f'{self.BASE_URL}auth/twitter/callback'
        state, auth_code = await self.link_twitter()
        params = {
            'state': state,
            'code': auth_code,
        }
        self.session.headers['upgrade-insecure-requests'] = '1'
        response = await self.request(Methods.GET, url=url, params=params, is_verify_twitter=True)
        self.session.headers.pop('upgrade-insecure-requests')
        if response.status_code == 200:
            self.is_twitter_connected = True
            logger.info(f'[{self.mail}] Twitter успешно привязан.')
        return response

    async def generate_api_key(self) -> dict:
        """
        Функция генерации API ключа для подключения к расширению.
        :return:
        """
        url = f'{self.BASE_URL}profile/generate-api-key'
        json_data = {}
        response = await self.request(Methods.POST, url=url, json=json_data)
        if response.get('error') == 'Unauthenticated.':
            await self.login()
            await self.generate_api_key()
        if response.get('message') == 'Api Key has been generated successfully':
            api_key = response.get('data', {}).get('api_secret')
            self.api_key = api_key
            logger.info(f'[{self.mail}] Успешно получен API ключ {api_key}')
        return response

    async def refresh_extension(self) -> dict:
        """
        Функция обновления расширения(пинг).
        :return:
        """
        url = f'{self.BASE_URL}profile/api/{self.api_key}'
        # sites = [
        #     'https://www.amazon.com/s?k=gaming+headsets&_encoding=UTF8&content-id=amzn1.sym.12129333-2117-4490-9c17-6d31baf0582a&pd_rd_r=c31b0438-437f-43c3-9eaf-be3a6f26d8f6&pd_rd_w=bhWyg&pd_rd_wg=aAvUJ&pf_rd_p=12129333-2117-4490-9c17-6d31baf0582a&pf_rd_r=YA4WCH1KARJ7MPTNC0JC&ref=pd_hp_d_atf_unk',
        #     'https://www.ebay.com/b/Health-Beauty/26395/bn_1865479?_trkparms=parentrq%3A65d293901950a2a70bb3d83effff632e%7Cpageci%3A8530b46e-f9ab-11ef-8166-a267d359f123%7Cc%3A2%7Ciid%3A1%7Cli%3A8874',
        #     'https://group.jumia.com/business',
        # ]
        if not self.cookies.get('3dosnetwork_session'):
            await self.get_session_cookie()
        self.session.headers['origin'] = 'chrome-extension://lpindahibbkakkdjifonckbhopdoaooe'
        response = await self.request(Methods.POST, url=url)
        if response.get('error') == 'Unauthenticated.':
            await self.login()
            await self.refresh_extension()
        return response

    async def make_all_actions(self, sleep_time: int) -> None:
        """
        Функция для прогона всех действия для аккаунта.
        :param sleep_time: Задержка между действиями.
        :return:
        """
        if not self.is_registered:
            await self.register_account()
            await asyncio.sleep(sleep_time)

        if not self.authorization_key and self.is_registered:
            await self.login()
            await asyncio.sleep(sleep_time)

        if not self.is_email_verified:
            await self.verify_mail()
            await asyncio.sleep(sleep_time)

        if not self.is_twitter_connected:
            await self.verify_twitter()
            await asyncio.sleep(sleep_time)

        await self.claim_daily_reward()
        await asyncio.sleep(sleep_time)

        if not self.api_key:
            await self.generate_api_key()
            await asyncio.sleep(sleep_time)

        await self.refresh_extension()
        await asyncio.sleep(sleep_time)
        await self.close_session()
