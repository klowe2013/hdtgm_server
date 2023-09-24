from cassandra.cluster import Cluster

class CassandraInterface:

    def __init__(self, keyspace):
        self.keyspace = keyspace 
        self.cassandra_cluster = Cluster(['0.0.0.0'],port=9042)
        self.cassandra_session = self.cassandra_cluster.connect(self.keyspace, wait_for_all_pools=True)
        self.cassandra_session.execute(f'USE {keyspace}')

    def create_table(self, table, schema):
        # Example: schema = '(id int, filename text, binary text, PRIMARY KEY (id))'

        self.cassandra_session.execute(
            f"""
            CREATE TABLE {self.keyspace}.{table} {schema};
            """
        )
        
    def write_entry(self, data, table):
        q = (
        f"""
        INSERT INTO {table} 
        ({', '.join(data.keys())}) 
        VALUES {tuple([v for k, v in data.items()])};
        """
        )
        rows = self.cassandra_session.execute(q)
        return rows 
    
    def query(self, query):
        rows = self.cassandra_session.execute(query)
        return rows 
    