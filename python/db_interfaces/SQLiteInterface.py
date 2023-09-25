import sqlite3 
import pandas as pd 

class SQLiteInterface:

    def __init__(self, database):
        self.database = database 
        # self.session = sqlite3.connect(self.database)

    def create_table(self, table, schema):
        # Example: schema = '(ID INT PRIMARY KEY     NOT NULL,
            # NAME           TEXT    NOT NULL,
            # AGE            INT     NOT NULL,
            # ADDRESS        CHAR(50),
            # SALARY         REAL);'
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} {schema};
                """
            )
            conn.commit()
            
    def write_entry(self, data, table):
        q = (
        f"""
        INSERT INTO {table} 
        ({', '.join(data.keys())}) 
        VALUES {tuple([v for k, v in data.items()])};
        """
        )
        print(q)
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                rows = cursor.execute(q)
                conn.commit()
        except sqlite3.IntegrityError as e:
            # UNIQUE constraint failed: episode_info.FILENAME
            print(f'Error writing to db: {e}')    
        return rows 
    
    def query(self, query):
        with sqlite3.connect(self.database) as conn:
            # cursor = conn.cursor()
            # rows = cursor.execute(query)
            res = pd.read_sql(query, conn)
        return res 
    