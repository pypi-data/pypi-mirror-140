import pandas as pd
import numpy as np
import datetime as dt
import humanfriendly as hf
import platform as pl
import openpyxl as xl
import os
import time
import json
import pymssql
import sys

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from smtplib import SMTP, SMTPException
from google.cloud.bigquery import Client, LoadJobConfig, DatasetReference, TableReference
from google.cloud.bigquery import SchemaField as sf
from google.oauth2 import service_account
from dateutil.relativedelta import relativedelta

from CsPy_Uploading.classes import BaseJob
from CsPy_Uploading.classes import JobSettings
from CsPy_Uploading.classes import UploadJob
from CsPy_Uploading.classes import DownloadJob
from CsPy_Uploading.classes import Account
from CsPy_Uploading.classes import Email
from CsPy_Uploading.classes import GeneralScriptError
from CsPy_Uploading.classes import InputError
from CsPy_Uploading.classes import ColumnMissingError

from CsPy_Uploading.functions import log
from CsPy_Uploading.functions import read_query_from_file
from CsPy_Uploading.functions import left
from CsPy_Uploading.functions import right
from CsPy_Uploading.functions import mid
from CsPy_Uploading.functions import copy_excel
from CsPy_Uploading.functions import save_excel_sheets_to_csv
from CsPy_Uploading.functions import delete_folder_contents
from CsPy_Uploading.functions import delete_bq_tables

"""
Classes:

    BaseJob: Underlying Class For UploadJob and DownloadJob
    
    JobSetting: Supporting class for BaseJob to create a set of settings under a single reference
    
    UploadJob: Class used to initialise an upload job and run the upload to Big Query
    
    DownloadJob: Class used to initialise an download job and run the download to export data
    
    Account: Class used to support BaseJob functions that stores additional variables
    
    
    GeneralScriptError: Exception Raised for general errors that should break the job
    
    InputError: Exception Raised for errors in the input to download job
    
    ColumnMissingError: Exception raised for errors within data_convert and int_convert
    
Functions:

    log(string): Used for script formatting
    
    read_query_from_file(string) -> string: Reads a txt or sql file and converts the contents to a string
    
    left(string, int) -> string: Reads and outputs the first x characters from the left of a string
    
    right(string, int) -> string: Reads and outputs the first x characters from the right of a string
    
    mid(string, int, int) -> string: Reads and outputs the first x characters from position y
    
    copy_excel(string, string): Copies a excel workbook to another location
    
    save_excel_sheets_to_csv(string, string, list): Converts a xlsx file into csv files of each sheet
    
    delete_folder_contents(string): Deletes all files within a specified folder
    
    delete_bq_files(string, string, string, int, string, string, string, string, string):
        Loops through dates to delete date suffixed tables within big query in bulk


Misc variables:

    __version__
    1.0.11
"""