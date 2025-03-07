from curl_cffi.requests import AsyncSession, Response

from utils.utils import format_proxy
from utils.methods import Methods

class Request:
    """
    Базовый класс для создания сессий.
    """
    def __init__(self, proxy: str | None, headers: dict | None = None, cookies: dict | None = None):
        if proxy:
            self.proxy = format_proxy(proxy)
        else:
            self.proxy = proxy
        if cookies is None:
            self.cookies = {}
        else:
            self.cookies = cookies
        self.headers = headers
        self.session = AsyncSession(proxy=self.proxy, headers=self.headers, cookies=self.cookies)

    async def close_session(self):
        """
        Закрытие сессии.
        :return:
        """
        await self.session.close()

    async def request(self, method: str, url: str, is_verify_twitter: bool = False, **kwargs, ) -> dict | Response:
        """
        Функция инициализации базового запроса.
        :return:
        """
        params = kwargs.pop('params', None)
        json_data = kwargs.pop('json', None)

        if method.upper() == Methods.GET:
            response = await self.session.get(url=url, params=params, timeout=15)
            if is_verify_twitter:
                return response
            return response.json()

        elif method.upper() == Methods.POST:
            response = await self.session.post(url=url, json=json_data, timeout=15)
            return response.json()
