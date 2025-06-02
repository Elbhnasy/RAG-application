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
            
    async def delete_collection(self, collection_name:str)->bool:
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f'Deleting collection: {collection_name}')

                drop_table_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(drop_table_sql)
                await session.commit()
        return True
    
    async def create_collection(self, collection_name: str,
                                    embedding_size: int,
                                    do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f'Creating collection: {collection_name}')
            async with self.db_client() as session:
                async with session.begin():
                    create_table_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableSchemeEnums.TEXT.value} text, '
                            f'{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), '
                            f'{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                            f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer, '
                            f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_table_sql)
                    await session.commit()
            return True
        else:
            self.logger.info(f'Collection {collection_name} already exists.')
            return False
        
    async def is_index_existed(self, collection_name:str)->bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client( )as session:
            async with session.begin():
                index_check_sql = sql_text(f""" 
                                    SELECT 1 
                                    FROM pg_indexes 
                                    WHERE tablename = :collection_name
                                    AND indexname = :index_name
                                    """)
                results = await session.execute(check_sql, {"index_name": index_name, "collection_name": collection_name})
                
                return bool(results.scalar_one_or_none())
            
    async def create_vector_index(self, collection_name: str,
                                        index_type: str = PgVectorIndexTypeEnums.HNSW.value):
        
        is_index_existed = await self.is_index_existed(collection_name=collection_name)
        if is_index_existed:
            self.logger.info(f'Index for collection {collection_name} already exists.')
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                result = await session.execute(count_sql)
                records_count = result.scalar_one()

                if records_count < self.index_threshold:
                    return False
                
                self.logger.info(f"START: Creating vector index for collection: {collection_name}")

                index_name = self.default_index_name(collection_name)
                create_index_sql = sql_text( 
                                            f'CREATE INDEX {index_name} ON {collection_name} '
                                            f'USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})'
                                            )
                await session.execute(create_index_sql)
                await session.commit()
                self.logger.info(f"END: Creating vector index for collection: {collection_name}")

    async def reset_vector_index(self, collection_name: str, 
                                    index_type: str = PgVectorIndexTypeEnums.HNSW.value) -> bool:
        
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                drop_index_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
                await session.execute(drop_index_sql)
                await session.commit()
        return await self.create_vector_index(collection_name=collection_name, index_type=index_type)


    async def insert_one(self, collection_name: str, text: str, vector: list,
                            metadata: dict = None,
                            record_id: str = None):
        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                        f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                        'VALUES (:text, :vector, :metadata, :chunk_id)'
                                        )
                metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata is not None else "{}"
                await session.execute(insert_sql, {
                    'text': text,
                    'vector': "[" + ",".join([ str(v) for v in vector ]) + "]",
                    'metadata': metadata_json,
                    'chunk_id': record_id
                })
                await session.commit()

                await self.create_vector_index(collection_name=collection_name)
        
        return True
