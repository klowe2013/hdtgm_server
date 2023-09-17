from cassandra.cluster import Cluster

class CassandraInterface:

    def __init__(self, keyspace):
        self.keyspace = keyspace 
        self.cassandra_cluster = Cluster(['0.0.0.0'],port=9042)
        self.cassandra_session = self.cassandra_cluster.connect(self.KEYSPACE, wait_for_all_pools=True)
        self.cassandra_session.execute(f'USE {self.KEYSPACE}')

    def create_table(self, table, schema):
        # Example: schema = '(id int, filename text, binary text, PRIMARY KEY (id))'

        self.cassandra_session.execute(
            f"""
            CREATE TABLE {self.KEYSPACE}.{table} {schema};
            """
        )
        
    def write_cassandra(self, data, table):
        rows = self.cassandra_session.execute(
            f"""
            INSERT INTO {self.KEYSPACE}.{table}
            {tuple([k for k in data.keys()])}  
            VALUES {tuple([v for k, v in data.items()])}
            """
        ) 
        return rows 
    
    def read_cassandra(self, query):
        rows = self.cassandra_session.execute(query)
        return rows 
    