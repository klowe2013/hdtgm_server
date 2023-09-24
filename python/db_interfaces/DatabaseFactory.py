from python.db_interfaces.CassandraInterface import CassandraInterface
from python.db_interfaces.SQLiteInterface import SQLiteInterface

class DatabaseFactory:
    INTERFACE_MAP = {
        'cassandra': CassandraInterface,
        'sqlite': SQLiteInterface,
    }
    def __init__(self, database):
        self.database = database 

    def create(self, db_type, *args, **kwargs):
        print(args)
        return self.INTERFACE_MAP[db_type](self.database, *args, **kwargs)