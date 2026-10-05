from utils.path_resolver import data_path
import sqlite3

db_path = data_path('database')


class Database:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.__connection = sqlite3.connect(f'{db_path}/{self.db_name}.db')
        self.__cursor = self.__connection.cursor()

    def create_tables(self) -> None:
        query = '''
            CREATE TABLE IF NOT EXISTS Remotes (
                id INTEGER NOT NULL PRIMARY KEY,
                mac VARCHAR(17) NOT NULL UNIQUE,
                load_status BOOLENA,
                Timestamp DATETIME DEFAULT (DATETIME('now', '-3 hours')) NOT NULL
            );
        '''
        self.__cursor.execute(query)

        # Migração: limpa MACs antigos gravados com espaços/quebra de linha (idempotente)
        self.__cursor.execute(
            "UPDATE OR IGNORE Remotes "
            "SET mac = UPPER(TRIM(mac, ' ' || char(9) || char(10) || char(13)))"
        )
        self.__connection.commit()

    def save_ctd(self, mac: str) -> None:
        self.__cursor.execute('INSERT INTO Remotes(mac) VALUES (?)', (mac,))
        self.__connection.commit()

    def find_remote_by_mac(self, mac: str) -> bool:
        result = self.__cursor.execute('SELECT 1 FROM Remotes WHERE mac = ?', (mac,))
        return result.fetchone() is not None
        
    def get_all_remotes(self) -> list:
        query = 'SELECT id, mac, Timestamp FROM Remotes'
        result = self.__cursor.execute(query)
        return result.fetchall()
    
    def drop_database(self):
        query = f"DELETE FROM Remotes"
        self.__cursor.execute(query)
        self.__connection.commit()

# database = Database('dev')
# database.create_tables()
# database.save_ctd('dwwdewdewwedwew')
# print(database.get_all_remotes())
# # print((database.find_remote_by_mac('dwedwedew')))