"""
Импорт данных из SQL баз данных (SQLite, PostgreSQL, MySQL)
"""

import pandas as pd
import urllib.parse


class SQLImporter:
    """Универсальный импорт из SQL"""

    SUPPORTED_DIALECTS = ['sqlite', 'postgresql', 'mysql']

    @staticmethod
    def build_connection_string(dialect: str, username: str, password: str, host: str, port: str, database: str) -> str:
        """Построение строки подключения SQLAlchemy"""
        if dialect == 'sqlite':
            # Для SQLite путь к файлу указывается как database
            return f"sqlite:///{database}"

        # Кодирование пароля на случай спецсимволов
        encoded_password = urllib.parse.quote_plus(password)

        if dialect == 'postgresql':
            return f"postgresql+psycopg2://{username}:{encoded_password}@{host}:{port}/{database}"
        elif dialect == 'mysql':
            return f"mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Неподдерживаемая СУБД: {dialect}")

    @staticmethod
    def import_from_query(connection_string: str, query: str) -> pd.DataFrame:
        """
        Выполнение SQL-запроса и возврат результата в DataFrame
        """
        try:
            from sqlalchemy import create_engine
            engine = create_engine(connection_string)

            with engine.connect() as connection:
                df = pd.read_sql_query(query, connection)

            return df
        except ImportError:
            raise ImportError(
                "Для работы с SQL необходимо установить библиотеки:\n"
                "pip install sqlalchemy psycopg2-binary pymysql"
            )
        except Exception as e:
            raise ConnectionError(f"Ошибка выполнения запроса: {e}")

    @staticmethod
    def get_tables_list(connection_string: str) -> list:
        """Получение списка таблиц в базе данных"""
        try:
            from sqlalchemy import create_engine, inspect
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            return inspector.get_table_names()
        except Exception as e:
            raise ConnectionError(f"Не удалось получить список таблиц: {e}")