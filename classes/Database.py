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
            CREATE TABLE IF NOT EXISTS ESPs (
                id INTEGER NOT NULL PRIMARY KEY,
                mac VARCHAR(17) NOT NULL UNIQUE,
                load_status BOOLENA,
                Timestamp DATETIME DEFAULT (DATETIME('now', '-3 hours')) NOT NULL
            );
        '''
        self.__cursor.execute(query)

        # Migração: limpa MACs antigos gravados com espaços/quebra de linha (idempotente)
        self.__cursor.execute(
            "UPDATE OR IGNORE ESPs "
            "SET mac = UPPER(TRIM(mac, ' ' || char(9) || char(10) || char(13)))"
        )
        self.__connection.commit()

    def save_ctd(self, mac: str) -> None:
        self.__cursor.execute('INSERT INTO ESPs(mac) VALUES (?)', (mac,))
        self.__connection.commit()

    def find_remote_by_mac(self, mac: str) -> bool:
        result = self.__cursor.execute('SELECT 1 FROM ESPs WHERE mac = ?', (mac,))
        return result.fetchone() is not None
        
    def get_all_ESPs(self) -> list:
        query = 'SELECT id, mac, Timestamp FROM ESPs'
        result = self.__cursor.execute(query)
        return result.fetchall()
    
    def drop_database(self):
        query = f"DELETE FROM ESPs"
        self.__cursor.execute(query)
        self.__connection.commit()

# database = Database('dev')
# database.create_tables()
# database.save_ctd('dwwdewdewwedwew')
# print(database.get_all_ESPs())
# # print((database.find_remote_by_mac('dwedwedew')))