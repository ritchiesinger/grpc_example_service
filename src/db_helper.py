"""Клиент по работе с БД."""

from dataclasses import dataclass
from sqlite3 import Connection, connect, IntegrityError

import GrpcExampleService_pb2 as Pb2


@dataclass
class SQLStrings:
    """SQL запросы и шаблоны для SQL запросов."""
    add_user = "INSERT INTO user(login, email, city) VALUES('{login}','{email}','{city}')"
    get_users = "SELECT * FROM user"
    get_user_by_login = "SELECT * FROM user WHERE login = '{login}'"
    init_db_structure = (
        "CREATE TABLE user(id INTEGER PRIMARY KEY AUTOINCREMENT, login text UNIQUE, email text, city text)"
    )
    check_db = "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
    delete_user = "DELETE FROM user WHERE id = {id}"


class DBHelper:
    """Клиент по работе с БД."""

    def __init__(self, path_to_db: str):
        """Клиент по работе с БД.

        :param path_to_db: Путь до файла с БД SQLite.
        """
        self.path_to_db = path_to_db
        self.prepare_db()

    def connect(self) -> Connection:
        """Открытие соединения с БД."""
        return connect(self.path_to_db)

    def prepare_db(self):
        """Проверка и подготовка БД в случае её отсутствия."""
        with self.connect() as connection:
            if not connection.cursor().execute(SQLStrings.check_db).fetchall():
                connection.cursor().execute(SQLStrings.init_db_structure)
                connection.commit()

    def add_users(self, users):
        """Добавление пользователей. Client Streaming.

        :param users: Итератор (grpc._server._RequestIterator) с набором данных пользователей.
        :return: Список результатов сохранения пользователей.
        """
        response = []
        for user in users:
            with self.connect() as connection:
                cursor = connection.cursor()
                sql = SQLStrings.add_user.format(login=user.login, email=user.email, city=user.city)
                try:
                    cursor.execute(sql)
                    user_id = cursor.lastrowid
                    user_info = Pb2.UserInfo(id=user_id, login=user.login, email=user.email, city=user.city)
                    connection.commit()
                    response_meta = Pb2.ResponseMeta(error_code=0)
                except IntegrityError:
                    user_info = Pb2.UserInfo(login=user.login, email=user.email, city=user.city)
                    response_meta = Pb2.ResponseMeta(error_code=3)
                response.append(Pb2.UserResponse(user_info=user_info, response_meta=response_meta))
        return Pb2.AddUsersResponse(add_results=response)

    def get_users(self):
        """Получение всех пользователей. Server Streaming.

        :return: Серия ответов с данными пользователей.
        """
        with self.connect() as connection:
            result = connection.cursor().execute(SQLStrings.get_users)
        for row in result:
            user_info = Pb2.UserInfo(id=row[0], login=row[1], email=row[2], city=row[3])
            response_meta = Pb2.ResponseMeta(error_code=0)
            yield Pb2.UserResponse(user_info=user_info, response_meta=response_meta)

    def get_user_by_login(self, login):
        """Получение данных пользователя. Unary.

        :param login: Логин пользователя.
        :return: Данные запрашиваемого пользователя.
        """
        with self.connect() as connection:
            row = connection.cursor().execute(SQLStrings.get_user_by_login.format(login=login)).fetchone()
        if row:
            user_info = Pb2.UserInfo(id=row[0], login=row[1], email=row[2], city=row[3])
            return Pb2.UserResponse(user_info=user_info, response_meta=Pb2.ResponseMeta(error_code=0))
        else:
            return Pb2.UserResponse(user_info=Pb2.UserInfo(), response_meta=Pb2.ResponseMeta(error_code=2))

    def delete_users(self, clients):
        """Удаление пользователей. Bidirectional Streaming.

        :param clients: Итератор (grpc._server._RequestIterator) с объектами (id) пользователей.
        :return: Серия ответов о результате удаления каждого пользователя.
        """
        for client in clients:
            with self.connect() as connection:
                cursor = connection.cursor()
                cursor.execute(SQLStrings.delete_user.format(id=client.id))
                modified_rows = cursor.rowcount
                response_meta = Pb2.ResponseMeta(error_code=0) if modified_rows > 0 else Pb2.ResponseMeta(error_code=2)
                connection.commit()
            yield Pb2.DeleteUserResponse(user_info=Pb2.DeleteUserInfo(id=client.id), response_meta=response_meta)
