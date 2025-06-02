from ..VectorDBInterface import VectorDBInterface
from VectorDBEnums import (DistanceMethodEnums,
                            PgVectorTableSchemeEnums,
                            PgVectorDistanceMethodEnums,
                            PgVectorIndexTypeEnums)

import logging 
from typing import List
from models.db_schemes import RetrievedDocument
from sqlalchemy.sql import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, default_vector_size: int = 786,
                    distance_method: str = None, index_threshold: int=100):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size

        self.index_threshold = index_threshold

        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = PgVectorDistanceMethodEnums.DOT.value

        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        self.distance_method = distance_method

        self.logger = logging.getLogger("uvicorn")
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector"
                ))
                await session.commit()
        
    async def disconnect(self):
        pass

    async def is_collection_existed(self, collection_name:str)-> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(f'SELECT * FROM pg_tables WHERE tablename = :collection_name')
                results = await session.execute(list_tbl, {'collection_name':collection_name})
                record = results.scalar_one_or_none()
        return record 
    
    async def list_all_collections(self)->List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tbl =  sql_text('SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix')
                results = await session.execute(list_tbl, {'prefix': self.pgvector_table_prefix})
                records = results.scalars().all()

        return records
    
    async def get_collection_info(self, collection_name:str)->dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(f'''
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes 
                    FROM pg_tables 
                    WHERE tablename = :collection_name
                ''')
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                
                table_info = await session.execute(table_info_sql, {'collection_name': collection_name})
                record_count = await session.execute(count_sql)

                table_data = table_info.fetchone()

                if not table_data:
                    return None
                
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "record_count": record_count.scalar_one(),
                }