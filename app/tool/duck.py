import duckdb

class Duck:
    @staticmethod
    def query(sql: str) -> duckdb.DuckDBPyRelation:
        con = duckdb.connect(database=':memory:')
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("INSTALL parquet; LOAD parquet;")
        return con.sql(sql)
