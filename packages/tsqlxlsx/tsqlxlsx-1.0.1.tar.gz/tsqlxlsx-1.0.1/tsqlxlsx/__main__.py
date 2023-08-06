"""
main function for parsing .xls, .xlsx and .csv files and sending data to a tsql server.
.sql files can be ran direclty.
"""
#pip install tsql_xlsx
import argparse
from .data_loader import DataLoader
from .tsql_connector import TsqlConnect
from .sql_ddl import SqlDDL
import argparse
import os
import pyodbc
import pathlib
import re

#argparse:
def mkdir (file_path):
    try:
        os.makedirs(file_path)
    except Exception as e:
        # print(e)
        pass

dtypex = ['bigint', 'numeric', 'smallint', 'int', 'float', 'real', 'date', 'datetime', 'datetime2', 'time',
    'varchar(250)', 'varchar(500)', 'varchar(100)', 'varchar(1500)', 'varchar(2000)', 'text' ]


class RunMain:

    def __init__(self):
        self.dargs = None

    def Run(self):
        #Step 1. Fill values
        dargs = self.dargs
        server   = dargs['s']
        database = dargs['d']
        username = dargs['u']
        password = dargs['p']
        schema_name = dargs['schema_name']
        table_name  = dargs['table_name']

        ctype_map = { 'ci': 'create_insert', 'c': 'create', 'i': 'insert',
            'u': 'update', 'd':'delete'}


        ctype       = ctype_map [ dargs['ctype'] ]
        use_trusted = dargs['use_trusted']
        username = dargs['u']
        password = dargs['p']
        pyodbc_driver = dargs['pyodbc_driver']
        in_file_name   = dargs['f']
        out_file_name  = dargs['o']
        odir = dargs['odir']
        verbose = dargs['v']
        alias   = dargs['alias']
        delim   = dargs['delim']
        as_null = dargs['null']

        column_types   = dargs['column_types']
        where_fields   = dargs['where_fields']
        set_fields     = dargs['set_fields']

        stripDateTime  = dargs['std']
        batchSize      = dargs['bsize']
        qstring        = dargs['q']

        sh = dargs['sh']
        sf = dargs['sf']
        # Run(self,sqlFileName, is_file=True, verbose=True, output_file="")

        if dargs['find_params']: #argument for first hit
            tsqlx = TsqlConnect(server,database,  username = username,password =password, 
                useTrusted=True, pyodbcDriver = "", store_df=False, sqlCmdSep=delim)
            tsqlx.FindCorrectConnection(first_hit=False)
            return

        if dargs['find_params_1']: #argument for first hit
            tsqlx = TsqlConnect(server,database,  username = username,password =password, 
                useTrusted=True, pyodbcDriver ='', store_df=False, sqlCmdSep=delim)
            tsqlx.FindCorrectConnection(first_hit=True)
            return

        if dargs['ld']: #argument for first hit
            print(pyodbc.drivers())
            return

        if dargs['pbat']:
            in_path = pathlib.Path(__file__).parent.resolve()
            fpath   = os.path.join(in_path, 'run_edw.bat')
            f = open(fpath)
            s = f.read()
            print(s)
            f.close()
            return

        if dargs['ppy']:
            in_path = pathlib.Path(__file__).parent.resolve()
            fpath   = os.path.join(in_path, 'example_py.txt')
            f = open(fpath)
            s = f.read()
            print(s)
            f.close()
            return

        if dargs['readme']:
            in_path = pathlib.Path(__file__).parent.resolve()
            fpath   = os.path.join(in_path, 'README.md')
            f = open(fpath)
            s = f.read()
            print(s)
            f.close()
            return



        #run raw query string
        if not dargs['q'] is None:
            sql_string = dargs['q']
            tsqlx = TsqlConnect(server,database,  username = username,password =password, 
            useTrusted=use_trusted, pyodbcDriver =pyodbc_driver)
            tsqlx.Run(sql_string, is_file=False,verbose=verbose,output_file=out_file_name)
            return

        #convert xls, xlsx and csv to sql files and run
        fext = pathlib.Path(in_file_name).suffix
        if fext in ['.xls', '.xlsx', '.csv']:
            input_file_path = in_file_name
            x = DataLoader(input_file_path, delimiter = delim, stripDateTime=stripDateTime, alias=alias, skipHeaderRows=sh, skipFooterRows=sf  )
            df = x.LoadFile()
            #sql script file creation:
            table_name  = table_name
            crud_type = ctype
            sql_file = os.path.join(odir, table_name)
            csqlx  = SqlDDL(df, schema_name, table_name, crud_type,  sql_file, batchSize = batchSize,
                set_fields = set_fields, where_fields = where_fields, 
                column_types=column_types, as_null=as_null)
            csqlx.CreateFiles()

            if dargs['sexe']:
                return


            for sql_file in csqlx.sql_output_file_list:
                tsqlx = TsqlConnect(server,database,  username = username,password =password, 
                    useTrusted=use_trusted, pyodbcDriver =pyodbc_driver)
                tname = pathlib.Path(sql_file).stem
                print(sql_file)
                of = ""
                if out_file_name != "":
                    of = out_file_name + '_'+tname.replace(" ","_")
                tsqlx.Run(sql_file, is_file=True,verbose=verbose, output_file=of)
            return

        #run sql file
        if fext == '.sql':
            sql_file = in_file_name
            tsqlx = TsqlConnect(server,database,  username = username,password =password, 
            useTrusted=use_trusted, pyodbcDriver =pyodbc_driver)
            tsqlx.Run(sql_file, is_file=True,verbose=verbose,output_file=out_file_name)
            return

    #simple script template
    def InitializeParser(self):

        main_description = """
        Module to convert xlsx/xls/csv into sql server files and return sql queries into csv/xls/xlsx. For help use the following commands:
        To view readme: https://pypi.org/project/tsqlxlsx/

        list all pyodbc drivers available:
            python -m tsqlxlsx --ld:
        dislpay example.bat file for running program as windows executable
            python -m tsqlxlsx --pbat
        display example python script for calling and running modules in python:
            python -m tsqlxlsx --ppy
        display README.md for module
            python -m tsqlxlsx --readme

        to output file file use
        linux/mac
        python -m --readme > pathToFolder/readme.md 
        windows:
        python -m --readme > C:\pathToFolder\readme.md 
        """

        parser = argparse.ArgumentParser(description=main_description)
        # parser.add_argument('integers', metavar='N', type=int, nargs='+',
        #                     help='an integer for the accumulator')
        findp_h =""" this flag makes serveral attempts to connect to a tsql server with different conneciton parameters. The first
        successful hit is generaly the best configuration to use. Please specify username and password. This is used as a last
        resort for connections that wont allow for the use_trusted flag. Python require the sql server drivers to be installed into
        the operating system. Version 13 seems to work consistently.

        SQL Drivers can be found at: These are the executables for connecting to sql server.
        https://docs.microsoft.com/en-us/sql/connect/odbc/windows/release-notes-odbc-sql-server-windows?view=sql-server-ver15#previous-releases
        """
        parser.add_argument('--find_params', help= findp_h, action='store_true')
        parser.add_argument('--find_params_1', help= "same as --find_params but stops on first succesful hit", action='store_true')
        parser.add_argument('--ld', help= "list all pyodbc drivers available", action='store_true')
        parser.add_argument('--pbat', help= "dislpay example.bat file for running program as windows executable", action='store_true')
        parser.add_argument('--ppy', help= "dislpay example.py file for running program as python module", action='store_true')
        parser.add_argument('--readme', help= "dislpay modules readme.md markdown file", action='store_true')

        parser.add_argument('-s', help= 'name of the server', default= "")
        parser.add_argument('-d', help= 'name of the database.', default= "")
        parser.add_argument('-schema_name', help= 'name of the schema', default= "")

        parser.add_argument('-table_name', help= 'Name of table. Default is the name of the input file with extension removed if its an .xls, .xlsx or .csv')
        ctype_h = """ name of the sql operation. default is ci
        ci: create/drop table followed by a series of insert tables into [schema].[table]
        c: create table only using columns from file
        i: series of insert tables into [schema].[table]
        u: series of update tables into [schema].[table] Requires where_fields and set_fields to be specified.
            this is a list of columns in the file that will be used in the where and set statements
        d: series of delete tables into [schema].[table] Requires where_fields to be specified.
            this is a list of columns in the file that will be used in the where statement
        """
        parser.add_argument('-ctype', help= ctype_h, choices=['ci','c','i','d','u'], default= "ci")


        parser.add_argument('-use_trusted', help= 'use credentials from vpn. this option does not require username or password', action='store_true' )
        parser.add_argument('-u', help= 'username i.e. bgovindara@iuhealth.org only required if use_trusted is false', default="")
        parser.add_argument('-p', help= 'password only required if use_trusted is false', default="")

        parser.add_argument('-pyodbc_driver', help= """name of the pyodbc drive to use i.e. "SQL SERVER 13" If no driver is specified, 
            will attempt to run sqlcmd direclty. This is not the preferred method""", default="")


        parser.add_argument('-f', help= 'Path to excel or csv file. Header must be present in file. if extension is .sql will run commands in the file directly')

        parser.add_argument('-sh',help= "List of rows to skip starting for top. For sqlcmd a --- is usually the second line. use -sh 1 to ignore if reading from csv that was created using sqlcmd direclty or exporting to .xlsx/.xls without specifying pyodbc_driver" , nargs='+', type=int )
        parser.add_argument('-sf',help= "Number of rows to skip starting for bottom. For sqlcmd a --- x rows affected is normally added at bottom. Use -sf 1 to ignore if reading from csv that was created using sqlcmd direclty or exporting to .xlsx/.xls without specifying pyodbc_driver" , nargs='+', type=int )

        parser.add_argument('-sexe', help= 'Optional. Skip execution of sql files generated from .xls, .xlsx or .csv files', action='store_true', default=False)


        parser.add_argument('-q', help= 'Raw query string. Make sure to wrap in quotes i.e. -q "Select 1 from table;"')

        o_help = """
            output file path. if pyodbc_driver is specified valid extenisons are .xls, .xlsx or .csv. i.e. ./pathToFileToWrite/Example.xlsx
            if .csv the delimiter to use can be specified by using -delim ","  The default is a comma. Any single character can be used
            as a delimiter
        """

        parser.add_argument('-o', help= o_help, default="")

        parser.add_argument('-odir', help= 'output directory for writing sql files generated from .xls, .xlsx and .csv')

        parser.add_argument('-v', help= 'Run program in verbose mode.', action='store_true' )

        parser.add_argument('-alias', help= """list of old_name new_name pairs where old_name is name of column in file
            example .xlsx has two column department and speciatly. to rename use
            -alias department DEPARTMENTS specialty Specialties. Use alias name if specifing data types for columns.        
        """, nargs="+", default = None)

        parser.add_argument('-set_fields', help= """Required for update i.e. -ctype u. list of column names used to create set argument.
        i.e. -set_fields department speciatly will create set department = department_value, specialty=specialty_value in sql files.
        name of columns should be names of alias columns if used
        """, nargs="+", default = None)

        parser.add_argument('-where_fields', help= """Required for update and delete i.e. -ctype u or -ctype d. list of column names used 
        to create where argument.i.e. -where_fields department speciatly will create 
        where department = department_value, specialty=specialty_value in sql files.
        name of columns should be names of alias columns if used
        """, nargs="+", default = None)

        parser.add_argument('-null', help= """list of column_names when missing should be set to sql server null value. Default behavior assumes value
        is a string and replaces values with 'NULL' where Null is a string. 
        """, nargs="+", default = None)

        parser.add_argument('-bsize', help="Batch size. Max number of sql commands sent in one file. 7000 appears to be the max allowed", default = 7000, type = int)

        help_std = """Date columns in excel are automatically converted to date time. In order to skip this effect use the -std flag. 
        If you only want the behavior for certain columns use -std col_name_ col_name_2
        """

        parser.add_argument('-std', help=help_std, default=False, const=True, nargs='?')

        parser.add_argument('-delim', help= 'delimiter for csv files', default=",")

        self.AddDtypes(parser)
        args = parser.parse_args()
        dargs = vars(args)
        self.CheckAndParseArgumentConditions(dargs)
        self.dargs = dargs

    def CheckAndParseArgumentConditions(self, dargs):
        """
        This check all conditional arguments and also parse arguments for downstream functions
        """

        #default use_trusted if u == "" and p == ""
        if not dargs['use_trusted'] and dargs['u'] == "" and dargs['p'] == "":
            dargs['use_trusted'] = True

        dargs['column_types'] = None
        if dargs['find_params']:
            if dargs['u'] == "" or dargs['p'] == "":
                print("username and password should be added to params when checking for all possible configurations")
            return

        if dargs['find_params_1']:
            if dargs['u'] == "" or dargs['p'] == "":
                print("username and password should be added to params when checking for all possible configurations")
            return

        if dargs['ld']:
            return

        if dargs['pbat']:
            return

        if dargs['ppy']:
            return

        if dargs['readme']:
            return

        #print help
        if not dargs['find_params'] and not dargs['find_params_1'] and not dargs['ld'] and not dargs['pbat'] and not dargs['ppy'] and dargs['f'] is None and dargs['q'] is None:
            raise Exception('No arguments specified use -h for help')

        if dargs['s'] == "" and not dargs['sexe']:
            raise Exception('The name of the server must be defined')

        #get file path
        if dargs['f'] is None and dargs['q'] is None:
            raise Exception('-f /path/to/file must be specified. or -q with query string')


        #add something for -q
        if not dargs['f'] is None:
            fp = dargs['f']
            if not os.path.exists(fp):
                raise Exception ('the specified path was not found: ' + fp)

            fext = pathlib.Path(fp).suffix
            if fext in ['.xls', '.xlsx', '.csv']:
                if dargs['odir'] is None:
                    em = """The output directory for where sql files should be written from data generated from input files
                    needs to be specified with -odir /path/to/output_dir 
                    """
                    raise Exception (em)
                mkdir(dargs['odir'])
                op = dargs['odir']
                if not os.path.exists(op):
                    raise Exception ('attempted to created directory path specified but failed. Make sure its a valid path for a directory: ' + op)

                if dargs['schema_name'] == "":
                    raise Exception ('schema_name must be defined.')


                if dargs['table_name'] is None:
                    tname = pathlib.Path(fp).stem
                    dargs['table_name'] = re.sub('[^a-zA-Z0-9_]', '', tname.replace(" ","_") )

        elif dargs['q'] is None:
            raise Exception ('-q or -f was not used. Nothing to do')

        if not dargs['use_trusted']:
            if dargs['u'] == "" or dargs['p'] == "":
                raise Exception("username and password must both be specified. Otherwise dont use either. Default has use_trusted set to true")

        if not dargs['alias'] is None:
            if len(dargs['alias']) % 2 != 0:
                raise Exception("alias list had uneven amount of entries make sure each old_column has a matching new_column name.")
            if len(dargs['alias']) > 0:
                alias_map = {}
                ax = dargs['alias']
                for i in range(0,len(ax),2):
                    alias_map[ax[i]] = ax[i+1]
                dargs['alias'] = alias_map

        # dargs['column_types'] = None
        column_types = {}
        for dtx in dtypex:
            if dargs[dtx] is None:
                continue
            column_names = dargs[dtx]
            for cn in column_names:
                column_types[cn] = dtx
        if len(column_types) > 0:
            dargs['column_types'] = column_types

        if dargs['ctype'] in ['u', 'd']:
            cx = dargs['ctype']
            if dargs['where_fields'] is None:
                raise Exception("-ctype " +x + "requires where_fields to be specified.")
            if cx == 'u':
                if dargs['set_fields'] is None:
                    raise Exception("-ctype -u requires set_fields to be specified.")


    def AddDtypes(self, parser):
        """
        Creates a list of flags for specifing data conversion types for reading from file.
        """
        for dtx in dtypex:
            arg = '-' + dtx
            helpx = 'list of columns to set as type '+dtx +'. ex: '+arg + ' column_name1 column_name2'
            parser.add_argument(arg, help=helpx, nargs="+")


if __name__ == '__main__':
    x = RunMain()
    x.InitializeParser()
    x.Run()
