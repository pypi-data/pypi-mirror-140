import datetime as dt
import openpyxl as xl
import pandas as pd
import sys
import os

from google.cloud.bigquery import Client, TableReference
from google.oauth2 import service_account
from dateutil.relativedelta import relativedelta


# TODO: Add Emailing Function To Read Log Files
# TODO: Add SQL to Workbook function that reads multiple outputs to a excel workbook

def log(string):
    """
    INTERNAL FUNCTION
    """
    print(dt.datetime.now(), ': ', string)


def read_query_from_file(file_path):
    """
    Desc:
        read_query_from_file (function): Reads a txt or sql file and converts the contents to a string

    Args:
        file_path (str): Full file path to the file you wish to read
                Example: "C:/Users/RobinsonJa/queries/query.txt"

    Returns:
        query (str): a string of the contents of the text file

    Raises:
        No exceptions raise in this function
    """
    with open(file_path, 'r') as text:
        query = text.read()
        text.close()
    return query


def left(string, amount):
    """
    Desc:
        left (function): Reads and outputs the first x characters from the left of a string

    Args:
        string (str): String you wish to split

        amount (int): Number of characters to read from the left hand side of the string
               Notes: Character positions count from 1

    Returns:
        string[:amount] (str): The resulting characters of the string

    Examples:
        >> string="Hello World"
        >> amount=3
        >> left(string, amount)
        Hel

    Raises:
        No exceptions raise in this function
    """

    new_string = string[:amount]
    return new_string


def right(string, amount):
    """
    Desc:
        right (function): Reads and outputs the first x characters from the right of a string

    Args:
        string (str): String you wish to split

        amount (int): Number of characters to read from the right hand side of the string
               Notes: Character positions count from 1

    Returns:
        new_string (str): The resulting characters of the string

    Examples:
        >> string="Hello World"
        >> amount=4
        >> right(string, amount)
        orld

    Raises:
        No exceptions raise in this function
    """

    new_string = string[-amount:]
    return new_string


def mid(string, offset, amount):
    """
    Desc:
        mid (function): Reads and outputs the first x characters from the character starting at position offset

    Args:
        string (str): String you wish to split

        offset (int): Number of characters to skip from the left hand side of the string
               Notes: Character positions count from 1

        amount (int): Number of characters to read from the starting position based on the offset variable

    Returns:
        new_string (str): The resulting characters of the string

    Examples:
        >> string="Hello World"
        >> offset=6
        >> amount=2
        >> mid(string, offset, amount)
        wo

    Raises:
        No exceptions raise in this function
    """

    new_string = string[offset:offset+amount]
    return new_string


def copy_excel(source, destination):
    """
    Desc:
        copy_excel (function): Copies a excel workbook to another location

    Args:
        source (str): Full file path of excel document you wish to copy

        destination (str): Full file path you wish to copy the excel workbook to

    Returns:
        Returns no values

    Raises:
        No exceptions raise in this function
    """
    wb1 = xl.load_workbook(source, data_only=True)
    wb1.save(str(destination))


def save_excel_sheets_to_csv(excel_file_path, save_path, sheet_names=None):
    """
    Desc:
        save_excel_sheets_to_csv (function): Converts a xlsx file into csv files of each sheet

    Args:
        excel_file_path (str): Full file path of excel document you wish to copy
                      Example: "C:/Users/RobinsonJa/excel_files/excel_fil.xslx"

        save_path (str): Full file path you wish to copy the excel workbook to
                Example: "C:/Users/RobinsonJa/csv_folder/"

        sheet_names (list): List of sheets to save as a CSV
                   Example: ['sheet1','sheet3']
                     Notes: If not supplied will default save all sheets

    Returns:
        Returns no values

    Raises:
        No exceptions raise in this function
    """
    log('Loading {} into pandas.'.format(excel_file_path))
    wb = pd.ExcelFile(excel_file_path)
    full_save_path = save_path + '{}.csv'
    for idx, name in enumerate(wb.sheet_names):
        if sheet_names is not None:
            if name in sheet_names:
                log('Reading sheet #{0}: {1}'.format(idx, name))
                sheet = wb.parse(name)
                sheet.to_csv(full_save_path.format(name), index=False)

        elif sheet_names is None:
            log('Reading sheet #{0}: {1}'.format(idx, name))
            sheet = wb.parse(name)
            sheet.to_csv(full_save_path.format(name), index=False)


