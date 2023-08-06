#Parameters
import subprocess
import os
import pyodbc
import pandas as pd
import pathlib


try:
    from .data_loader import DataLoader
except ImportError:
    print("DataLoader failed to load. Export dataframes from sqlcmd will not work")

class TsqlConnect:
    """
    SQL Drivers can be found at: These are the executables for connecting to sql server.
    https://docs.microsoft.com/en-us/sql/connect/odbc/windows/release-notes-odbc-sql-server-windows?view=sql-server-ver15#previous-releases

    Module used to connect to tsql and run sql files either as a string or a list of files.

    Connection information in the TsqlConnection class comments. To find the connection parameters run:
    server = ''
    database =''
    username = ''
    password = ""

    tsqlx = TsqlConnect(server,database,  username = username,password =password, 
        useTrusted=True, pyodbcDriver ='', store_df=False, sqlCmdSep='^')
    tsqlx.FindCorrectConnection(first_hit=False)

    Use Trusted is the preferred option. This does not require the username and password to be stored. But sometimes
    the local computer configurations dont work. There are many possible drivers that can connect to the tsql server. 

    if useTrusted true params:
        useTrusted = True (preferred method. )
        server = ''
        database =''        
    else:
        username = ""
        password = ""
        server = ''
        database =''
 
    pyodbcDriver = if empty string will use the sqlcmd command line option. If a string specifying the driver.
        Will use the pyodbc driver with the the specified driver string. Example
        pyodbcDriver = "ODBC Driver 13 for SQL Server"
        or another driver.

    error_string stores all errors from running sql commands.

    sqlCmdSep: the delimiter used when running sqlCmd. Also the delimiter used if writing to text or csv file.

    store_df: Default false. Stores query output into dataframe. Mainly for select statements
    output_df: List of dfs where dataframes are store after every query execution.

    """
    def __init__(self,server,database, username = '',password ='', 
        useTrusted=True, pyodbcDriver ='', store_df=False, sqlCmdSep='^'):

        self.server = server
        self.database = database
        self.username  = username
        self.password  = password

        self.useSqlCmd = pyodbcDriver == ''
        self.pyodbcDriver = pyodbcDriver
        self.useTrusted = useTrusted
        self.error_string = ''
        #supplemental values?
        self.sqlCmdSep = sqlCmdSep #deliminter used when writing results to file from sqlCmd. Also used as output separator for text files?
        self.store_df = store_df #used to determine if query results will be saved as pandas dataframe:
        #For using sqlcmd the output file must be specified when running query
        #Need output file for sqlcmd and output file for .xlsx
        self.output_dfs = []

    def RunBatch(self, sqlFileList, sqlOutputFileList=None):
        """
        sqlFileList: list of file paths to sql input scripts
        sqlOutputFileList: optional list of full paths to send each query. The list path should match the 
            input paths in sqlFileList 1:1.
        """
        #change to current directory
        if self.InvalidInputValues():
            return
        if not sqlOutputFileList is None:
            if len(sqlOutputFileList) != len(sqlFileList):
                raise Exception("The list for sqlFileList and sqlOutputFileList must be the same")

        for i in range(0,len(self.sqlFileList) ):
            output_file = ""
            sqlFileName = self.sqlFileList[i]
            if not sqlOutputFileList is None:
                output_file = sqlOutputFileList[i]
            self.Run(sqlFileName, is_file=True, verbose=True, output_file=output_file)

    def Run(self,sqlFileName, is_file=True, verbose=True, output_file=""):
        #change to current directory
        if self.InvalidInputValues():
            return

        if self.useSqlCmd:
            self.RunSqlCmd(sqlFileName, is_file=is_file, verbose=verbose, output_file = output_file)
        else:
            self.RunPyodb(sqlFileName, is_file=is_file, verbose=verbose, output_file = output_file)

    def RunQuery(self):
        #Used to run a select statement and return results
        pass

    def InvalidInputValues(self):
        if self.server == "":
            print("No server specified")
            return True
        if self.database == "":
            print("No server specified")
            return True
        if not self.useTrusted:
            if self.username == "" or self.password == "":
                print("username or password is not defined.")
                return True
        else:
            if self.username != "" or self.password != "":
                print("username and password is not required when running in trusted mode")
                return True
        return self.InvalidPyodbcValues()

    def InvalidPyodbcValues(self):
        """
        Checks if pyodbcDriver provided is valid
        """
        if not self.useSqlCmd:
            if self.pyodbcDriver == '':
                print("sqlDriver is not defined. Please select the proper drivers from list below")
                print( pyodbc.drivers() )
                return True
            else:
                if self.pyodbcDriver not in pyodbc.drivers():
                    print(self.pyodbcDriver+" is not available. Please select correct driver from list below")
                    print(pyodbc.drivers())
                    return True
                else:
                    return False
        else:
            return False


    def RunSqlCmd(self,sqlFileName, is_file=True, verbose=True, output_file = ""):
        """
        #executes the sqlcmd command
        """
        sqlCmd = self.CreateSqlServerCmd(sqlFileName,is_file=is_file, output_file = output_file)
        if verbose:
            print(sqlCmd)
            print('ExceutingCommand: '+ sqlFileName)        
        # subprocess.run(sqlCmd)
        x = subprocess.run(sqlCmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if x.stdout:
            stdout = x.stdout.decode("utf-8")
            print(stdout)
            #For storing data
            if self.store_df or (output_file != "" and fext != ".csv"):
                sqlFileName = output_file
                fext = pathlib.Path(sqlFileName).suffix
                if fext == '.xls':
                    sqlFileName = sqlFileName.split('.xls')[0] +'.csv'
                elif fext == '.xlsx':
                    sqlFileName = sqlFileName.split('.xlsx')[0] +'.csv'

                dlx = DataLoader(sqlFileName, delimiter = self.sqlCmdSep, hasHeader=True, skiprows=[1], skipfooter=[1]  )
                dfx = x.LoadFile()
                if output_file != "" and fext != ".csv":
                    self.WriteDfToFile(dfx,output_file)
                if self.store_df:
                    self.output_dfs.append(df)

        if x.stderr:
            print("SQL Cmd Error")
            stderr = x.stderr.decode("utf-8")
            self.error_string = stderr
            raise Exception(stderr)

    def CreateSqlServerCmd(self,sqlStrFileName, is_file=True, output_file = ""):
        """
        #sqlCmd with trusted Connection?
        #creates the sqlcmd command to be run. Adds the username, password, and sqlfile to command string
        """
        sqlFileName = sqlStrFileName
        #if .xlsx or .xls replace with .csv
        if is_file:
            fext = pathlib.Path(sqlFileName).suffix
            if fext == '.xls':
                sqlFileName = sqlFileName.split('.xls')[0] +'.csv'
            elif fext == '.xlsx':
                sqlFileName = sqlFileName.split('.xlsx')[0] +'.csv'
            sqlCmd = 'sqlcmd -S {server} -d {database} -U "{username}" -P "{password}" -s "{seperator}" -W -G -I ' \
                '-i {sqlFile}'.format(seperator=self.sqlCmdSep,  username = self.username, password = self.password, server=self.server,database=self.database, sqlFile = sqlFileName)
            if self.useTrusted:
                sqlCmd = 'sqlcmd -S {server} -d {database} -E -s "{seperator}" -W -G -I ' \
                    '-i {sqlFile}'.format(seperator=self.sqlCmdSep, server=self.server, database=self.database, sqlFile = sqlFileName)
        else:
            sqlCmd = 'sqlcmd -S {server} -d {database} -U "{username}" -P "{password}" -s "{seperator}" -W -G -I ' \
                '-Q "{sqlStr}"'.format(seperator=self.sqlCmdSep, username = self.username, password = self.password, server=self.server,database=self.database, sqlStr = sqlFileName)
            if self.useTrusted:
                sqlCmd = 'sqlcmd -S {server} -d {database} -E -s "{seperator}" -W -G -I ' \
                    '-Q "{sqlStr}"'.format(seperator=self.sqlCmdSep, server=self.server, database=self.database, sqlStr = sqlFileName)

        if output_file != "":
            sqlCmd += " -o " +output_file

        return sqlCmd

    def RunPyodb(self,sqlStrFileName, is_file=True, verbose=True, output_file = ""):
        """
        sqlStrFileName: Path to sql file or if is_file=False the sql statement to be executed
        """
        sqlFileName = sqlStrFileName
        # print(self.pyodbcDriver)
        sqlDriverX = '{'+self.pyodbcDriver+'}'
        sqlConnString = "DRIVER={driver};".format(driver=sqlDriverX) + "SERVER={server};".format(server=self.server)+"DATABASE={database};".format(database=self.database)+ "UID={username};".format(username=self.username)+"PWD={password};".format(password=self.password)+"Authentication=ActiveDirectoryPassword;"
        #run connection using python back end trusted driver
        if self.useTrusted:
            sqlConnString = "DRIVER={driver};".format(driver=sqlDriverX) + "SERVER={server};".format(server=self.server)+"DATABASE={database};".format(database=self.database)+ "Authentication=ActiveDirectoryIntegrated;"

        sqlString = ""
        if is_file:
            sqlFile = open(sqlFileName)
            sqlString = sqlFile.read()
            sqlFile.close()
        else:
            sqlString = sqlStrFileName
        if verbose:
            print("Executing: "+sqlFileName)
            print(sqlConnString)
        try:
            conn = pyodbc.connect(sqlConnString)
            conn.autocommit=True
            cursor = conn.cursor()
            cursor.execute(sqlString)
            if output_file != "" or self.store_df:
                dfx = self.CreateDfFromPyodbQueryResults(cursor)
                if output_file != "":
                    self.WriteDfToFile(dfx,output_file)
                if self.store_df:
                    self.output_dfs.append(dfx)

            if verbose:
                print(str(cursor.rowcount) + " rows affected")

            #output file or df
            conn.close()
        except pyodbc.Error as e:
            print("SQL Pyboc cmd Error")
            self.error_string = e
            raise Exception(e)

    def CreateDfFromPyodbQueryResults(self, cursor):
        """
        Convert pyodbc driver data to df.
        """
        col_headers = [ i[0] for i in cursor.description ]
        rows = [ list(i) for i in cursor.fetchall()] 
        df = pd.DataFrame(rows, columns=col_headers)
        return df      

    def WriteDfToFile(self, df, output_file_path):
        """
        Writes data frame to file
        """
        fext = pathlib.Path(output_file_path).suffix
        if fext in ['.xls', '.xlsx']:
            df.to_excel(output_file_path, index=False)
        else:
            df.to_csv(output_file_path, sep=self.sqlCmdSep, index=False)


    def PrintPyodbcDrivers(self):
        print( pyodbc.drivers() )

    def FindCorrectConnection(self,first_hit=True):
        """
        #used to find right combination
        #run select 1; in order of most secure to least secure connection.
        #return command options for correct hits
        #if first_hit = True return results of first succesful run.
        """
        #Try Trusted Pyobc
        self.__AllFieldsRequiredForTestConn__()
        sxp = []
        username = self.username
        password = self.password
        is_hit = False
        for driverx in pyodbc.drivers():
            if self.SkipDriver(driverx):
                continue
            px = {'pyodbcDriver': driverx, 'useTrusted': True}
            self.ChangeParams(px)
            try:
                self.RunPyodb("Select 1;", is_file=False)
                sxp.append(px)
                if self.error_string == "":
                    is_hit = True
                    print("Connection Succesful with parameters: ", px )
                    if first_hit:
                        return
            except:
                pass

        px = {'pyodbcDriver': '', 'useTrusted': True}
        self.ChangeParams(px)
        try:
            self.RunSqlCmd("Select 1;", is_file=False)
            if self.error_string == "":
                is_hit = True
                px = {'pyodbcDriver': "", 'useTrusted': True}
                sxp.append(px)
                print("Connection Succesful with parameters: ", px )
                if first_hit:
                    return
        except:
            pass


        for driverx in pyodbc.drivers():
            if self.SkipDriver(driverx):
                continue
            px = {'pyodbcDriver': driverx, 'useTrusted': False, 'username': username, 'password': password}
            self.ChangeParams(px)
            if self.InvalidInputValues():
                continue
            try:
                self.RunPyodb("Select 1;", is_file=False)
                is_hit = True
                sxp.append(px)
                if self.error_string == "":
                    print("Connection Succesful with parameters: ", px )
                    if first_hit:
                        return
            except:
                pass

        px = {'pyodbcDriver': "", 'useTrusted': False, 'username': username, 'password': password}
        self.ChangeParams(px)

        if not self.InvalidInputValues():
            try:
                self.RunSqlCmd("Select 1;", is_file=False)
                if self.error_string == "":
                    print("Connection Succesful with parameters: ", px )
                    sxp.append(px)
                    if first_hit:
                        return
            except:
                pass

        if not is_hit:
            print("No combination of connections were succesful")
        else:
            print("Some Succesful Combinations")
            for x in sxp:
                print(x)

    def ChangeParams(self, params):
        if 'pyodbcDriver' in params:
            self.pyodbcDriver = params['pyodbcDriver']

        if 'useTrusted' in params:
            self.useTrusted = params['useTrusted']

        if 'username' in params:
            self.username = params['username']

        if 'password' in params:
            self.password = params['password']

        self.error_string = ''

    def SkipDriver(self, driver_name):
        skip_list = ['Microsoft', 'PostgresSQL','Amazon'] 
        for dx in skip_list:
            if dx in driver_name:
                return True
        return False


    def __AllFieldsRequiredForTestConn__(self):
        if self.username  == "" or self.password  == "":
            print('username and password must be defined for test connections. will skip testing that requires username and password. Only test trusted')

if __name__ == '__main__':
    server = ''
    database =''
    username = ''
    password = ""

    tsqlx = TsqlConnect(server,database,  username = username,password =password, 
        useTrusted=True, pyodbcDriver ='', store_df=False, sqlCmdSep='^')
    tsqlx.FindCorrectConnection(first_hit=False)