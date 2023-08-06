import pandas as pd
import string
import random
from dvgroup_factory.etl.greenplum_utils import GreenplumUtils


class CopyUtils:

    @staticmethod
    def fillna(df):
        for col in df:
            # get dtype for column
            dt = df[col].dtype
            # check if it is a number
            if dt == int or dt == float:
                df[col].fillna(0, inplace=True)
            else:
                df[col].fillna("", inplace=True)

    @staticmethod
    def process_rows(rows, value_processor):
        if not value_processor:
            return

        for i, row in enumerate(rows):
            for j, el in enumerate(row):
                processed_el = value_processor(el)
                if processed_el != el:
                    rows[i][j] = processed_el

    @staticmethod
    def gp2ch(
            src_table: str,
            dst_table: str,
            factory,
            cols_map,
            types_map=None,
            gp_db='dvault',
            ch_db='db1',
            ch_type='ui',
            batch_size=1_000_000,
            where_condition='',
            value_processor=None,
    ):
        """
        Copy table from greenplum aka gp to clickhouse aka ch in batch_mode
        :param ch_type: 'analytics', 'ui', 'dedup'
        :param value_processor: function to update each value
        :param src_table: src table name from gp
        :param dst_table: dst table name from ch
        :param factory: factory instance
        :param cols_map: column name relation between gp and ch
        :param gp_db: gp database name
        :param ch_db: ch database name
        :param batch_size: size of batch
        :param where_condition: EXAMPLE "incoming_date='2022-01-01'"
        :return:
        """
        ch_client = factory.clickhouse_client(new=True, settings={'use_numpy': True}, type=ch_type)
        with factory.gp_connection(new=True, dbname=gp_db) as conn:
            cursor = conn.cursor()
            cursor_name = f"tmp_cursor_{''.join(random.choice(string.ascii_lowercase) for _ in range(16))}"
            columns = list(cols_map.keys())
            start_sql = f"""
               DECLARE {cursor_name} CURSOR FOR (
                    SELECT {','.join(columns)}
                    FROM {src_table}
                    {'where' if where_condition != '' else ''} {where_condition}
               );
            """
            cursor.execute(start_sql)
            cursor.execute(f"""FETCH FORWARD {batch_size} FROM {cursor_name};""")
            rows = cursor.fetchall()
            if value_processor:
                rows = [list(r) for r in rows]
                CopyUtils.process_rows(rows, value_processor)
            data_df = pd.DataFrame(rows, columns=columns)
            CopyUtils.fillna(data_df)
            if types_map:
                data_df = data_df.astype(types_map)
            if cols_map:
                data_df.rename(columns=cols_map, inplace=True)
            while data_df.shape[0] > 0:
                ch_client.insert_dataframe(f"INSERT INTO {ch_db}.{dst_table} VALUES", data_df)
                cursor.execute(f"""FETCH FORWARD {batch_size} FROM {cursor_name};""")
                rows = cursor.fetchall()
                if value_processor:
                    rows = [list(r) for r in rows]
                    CopyUtils.process_rows(rows, value_processor)
                data_df = pd.DataFrame(rows, columns=columns)
                CopyUtils.fillna(data_df)
                if types_map:
                    data_df = data_df.astype(types_map)
                if cols_map:
                    data_df.rename(columns=cols_map, inplace=True)
            end_sql = f"CLOSE {cursor_name}"
            cursor.execute(end_sql)

    @staticmethod
    def ch2gp(
            src_table: str,
            dst_table: str,
            factory,
            cols_map=None,
            types_map=None,
            ch_db='db1',
            ch_type='ui',
            gp_db='dvault',
            batch_size=1_000_000
    ):
        """
        Copy table from clickhouse aka ch to greenplum aka gp in batch_mode
        :param src_table: src table name from ch
        :param dst_table: dst table name from gp
        :param factory: factory instance
        :param cols_map: column name relation between gp and ch
        :param ch_db: ch database name
        :param gp_db: gp database name
        :param batch_size: size of batch
        :return:
        """
        offset = 0
        ch_client = factory.clickhouse_client(new=True, settings={'use_numpy': True}, type=ch_type)
        select_query = f"""
            SELECT {','.join(cols_map.keys()) if cols_map else '*'}
            FROM {ch_db}.{src_table} LIMIT {batch_size} OFFSET %s
        """
        data_df = ch_client.query_dataframe(select_query % offset)
        data_df = data_df.astype(types_map)
        data_df = data_df.astype(str)
        data_df.fillna('')
        if cols_map:
            data_df.rename(columns=cols_map, inplace=True)
        while data_df.shape[0] > 0:
            with factory.gp_connection(new=True, dbname=gp_db) as conn:
                GreenplumUtils.insert_dataframe(data_df, conn, dst_table)
            data_df = ch_client.query_dataframe(select_query % offset)
            if cols_map:
                data_df.rename(cols_map, inplace=True)
            data_df = data_df.astype(str)
            data_df.fillna('')