def delete_folder_contents(directory):
    """
    Desc:
        delete_folder_contents (function): Deletes all files within a specified folder

    Args:
        directory (str): Full file path to the folder you wish to remove files from
                Example: "C:/Users/RobinsonJa/Files_To_Delete/"

    Returns:
        No values are returned

    Raises:
        No exceptions raise in this initialisation class
    """
    log('Deleting files from: {}'.format(directory))
    for file in os.listdir(directory):
        log('Deleting: {}'.format(file))
        os.unlink(directory + file)


def delete_bq_tables(start_date: str, end_date: str, interval_type: str, interval_length: int,
                     bq_project: str, bq_dataset: str, bq_table: str, bq_key_path: str = None, bq_key_name: str = None,
                     ):
    """
    Desc:
        delete_bq_table (function): Loops through dates to delete date suffixed tables within big query in bulk
                             Notes: There are no recovery options for deleted tables so use with caution

    Args:
        start_date (str): Date you wish to start deleting table from. Format must be YYYY-MM-DD
                 Example: "2021-01-01"

        end_date (str): Date you wish to end deleting table from. Format must be YYYY-MM-DD
               Example: "2021-01-01"

        interval_type (str): The type of interval between dates you wish to use. Accepted values DAY, MONTH, YEAR

        interval_length (int): The number of interval_type you want to step by

        bq_project (str): The name of the Big Query project you wish to use

        bq_dataset (str): The name of the Big Query dataset you wish to use

        bq_table (str): The name of the Big Query table you wish to use
               Example: "my_bq_table_"
                 Notes: Only supply the table name without any suffixes


        Optional Args:

        bq_key_path (str): The file path to the folder that holds you Big Query service account file
                  Example: "C:/Users/RobinsonJa/bq_service_accounts/"
                    Notes: If not supplied the script will default to the working directory

        bq_key_name (str): Name of the service account file you wish to use
                Example: "bq_key.json"
                  Notes: If not supplied the script with default to "key.json"

    Returns:
        No values are returned

    Raises:
        InputError: When an input is supplied incorrectly
    """
    # Set Up Dates
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    step_change = dt.timedelta(days=1)
    if interval_type not in ('DAY', 'MONTH', 'YEAR'):
        raise InputError(job_progress="Setting Up Dates",
                         input_variable_name="interval_type",
                         message="Interval variable input not recognised. Accepted values DAY, MONTH, YEAR",
                         solution="Check the interval_type variable input and that it matches the accepted inputs"
                         )

    else:
        if interval_type == 'DAY':
            step_change = dt.timedelta(days=interval_length)
        elif interval_type == 'MONTH':
            step_change = relativedelta(months=+interval_length)
        elif interval_type == 'YEAR':
            step_change = relativedelta(years=+interval_length)

    # Find BQ Key and Set Up Connection
    if bq_key_name is None:
        log("bq_key_name not provided using default search of key.json")
        bq_key_name = "key.json"

    if bq_key_path is None:
        log("bq_key_path not provided searching working directory")
        directory_name, file_name = os.path.split(os.path.abspath(sys.modules['__main__'].__file__))
        bq_key_path = directory_name
        bq_full_key_path = os.path.join(bq_key_path, bq_key_name)

    else:
        bq_full_key_path = bq_key_path + bq_key_name

    scopes = ['https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/drive.readonly']
    credentials = service_account.Credentials.from_service_account_file(bq_full_key_path, scopes=scopes)
    client = Client(project=bq_project, credentials=credentials)

    # Delete Tables
    while start_date <= end_date:
        date_key = start_date.strftime('%Y%m%d')
        table_reference_string = bq_project + '.' + bq_dataset + '.' + bq_table + date_key
        table_reference = TableReference.from_string(table_reference_string)
        try:
            client.delete_table(table=table_reference)
            log(table_reference_string + "Deleted!")

        except Exception as e:
            log(table_reference_string + "Does Not Exist")

        start_date = start_date + step_change


class InputError(Exception):
    """
    Desc:
        InputError (Exception): Exception Raised for errors in the input to download job

    Args:
        job_progress (str): Progress in the script

        input_variable_name (str): Input expression in which the error occurred

        message (str): Explanation of the error

        solution (str): Most common way to fix the error
    """

    def __init__(self, job_progress, input_variable_name, message, solution):
        self.job_progress = job_progress
        self.input_variable_name = input_variable_name
        self.message = message
        self.solution = solution
        self.line = '=' * 99
        super().__init__(self)

    def __str__(self):
        return f"""

INPUT ERROR!
{self.line}
FAILED DURING: {self.job_progress}
FAILED VARIABLE: {self.input_variable_name}
INPUT ERROR: {self.message}
SOLUTION: {self.solution}
{self.line}
        """
