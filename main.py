import asyncio
import os

from loguru import logger

from utils.Import import Import
from db.db_api import DB
from config import THREADS, SLEEP


def make_start_files():
    directory = 'data'
    file_name = 'input.txt'

    # Проверяем, существует ли папка, если нет - создаем ее
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f'Создана папка {directory}')

    # Полный путь к файлу
    file_path = os.path.join(directory, file_name)

    # Проверяем, существует ли файл, если нет - создаем его
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')
        logger.info(f'Создан файл {file_name}')



async def make_base_action(action):
    """
    Функция обработки выбранного запроса.
    :param action: Номер выбранного запроса.
    :return:
    """
    make_start_files()
    semaphore = asyncio.Semaphore(THREADS)

    async def limited_task(coro):
        async with semaphore:
            return await coro

    database = DB()
    accounts = database.create_worked_accounts()
    logger.info(f'Total accounts fetched: {len(accounts)}')
    if action == 3:
        try:
            tasks = [asyncio.create_task(limited_task(account.get_account_info())) for account in accounts if account.is_registered]
            if tasks:
                results = await asyncio.wait(tasks)
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f'Error in get_account_info: {result}')

        except Exception as error:
            logger.error(f'Exception during account processing: {error}')

        finally:
            for account in accounts:
                await account.close_session()
            database.update_account_info(accounts=accounts)

    elif action == 2:
        try:
            for account in accounts:
                logger.info(account.api_key)
            tasks = [asyncio.create_task(limited_task(account.make_all_actions(SLEEP))) for account in accounts]
            if tasks:
                await asyncio.wait(tasks)

        except Exception as error:
            logger.error(f'Exception during account processing: {error}')

        finally:
            database.update_account_info(accounts=accounts)



async def main():
    """
    Функция запуска программы.
    :return:
    """
    while True:
        print('''  Select the action:
        1) Import accounts from the spreadsheet to the DB;
        2) Make all actions;
        3) Get accounts info;
        6) Exit
        ''')
        try:
            action = int(input('Выберите действие: '))
            if action == 1:
                Import.db_objects()

            elif action == 2 or action == 3:
                await make_base_action(action)


            elif action == 6:
                logger.info('Программа завершена')
                break

        except KeyboardInterrupt:
            print()

        except ValueError as err:
            logger.error(f'Value error: {err}')

        except BaseException as e:
            logger.error(f'Something went wrong: {e}')

if __name__ == '__main__':
    asyncio.run(main())