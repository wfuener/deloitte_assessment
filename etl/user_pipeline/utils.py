"""This module holds classes and functions used
by various parts of the ETL. In this case it is just a database
access class"""
import logging
import os
import psycopg

logger = logging.getLogger("etl_logger")


class PgAccess:

    def __init__(self):
        self.conn = self.create_conn()


    def create_conn(self) -> object:
        """Create A psycopg2 connection.

        Returns:
            (obj) psycopg2 connection
        """
        # get our "secrets" from environment variables
        db_config = {
            'dbname': os.environ.get("PG_NAME"),
            'port': os.environ.get("PG_PORT"),
            'host': os.environ.get("PG_HOSTNAME"),
            'application_name': os.environ.get("PG_APP_NAME"),
            'connect_timeout': 20,
            'user': os.environ.get("PG_USER"),
            'password': os.environ.get("PG_PASSWORD"),
        }

        try:
            conn = psycopg.connect(**db_config)
            conn.autocommit = True
        except psycopg.Error as e:
            logger.error(f"Error getting database: {e.__class__.__name__} - {str(e)} ")
            return None

        logger.info("***** POSTGRES CONNECTION CREATED *****")

        return conn


    def copy(self, query, file_stream) -> None:
        """Run the postgres copy command through the psycopg2 copy_expert method"""
        try:
            with self.conn.cursor() as cur:
                with cur.copy(query) as copy:
                    # read file chunk by chunk and write to postgres
                    while data := file_stream.read(100):
                        copy.write(data)
        # NOTE in a production system you would want to catch more specific errors and handle each accordingly
        except Exception as e:
            logger.error(f"ERROR ON QUERY: {query}\nERROR MESSAGE: {str(e)}")
            logger.error("Data was not loaded")
        else:
            logger.info("data was copied into postgres")

