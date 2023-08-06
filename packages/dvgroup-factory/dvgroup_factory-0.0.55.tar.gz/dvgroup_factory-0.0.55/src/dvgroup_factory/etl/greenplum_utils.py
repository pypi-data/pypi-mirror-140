import logging
import psycopg2

log = logging.getLogger(__name__)


class GreenplumUtils:

    @staticmethod
    def _insert_batch_df(df, conn, table):
        """
        Insert pandas dataframe to table
        :param df: dataframe to insert
        :param conn: pg/gp connection
        :param table: target table name
        :return:
        """
        cursor = conn.cursor()
        cols = df.columns.tolist()
        values = [cursor.mogrify("(%s)" % ','.join('%s' for _ in cols), tup).decode('utf8') for tup in df.itertuples(index=False)]
        query = "INSERT INTO %s(%s) VALUES " % (table, ','.join(cols)) + ",".join(values)
        try:
            cursor.execute(query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            log.error("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        log.debug("_insert_batch_df() done")
        cursor.close()

    @staticmethod
    def insert_dataframe(df, conn, table, batch_size=100_000):
        """
        Insert data from pandas dataframe into table in batch mode'
        :param df: dataframe to insert
        :param conn: pg/gp connection
        :param table: target table name
        :param batch_size: batch size
        :return:
        """
        size = df.shape[0]
        for ind in range(0, size, batch_size):
            GreenplumUtils._insert_batch_df(df.loc[ind:ind+batch_size], conn, table)

    @staticmethod
    def drop_table(conn, table, if_exists: bool=True):
        """
        :param conn: pg/gp connection
        :param table: table name to drop
        :param if_exists: flag to append IF EXISTS
        :return:
        """
        query = "DROP TABLE {if_exists} {table}".format(if_exists='IF EXISTS' if if_exists else '', table=table)
        conn.cursor().execute(query)
        conn.commit()