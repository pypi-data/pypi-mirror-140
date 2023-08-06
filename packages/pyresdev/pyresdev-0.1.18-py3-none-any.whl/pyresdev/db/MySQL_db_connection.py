import logging
from typing import Optional, List
from numpy import int32
from sqlalchemy import create_engine, MetaData, Table, select, and_
import sqlalchemy
from sqlalchemy.pool import NullPool
import pandas as pd




logger = logging.getLogger()
logger.setLevel(logging.INFO)



class MySQLDbConnection:
    def __init__(self, ssm_db_user: str, ssm_db_pass: str, ssm_db_host: str, ssm_db_name:str,
                 read_timeout=7200, write_timeout=59, connection_echo=False,
                 isolation_level="REPEATABLE READ"):
        self.__read_timeout = read_timeout
        self.__write_timeout = write_timeout
        self.__enable_connection_echo = connection_echo
        self.__isolation_level = isolation_level
        self.__db_user = ssm_db_user
        self.__db_pass = ssm_db_pass
        self.__db_host = ssm_db_host
        self.__db_name = ssm_db_name
        self.__db_port = 3306

    def __enter__(self):
        self.__engine, self.__engine_metadata, self.__connection = self.__connect_to_db()
        return self

    def __exit__(self, *args, **kwargs):
        self.__close_db_connection()

    def __connect_to_db(self):
        logger.info(f'Connecting to {self.__db_name}')
        engine = create_engine(
            f'mysql+pymysql://{self.__db_user}:{self.__db_pass}@'
            f'{self.__db_host}:{self.__db_port}/{self.__db_name}?autocommit=true',
            echo=self.__enable_connection_echo, poolclass=NullPool,
            connect_args={'read_timeout': self.__read_timeout, 'write_timeout': self.__write_timeout},
            execution_options={
                "isolation_level": self.__isolation_level
            },
        )
        engine_metadata = MetaData(bind=engine)
        connection = engine.connect()
        logger.info(f'Connected to {self.__db_name} successfully')
        return engine, engine_metadata, connection

    
    def __get_table(self, name: str) -> Table:
        return Table(name, self.__engine_metadata, autoload=True)

    def __close_db_connection(self):
        if self.__connection:
            try:
                self.__connection.detach()
            except AttributeError:
                pass
            self.__connection.close()
            logger.info('OperationsDB connection closed successfully')

    def get_dataframe_from_text_query(self, query: str, parameters:dict):
        
        select_query = sqlalchemy.text(query)
        result = self.__connection.execute(select_query,parameters).fetchall()
        result = [dict(zip(row.keys(), row)) for row in result]
        print(f"- Total rows : {len(result)}")
        return pd.DataFrame(result)
 