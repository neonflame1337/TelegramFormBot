from persistance.db_connection import DbConnection
from typing import Union
from sqlite3 import Connection, Cursor

from persistance.entity.question_entity import QuestionEntity


class QuestionRepo:
    def __init__(self, db_connection: DbConnection):
        self.connection: Connection = db_connection.connection
        self.cursor: Cursor = db_connection.cursor

    def __map_question(self, row: tuple) -> Union[QuestionEntity, None]:
        if row is None:
            return None
        return QuestionEntity(row[0], row[1], row[2])

    def find_all_questions(self) -> list:
        result_set = self.cursor.execute(
            """
            select * from question;
            """
        )
        result = []
        for row in result_set.fetchall():
            result.append(self.__map_question(row))
        return result

    def find_by_id(self, id: int) -> QuestionEntity:
        result_set = self.cursor.execute(
            """
            select * from question
            where id = {0}
            """.format(id)
        )
        return self.__map_question(result_set.fetchone())

    def count(self) -> int:
        return self.cursor.execute(
            """
            select count(id) from question
            where id > 0 and id < 100;
            """
        ).fetchone()[0]
