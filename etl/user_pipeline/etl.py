"""Main module for the ETL. It will:
1. Read in the csv file
2. Transform each row
3. Create a new file
4. Load it into Postgres
"""
import os
import csv
import logging
from user_pipeline.utils import PgAccess


logger = logging.getLogger("etl_logger")

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(BASE_DIR, 'data')   # where we will store our input and output files
INPUT_FILE_NAME = "SRDataEngineerChallenge_DATASET.csv"
OUTPUT_FILE_NAME = "transformed_file.csv"


class ETL:

    def __init__(self):
        self.pg = PgAccess()
        self.data = []  # data read from csv file


    def main(self) -> None:
        """This main method controls the logic flow of the ETL."""
        self.read_data()
        self.write_transformed_file()
        self.copy_to_pg()


    def read_data(self) -> None:
        file_columns = ("id", "first_name", "last_name",	"email", "gender", "ip_address")
        with open(f"{DATA_DIR}/{INPUT_FILE_NAME}", "r") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=file_columns, delimiter=',')
            next(reader, None)    # read header line

            for row in reader:
                row = self.transform(row)
                if row:     # None is returned for invalid data in the row
                    self.data.append(self.transform(row))

        logger.info(f"Number of rows read and transformed: {len(self.data)}")


    def transform(self, row: dict) -> dict:
        """Transform a row of data read from the input file. Checks
        the ID is right data type (int), strips whitespace from the fields
        that are of string type, and creates the full name field from first
        and last name

        Args:
            row(dict): raw row from file

        Returns:
            (dict): The row with transformations
            None: if there was an issue with the data
        """
        try:
            # ID must be a number and not null
            row['id'] = int(row.get('id'))
        except (ValueError, TypeError) as exc:
            print(f"invalid ID found - {row.get('id')} Removing row. ")
            return None

        # strip all trailing and leading whitespace from rows being read in as string
        row["first_name"] = row.get("first_name", "").strip()
        row["last_name"] = row.get("last_name", "").strip()
        row["email"] = row.get("email", "").strip()
        row["gender"] = row.get("gender", "").strip()
        row["ip_address"] = row.get("gender", "").strip()
        # create derived column
        row['full_name'] = row.get("first_name") + " " + row.get("last_name")

        return row


    def write_transformed_file(self) -> None:
        """Write the data to a pipe delimited csv file stored in the data directory"""
        logger.info("writing transformed file")

        with open(f"{DATA_DIR}/{OUTPUT_FILE_NAME}", "w") as csv_file:
            writer = csv.DictWriter(csv_file, delimiter='|', fieldnames=list(self.data[0].keys()),
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(self.data)

        logger.info("Finished writing transformed file")


    def copy_to_pg(self) -> None:
        """Copy CSV to bar table using COPY command"""
        logger.info("copying data to postgres")
        columns = ("id", "first_name", "last_name", "email", "gender", "ip_address", "full_name")

        copy_command = f"""COPY user_info."user" ({','.join(columns)}) from STDIN WITH
                     CSV DELIMITER '|' HEADER NULL as '' """

        with open(f"{DATA_DIR}/{OUTPUT_FILE_NAME}", "r") as file:
            self.pg.copy(copy_command, file)





