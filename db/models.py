from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
     pass


class AccountModel(Base):
    """
    Базовая модель аккаунта для БД.
    """
    __tablename__ = 'user_account'

    id: Mapped[int] = mapped_column(primary_key=True)
    mail: Mapped[str] = mapped_column(unique=True)
    mail_password: Mapped[str]
    password: Mapped[str]
    twitter_auth: Mapped[str] = mapped_column(unique=True)
    proxy: Mapped[str] = mapped_column(default=None, server_default='')
    headers: Mapped[str] = mapped_column(default=None, server_default='{}')
    cookies: Mapped[str] = mapped_column(default=None, server_default='{}')
    authorization_key: Mapped[str] = mapped_column(default=None, server_default='')
    is_registered: Mapped[bool] = mapped_column(default=False, server_default='0')
    is_email_verified: Mapped[bool] = mapped_column(default=False, server_default='0')
    is_twitter_connected: Mapped[bool] = mapped_column(default=False, server_default='0')
    is_twitter_locked: Mapped[bool] = mapped_column(default=False, server_default='0')
    total_points: Mapped[int] = mapped_column(default=0, server_default='0')
    sui_wallet: Mapped[str] = mapped_column(default=None, server_default='')
    referral_code: Mapped[str] = mapped_column(default=None, server_default='')
    api_key: Mapped[str] = mapped_column(default=None, server_default='')
