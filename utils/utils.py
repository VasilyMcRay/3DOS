import random

import jwt

from datetime import datetime

from fake_useragent import FakeUserAgent


def format_proxy(proxy: str, protocol: str = 'http') -> str:
    """
    Функция для форматирования прокси в http или socks5.

    Args:
        proxy (str): Прокси в любом формате (ip:port, username:password@ip:port и т.д.).
        protocol (str): Требуемый протокол ('http' или 'socks5').

    Returns:
        str: Прокси в формате protocol://username:password@ip:port.

    Raises:
        ValueError: Если формат прокси неверен или если указан неподдерживаемый протокол.
    """
    # Поддерживаемые протоколы
    supported_protocols = ['http', 'socks5']
    if protocol not in supported_protocols:
        raise ValueError(f"Unsupported protocol: {protocol}. Supported protocols are: {', '.join(supported_protocols)}")

    # Разделим прокси на компоненты
    try:
        if '@' in proxy:  # Если есть логин и пароль
            auth, endpoint = proxy.split('@')
            username, password = auth.split(':')
        else:  # Если логина и пароля нет
            username = password = None
            endpoint = proxy

        # Разделяем IP и порт
        ip, port = endpoint.split(':')
    except ValueError:
        raise ValueError(f"Invalid proxy format: {proxy}. Expected formats: ip:port, username:password@ip:port.")

    # Формируем строку
    if username and password:
        formatted_proxy = f"{protocol}://{username}:{password}@{ip}:{port}"
    else:
        formatted_proxy = f"{protocol}://{ip}:{port}"

    return formatted_proxy


def is_token_expired(token: str):
    """
    Проверка на время жизни авторизационного токена.
    :param token:
    :return:
    """
    try:
        # Декодируем токен без проверки подписи
        payload = jwt.decode(token, options={"verify_signature": False})

        # Получаем текущее время в секундах
        current_time = datetime.utcnow().timestamp()

        # Проверяем время истечения токена
        if payload['exp'] < current_time:
            return True  # Токен истек
        # else:
        #     return payload  # Возвращаем полезную нагрузку токена, если он действителен
    except jwt.ExpiredSignatureError:
        return None  # Токен истек (в случае проверки подписи)

    except jwt.DecodeError:
        print("Ошибка декодирования токена")
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

def initialise_headers() -> dict:
    oses = ['Linux', 'Windows', 'Macintosh']
    agent = FakeUserAgent(os=random.choice(oses)).chrome

    # Пример: извлечение информации из user-agent
    if "Mobile" in agent:
        sec_ch_ua_mobile = '?1'
    else:
        sec_ch_ua_mobile = '?0'

    if "Windows" in agent:
        sec_ch_ua_platform = '"Windows"'
    elif "Macintosh" in agent:
        sec_ch_ua_platform = '"Mac OS"'
    elif "Linux" in agent:
        sec_ch_ua_platform = '"Linux"'
    else:
        sec_ch_ua_platform = '"Other"'

    # Образец для sec-ch-ua с использованием версий браузера
    sec_ch_ua = f'"Chromium";v="{agent.split("/")[1].split(" ")[0]}", "Google Chrome";v="{agent.split("/")[1].split(" ")[0]}", "Not A(Brand";v="99"'

    headers = {
        'accept': 'application/json, text/plain, */*',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://dashboard.3dos.io',
        'referer': 'https://dashboard.3dos.io/',
        'sec-ch-ua': sec_ch_ua,
        'sec-ch-ua-mobile': sec_ch_ua_mobile,
        'sec-ch-ua-platform': sec_ch_ua_platform,
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': agent,
    }
    return headers
