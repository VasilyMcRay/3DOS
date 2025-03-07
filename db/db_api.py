import json

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from DOS_account.account import Account
from db.models import AccountModel


class DB:
    def __init__(self, db_url: str = 'sqlite:///db.db'):
        """
        Инициализация менеджера аккаунтов.

        Args:
            db_url (str): URL базы данных.
        """
        self.db_url = db_url

    def load_accounts(self) -> list[AccountModel] | None:
        """
        Выгрузка всех аккаунтов из БД.

        Returns:
            list[AccountModel] | None: Список объектов AccountModel или None, если аккаунтов нет.
        """
        try:
            self._create_session()
            accounts: list[AccountModel] = self.session.query(AccountModel).all()
            if accounts:
                return accounts
            else:
                logger.info("Нет зарегистрированных аккаунтов.")
                return None
        except Exception as e:
            logger.error(f"Произошла ошибка при загрузке аккаунтов: {e}")
            return None
        finally:
            self._close_session()

    def create_worked_accounts(self) -> list[Account]:
        """
        Создание DOS аккаунтов из БД.
        :return:
        """
        db_accounts = self.load_accounts()
        accounts = []
        if db_accounts:
            try:
                for db_account in db_accounts:
                    if not db_account.cookies:
                        db_account.cookies = "{}"
                    account = Account(
                        id=db_account.id,
                        mail=db_account.mail,
                        password=db_account.password,
                        mail_password=db_account.mail_password,
                        twitter_auth=db_account.twitter_auth,
                        proxy=db_account.proxy,
                        authorization_key=db_account.authorization_key,
                        api_key=db_account.api_key,
                        is_registered=db_account.is_registered,
                        is_email_verified=db_account.is_email_verified,
                        is_twitter_connected=db_account.is_twitter_connected,
                        is_twitter_locked=db_account.is_twitter_locked,
                        headers=json.loads(db_account.headers),
                        sui_wallet=db_account.sui_wallet,
                        total_points=db_account.total_points,
                        cookies=json.loads(db_account.cookies),
                    )
                    accounts.append(account)
            except Exception as e:
                logger.error(f"Произошла ошибка при загрузке аккаунтов: {e}")
        return accounts

    def update_account_info(self, accounts: list[Account]) -> None:
        """
        Обновление информации об аккаунте в БД.
        :param accounts:
        :return:
        """
        self._create_session()
        for account in accounts:
            logger.info(account.total_points)
            try:
                db_account = self.session.query(AccountModel).filter(AccountModel.id == account.id).one_or_none()
                db_account.api_key = account.api_key
                db_account.sui_wallet = account.sui_wallet
                db_account.is_twitter_connected = account.is_twitter_connected
                db_account.is_email_verified = account.is_email_verified
                db_account.authorization_key = account.authorization_key
                db_account.referral_code = account.referral_code
                db_account.total_points = account.total_points
                db_account.cookies = json.dumps(account.cookies)
                db_account.is_registered = account.is_registered
                db_account.headers = json.dumps(account.headers)
                self.session.commit()
            except Exception as error:
                logger.info(error)
            finally:
                self._close_session()

    def _create_session(self) -> None:
        """
        Создание сессии
        :return:
        """
        self.engine = create_engine(self.db_url)
        self.session = Session(self.engine)

    def _close_session(self):
        """
        Закрытие текущей сессии.
        """
        try:
            self.session.close()
        except Exception as e:
            logger.warning(f"Произошла ошибка при закрытии сессии: {e}")
