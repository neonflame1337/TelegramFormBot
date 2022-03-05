from sqlite3 import connect, Connection, Cursor


class DbConnection:
    def __init__(self, path: str):
        self.connection: Connection = connect("db")
        self.cursor: Cursor = self.connection.cursor()
