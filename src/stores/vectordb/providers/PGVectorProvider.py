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