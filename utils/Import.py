from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from TXT.models import AccountTXT
from db.models import AccountModel, Base


class TXT:
    """
    Класс для работы с TXT файлами.
    """
    @staticmethod
    def get_accounts_from_txt(path: str = 'data/input.txt', is_first_iter: bool = True) -> list[AccountTXT]:
        """
        Функция для получения объектов класса AccounTXT из txt файла.
        Args:
            path: Путь
            is_first_iter: Флаг первой итерации
        Returns:
            list[AccountTXT]
        """
        accounts = []
        with open(path, 'r') as file:
            for row in file:
                if is_first_iter:
                    is_first_iter = False
                    continue
                row = row.split(';')
                print(row)
                accounts.append(
                    AccountTXT(
                        mail=row[0],
                        mail_password=row[1],
                        password=row[2],
                        twitter_auth=row[3],
                        proxy=row[4],
                        authorization_key=row[5],
                        referral_code=row[6],
                        api_key=row[7].strip(),
                    )
                )
        return accounts

class Import:
    """
    Класс импорта и создания объектов в БД
    """
    @staticmethod
    def create_db_object() -> list[AccountModel]:
        """
        Создание объектов класса AccountModel
        Returns:

        """
        db_objects = []
        txt_accounts = TXT.get_accounts_from_txt()
        for account in txt_accounts:
            db_account = AccountModel(
                mail=account.mail,
                mail_password=account.mail_password,
                password=account.password,
                twitter_auth=account.twitter_auth,
                proxy=account.proxy,
                authorization_key=account.authorization_key,
                api_key=account.api_key,
                referral_code=account.referral_code,
            )
            db_objects.append(db_account)
        return db_objects

    @staticmethod
    def db_objects():
        """
        Добавление аккаунтов в БД.
        Returns:

        """
        objects_for_db = Import.create_db_object()
        engine = create_engine('sqlite:///db.db')
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            for db_obj in objects_for_db:
                session.add(db_obj)
            session.commit()
        logger.info(f'Аккаунты успешно добавлены в базу данных')