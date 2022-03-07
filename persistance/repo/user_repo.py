from persistance.db_connection import DbConnection
from typing import Union
from sqlite3 import Connection, Cursor

from persistance.entity.user_entity import UserEntity


class UserRepo:
    def __init__(self, db_connection: DbConnection):
        self.connection: Connection = db_connection.connection
        self.cursor: Cursor = db_connection.cursor

    def __map_user(self, row: tuple) -> Union[UserEntity, None]:
        if row is None:
            return None
        return UserEntity(row[0], row[4], row[1], row[2], row[3], row[5])

    def find_all_ready_and_not_processed(self) -> list:
        result_set = self.cursor.execute(
            """
            select * from user
            where ready = 1
            and processed = 0;
            """
        )
        result = []
        for row in result_set.fetchall():
            result.append(self.__map_user(row))
        return result

    def find_user_by_id(self, id: int) -> Union[UserEntity, None]:
        result_set = self.cursor.execute(
            """
            select * from user
            where id = {0};
            """.format(id)
        )
        return self.__map_user(result_set.fetchone())

    def save_or_update(self, user: UserEntity):
        self.cursor.execute(
            """
            insert or replace into user (id, current_question_id, ready, processed, username, contact_info)
            values({0}, {1}, {2}, {3}, '{4}', '{5}');
            """.format(user.id, user.current_question, user.ready, user.processed, user.username, user.contact_info)
        )
        self.connection.commit()
