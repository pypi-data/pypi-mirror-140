# Overview
This package is used to convert data from .csv, .xlsx and .xls into corresponing
insert, update, delete commands in a .sql file. This module alos has utility functions
for running sql queries and output the data into .csv, .xlsx, and .xls.

The package can be ran at the command line or the libraries can be imported within
python. This is mainly a wrapper around pyobc and pandas for connecting local data files
to a sql server databse.

help: will print available command line arguments
python -m tsqlxlsx -h

# Print Available Drivers for pyodbc
python -m tsqlxlsx --ld
Common Sql Drivers:
"ODBC Driver 13 for SQL Server"
"ODBC Driver 17 for SQL Server"

# Sql Server Drivers
SQL Drivers can be found at: These are the executables for connecting to sql server and are required to used this module.
https://docs.microsoft.com/en-us/sql/connect/odbc/windows/release-notes-odbc-sql-server-windows?view=sql-server-ver15#previous-releases

# Supported File Extensions 
If .sql extension is used module assumes it contains commands to run and no further processing is done. other extenisons are used as output
files or used to pull the arguments for the sql commands to be generated.
## -f flag
.xlsx
.xls
.sql
.csv
## -o flag
.xlsx
.xls
.csv

# Example Commands
## General:
python -m tsqlxlsx -u username -p password -f /pathToFile/example.xlsx -odir /pathWhereFileDataIsStoredAsSqlCommands/ -ctype i -pyodbc_driver "ODBC Driver 13 for SQL Server"

## VPN (Doesnt require username or password):
python -m tsqlxlsx -f /pathToFile/example.xlsx -odir /pathWhereFileDataIsStoredAsSqlCommands/ -ctype d where_fieds id -pyodbc_driver "ODBC Driver 13 for SQL Server"
python -m tsqlxlsx -f /pathToFile/example.xlsx -odir /pathWhereFileDataIsStoredAsSqlCommands/ -ctype u where_fieds id set_fields column_x -pyodbc_driver "ODBC Driver 13 for SQL Server"

python -m tsqlxlsx -f /pathToFile/example.sql -o /filePathToOutput/outptut.csv -ctype u where_fieds id set_fields column_x -pyodbc_driver "ODBC Driver 13 for SQL Server"
python -m tsqlxlsx -f /pathToFile/example.sql -o /filePathToOutput/outptut.xlsx -ctype u where_fieds id set_fields column_x -pyodbc_driver "ODBC Driver 13 for SQL Server"

## Command Line Query
python -m tsqlxlsx -q "SELECT 1" -pyodbc_driver "ODBC Driver 13 for SQL Server"

## Driver naming conventions for sql server:
python -m tsqlxlsx --ld

# Windows Command Line
python -m tsqlxlsx -f C:\pathToFile\example.sql -o C:\filePathToOutput\outptut.csv -ctype u where_fieds id set_fields column_x -pyodbc_driver "ODBC Driver 13 for SQL Server"

## Windows .bat file with Anaconda Distribution of Python:
Install anaconda distribution.

Running python commands in .bat files requires the anaconda enviornment to be imported. First search for anaconda command prompt in windows search bar
Right click on the anaconda prompt and select "open file location"
Right click on the anaconda prompt icon in folder directory and select properties. In the shortcut section copy and paste the string in target window
The target window will have the full path to activate.bat followed by a path to anaconda. Replace the string below with those values and 

example.bat file
```bat
REM Command below sets environment for python
call C:\Users\{username}\AppData\Local\Continuum\anaconda3\Scripts\activate.bat C:\Users\{username}\AppData\Local\Continuum\anaconda3

Rem first argument is full path to anaconda python exectuable. this can be found in select properties of anaconda terminal
call C:\Users\{username}\AppData\Local\Continuum\anaconda3\python -q "SELECT 1" -pyodbc_driver "ODBC Driver 13 for SQL Server"
```

example.py
```python
#pip install tsqlxlsx
from tsqlxlsx.data_loader import DataLoader
from tsqlxlsx.tsql_connector import TsqlConnect
from tsqlxlsx.sql_ddl import SqlDDL

#Step 1. Fill values
server = 'server'
database ='database'
username = 'username'
password = "password"
use_trusted = False #set to true if on a vpn and dont require username/password or on a trusted server

#Step: 2 create sql files
input_file_path = './file_path/ExampleData.xlsx' 
x = DataLoader(input_file_path )
df = x.LoadFile()


"""
available crud_types
crud_type: create, create_insert, update, insert, delete
"""

#create sql for update
table_name  = "ExampleData"
crud_type = "update" #(other options are create, insert, update, delete)
sql_file = "./file_path/test/ExampleData"  #sql file generated from df object SqlDDL will append extensions
where_fields = ['id', 'department']
set_fields   = ['Billing', 'Collections']
csqlx  = SqlDDL(df, table_name, crud_type, sql_file, where_fields = where_fields, set_fields=set_fields) #, column_types={"id":"integer"})
csqlx.CreateFiles()

#create sql statements for create table and insert data
table_name  = "ExampleData"
schema_name = "schema_name" #should be replaced
crud_type = "create_insert" #(other options are create, insert, update, delete)
sql_file = "./file_path/test/ExampleData2"  #sql file generated from df object SqlDDL will append extensions
column_types = {'id': 'int'}
csqlx  = SqlDDL(df, schema_name, table_name, crud_type, sql_file,column_types=column_types) #, column_types={"id":"integer"})
csqlx.CreateFiles()

#Step 3
#loop throough all files created from csqlx.CreateFiles and send data to sql server
for sql_file in csqlx.sql_output_file_list:
    tsqlx = TsqlConnect(server,database,  username = username,password =password, 
        useTrusted=use_trusted, pyodbcDriver =pyodbc_driver)
    tname = pathlib.Path(sql_file).stem
    print(sql_file)
    tsqlx.Run(sql_file, is_file=True,verbose=verbose, output_file="")


#Alternative run sql statement direclty
out_file = "" #optional path to output results
tsqlx = TsqlConnect(server,database,  username = username,password =password, 
    useTrusted=use_trusted, pyodbcDriver =pyodbc_driver)
tname = pathlib.Path(sql_file).stem
tsqlx.Run("SELECT 1", is_file=False,verbose=verbose, output_file=out_file)
```