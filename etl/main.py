"""This is our driver file to run our ETL. Any uncaught exceptions
 will be caught and logged. In production system you would want to
 send metrics of success or failure to a monitoring/alerting system as well.
 """
import time
import logging
import sys
from user_pipeline.etl import ETL
from dotenv import load_dotenv


# load env variables before loading app's modules
load_dotenv()
START = time.time()


# create logger
logger = logging.getLogger('etl_logger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.DEBUG)

# add formatter to ch
handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# add ch to logger
logger.addHandler(handler)


if __name__ == '__main__':
    logger.info("******************* STARTING PIPELINE *******************\n")
    try:
        etl = ETL()
        etl.main()
    except Exception as exc:
        # Send error to alerting system
        logger.error(exc, exc_info=True)
    else:
        logger.info("******************* PIPELINE FINISHED *******************")
    finally:
        end_time = round(time.time() - START, 3)
        logger.info(f"Elapsed run time: {end_time} seconds")
