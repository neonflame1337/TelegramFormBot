from persistance.db_connection import DbConnection
from typing import Union
from sqlite3 import Connection, Cursor

from persistance.entity.answer_entity import AnswerEntity


class AnswerRepo:
    def __init__(self, db_connection: DbConnection):
        self.connection: Connection = db_connection.connection
        self.cursor: Cursor = db_connection.cursor

    def __map_answer(self, row: tuple) -> Union[AnswerEntity, None]:
        if row is None:
            return None
        return AnswerEntity(row[0], row[1], row[2])

    def find_all_answers_by_user_id(self, user_id: int) -> list:
        result_set = self.cursor.execute(
            """
            select * from answer
            where user_id = {0};
            """.format(user_id)
        )
        result = []
        for row in result_set.fetchall():
            result.append(self.__map_answer(row))
        return result

    def save_or_update(self, answer: AnswerEntity):
        self.cursor.execute(
            """
            insert or replace into answer (user_id, question_id, text)
            values ({0}, {1}, '{2}');
            """.format(answer.user_id, answer.question_id, answer.text)
        )
        self.connection.commit()
