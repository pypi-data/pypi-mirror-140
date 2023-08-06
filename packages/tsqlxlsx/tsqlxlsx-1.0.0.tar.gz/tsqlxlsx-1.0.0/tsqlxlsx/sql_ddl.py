import pandas as pd
import subprocess
import collections
import math
import pathlib
import os

class SqlDDL:
    """
    Used to create corresponding sql files for sql server processing. Uses column information from pandas dataframe to generate
    sql files

    Creates sql file to refresh data

    Quickstart:
    df   = pd.read_excel("./ExampleData.xlsx", dtype="string")
    csqlx  = SqlDDL(df, "test", "create",  "./test/create.sql", column_types={"id":"integer"})
    csqlx.CreateFiles()

    Parameters:
    df: pandas data frame object to use for create sql statements. All values should be set to string
        i.e. pd.read_excel("ExcelFile.xlsx",dtype="string")
    schema_name: name of schema/database
    table_name: Name of table to preform crud operations on
    column_types: dictionary {columnName: data_type} i.e. {"department": "text"} The columnName should be in the
        pandas dataframe. The data_type is a correpsonding sql data type. Column types are only needed when using
        create or create_insert crud_type. If column type is not specified text is used by default.


    crud_type: List of sql statements that can be created from dataframe. All require schema_name and table_name
        create: Drop/Create a new table. Optionally can specify column_types
        create_insert: Drop/Create a new table. Optionally can specify column_types. Also creates batch insert commands
            from data in the data frame.
        insert: creates batch insert commands from data in the data frame.
        update: creates batch update commands. Requires list of set_fields and list of where_fields to run
        delete: creates batch delete commands. Requires list of where_fields to run

    batchSize: 7000 How many crud statements per file.
    output_file_path: 

    set_fields: list of columns used to set new values on update crud operation. i.e. ["provider"] will create
        set [provider] = provider_value

    where_fields: list of columns used to specifiy query conditions for update/delete i.e. ["department","specialty"]
        will create: where [department] = department_value, [specialty] = specialty_value
    as_null: list of column names where an actual NULL value should be placed in sql file where appropriate. replaces
        df values with "none", "null", "", None with sql NULL

    sql_output_file_list: Stores list of absolute files paths to created files. Used to keep track of file order creation
        for batch file creation.
    """
    def __init__(self,df,schema_name  , table_name, crud_type,  output_file_path, batchSize = 7000, set_fields = None, where_fields = None, 
        column_types=None,  as_null = None ):
        self.df = df
        self.table_name = table_name
        self.crud_type = crud_type
        self.output_file_path = output_file_path
        self.batchSize = 7000
        self.set_fields = set_fields #should be list of columns to use as set value. should be name of column after alias
        self.where_fields = where_fields
        if column_types is None:
            column_types = {}
        self.column_types=column_types #key value pair. column name and type

        self.schema_name=schema_name
        #self.sqlFileList
        self.batch_list = None
        self.as_null = as_null #List of column names that should have NULL used in place of "NULL" pandas df null or ""
        self.sql_output_file_list = [] #stored in file creation order. Used for sending sql files to sql server in order.

    def CreateFiles(self):
        self.ValidateInputParameters()
        self.GetBatches()
        self.WriteFiles()

    def GetBatches(self):
        #Add loop based on index
        numLoops = math.ceil( len(self.df)/(1.0*self.batchSize) )
        batch_list = []
        print("Number of files to be created: "+str(numLoops))
        for i in range(0,numLoops):
            indexStart = i*self.batchSize
            indexEnd = (i+1)*self.batchSize
            ix = {'start_index': indexStart, 'stop_index': indexEnd}
            batch_list.append(ix)
        self.batch_list = batch_list

    def ValidateInputParameters(self):
        if self.crud_type not in ['create_insert', 'create', 'insert', 'update', 'delete']:
            pass
        if self.crud_type == 'update' and (self.set_fields is None or self.where_fields is None):
            raise Exception("set_fields and/or where_fields not defined for update")
        if self.crud_type == 'delete' and self.where_fields is None:
            raise Exception("where_fields not defined for delete")

        if self.batchSize <= 0:
            self.batchSize = 7000

    def WriteFiles(self):
        if self.crud_type == 'create_insert':
            self.WriteCreateInsertStatements()

        elif self.crud_type == 'create':
            self.WriteCreateStatement()

        elif self.crud_type == 'insert':
            self.WriteInsertStatements()

        elif self.crud_type == 'update':
            self.WriteUpdateStatements()

        elif self.crud_type == 'delete':
            self.WriteDeleteStatements()
        else:
            raise Exception("""No valid crud type select. if on command line use ci, c, i, u or d 
                which represent create_insert, create, insert, update and delete in the module""")

    #Write functions used for writing sql to file
    def WriteCreateInsertStatements(self):
        createStr = self.CreateDropStatement()
        insertStr = self.CreateInsertStatements()
        for i in range(0,len(self.batch_list)):
            bk = self.batch_list[i]
            insertSelectStr = self.CreateSelectStatements( bk['start_index'], bk['stop_index'])
            sqlString = None
            if i == 0:
                sqlString = '\n'.join( [createStr, insertStr, insertSelectStr] )
            else:
                sqlString = '\n'.join( [insertStr, insertSelectStr] )
            sqlFileName = self.CreateSqlFileNamePath(i)
            self.WriteSqlFileCommand(sqlFileName,sqlString)

    def WriteCreateStatement(self):
        createStr = self.CreateDropStatement()
        sqlFileName = self.CreateSqlFileNamePath(0)
        self.WriteSqlFileCommand(sqlFileName,createStr)

    def WriteDeleteStatements(self):
        for i in range(0,len(self.batch_list)):
            bk = self.batch_list[i]
            sqlString = self.CreateDeleteStatements( bk['start_index'], bk['stop_index'])
            sqlFileName = self.CreateSqlFileNamePath(i)
            self.WriteSqlFileCommand(sqlFileName,sqlString)
    
    def WriteInsertStatements(self):
        insertStr = self.CreateInsertStatements()
        for i in range(0,len(self.batch_list)):
            bk = self.batch_list[i]
            insertSelectStr = self.CreateSelectStatements( bk['start_index'], bk['stop_index'])
            sqlString = '\n'.join( [insertStr, insertSelectStr] )
            sqlFileName = self.CreateSqlFileNamePath(i)
            self.WriteSqlFileCommand(sqlFileName,sqlString)

    def WriteUpdateStatements(self):
        for i in range(0,len(self.batch_list)):
            bk = self.batch_list[i]
            sqlString = self.CreateUpdateStatements( bk['start_index'], bk['stop_index'])
            sqlFileName = self.CreateSqlFileNamePath(i)
            self.WriteSqlFileCommand(sqlFileName,sqlString)
    #End of Write functions used for writing sql to file

    #Create functions used to create sql strings
    def CreateUpdateStatements(self, indexStart, indexEnd):
        sql_list = []
        for index,row in self.df.iloc[indexStart:indexEnd].iterrows():
            set_string, where_string = self.UpdateSetWhereString(row)
            update_string = "UPDATE [{schema_name}].[{tableName}] set {set_string} where {where_string} ;".format(
                tableName=self.table_name, schema_name=self.schema_name, set_string=set_string, where_string=where_string)
            sql_list.append(update_string)
        return '\n'.join(sql_list)

    def CreateDeleteStatements(self, indexStart, indexEnd):
        sql_list = []
        for index,row in self.df.iloc[indexStart:indexEnd].iterrows():
            where_string = self.WhereString(row)
            delete_string = "DELETE FROM [{schema_name}].[{tableName}] where {where_string} ;".format(
                tableName=self.table_name, schema_name=self.schema_name, where_string=where_string)
            sql_list.append(delete_string)
        return '\n'.join(sql_list)

    def CreateInsertStatements(self):
        """
        The insert command is created with the defined columns entered in the order specified in
        self.column_types
        """
        insertString = "INSERT INTO [{schema_name}].[{tableName}] ".format(tableName=self.table_name, schema_name=self.schema_name)

        columnTypes = []
        for columnName in self.df.columns:
            columnTypes.append( "[{columnName}]".format(columnName=columnName) )

        columnTypesStr ='(' + ','.join(columnTypes)+')\n'
        insertString += columnTypesStr
        return insertString

    def CreateSelectStatements(self, indexStart, indexEnd):
        """
        Creates bulk insert string that allows for insert into sql server. This is where all the data from
        the excel file is transfered to the sql file. Union alls use older version syntax for sql server. So to do
        a bulk insert requires multiple select and Union Alls. 
        """
        columnTypes = []
        for columnName, dataType in self.df.iteritems():
            columnTypes.append( "{{{columnName}}}".format(columnName=columnName) )

        selectString ="SELECT " + ','.join(columnTypes)

        #begin adding data to sql sever string
        outList = [ ]
        for index,row in self.df.iloc[indexStart:indexEnd].iterrows():
            #string wrapping and unrapping here?
            rowx= self.StringifyPandasRow(row)
            x = selectString.format(**rowx)
            outList.append(x)

        outStr = "\nUNION ALL\n".join(outList) +';'
        return outStr


    def UpdateSetWhereString(self,row):
        """
        Creates where and set statements for sql string
        """
        rowx= self.StringifyPandasRow(row)
        set_list = []
        for sx in self.set_fields:
            set_list.append( "[{column_name}] = {value}".format(column_name=sx, value=rowx[sx])  )
        set_str = ', '.join(set_list)
        where_str = self.WhereString(row)
        return set_str, where_str

    def WhereString(self,row):
        """
        Creates where statements
        """
        where_list = []
        rowx= self.StringifyPandasRow(row)
        for sx in self.where_fields:
            where_list.append( "[{column_name}] = {value}".format(column_name=sx, value=rowx[sx])  )
        return ' and '.join(where_list)

    def CreateDropStatement(self):
        """
        Creates the conditional drop if and create table statemetns. Uses the column names and data types in self.columnFields to 
        define the table to be created
        """

        createTableString = """IF OBJECT_ID('[{schema_name}].[{tableName}]','U') IS NOT NULL DROP TABLE [{schema_name}].[{tableName}] ;
        CREATE TABLE [{schema_name}].[{tableName}] 
        ( """.format(tableName=self.table_name, schema_name=self.schema_name)
        columnTypes = []
        for columnName in self.df.columns:
            dataType = "varchar(2000)"
            if columnName in self.column_types:
                dataType = self.column_types[columnName]
            columnTypes.append( "[{columnName}] {dataType}".format(columnName=columnName, dataType=dataType) )

        columnTypesStr = ','.join(columnTypes)+' );\n'
        createTableString += columnTypesStr
        return createTableString
    #Create functions used to create sql strings


    def StringifyPandasRow(self, row):
        """
        Parse values for null statements and makes strings of all values. single quotes
        wrap all values.
        """
        rowx = {}
        as_null = self.as_null
        if as_null is None:
            as_null = []

        if not self.column_types is None:
            for key, value in self.column_types.items():
                if value in  ['bigint', 'numeric', 'smallint', 'int', 'float', 'real', 'date', 'datetime', 'datetime2', 'time']:
                    if key not in as_null:
                        as_null.append(key)

        for column_name in row.keys():
            value = row[column_name]
            # tx = self.IsNull(value)
            if column_name in as_null:
                if self.IsNull(value) :
                    rowx[column_name] = "NULL"
                else:
                    rowx[column_name] = "'"+str(value) +"'"
            else:
                rowx[column_name] = "'"+str(value) +"'"
        return rowx

    def IsNull(self, value):
        tmp_str = str(value) 
        if pd.isna(value) or pd.isnull(value) or value is None:
            return True
        elif tmp_str.lower() in ["null", "none", "", "nan", "nat"]:
            return True
        else:
            return False


    def CreateSqlFileNamePath(self, idx_num, ignore_index=False):
        """
        Used to rename output file if necessary. And add indexes.
        """
        fext = pathlib.Path(self.output_file_path).suffix
        new_ext = ''
        if not ignore_index:
            new_ext =  "_"+str(idx_num)
        if fext == "":
            new_ext += '.sql'
        else:
            new_ext += fext
            return self.output_file_path.split(fext)[0] + new_ext
        return self.output_file_path + new_ext

    def WriteSqlFileCommand(self,sqlFileName,sqlString):
        """
        Combines all the sql file strings together into one string. Writes the
        string to the specified sql file.
        """
        self.sql_output_file_list.append( os.path.abspath( sqlFileName) )
        fout = open(sqlFileName,'w')
        fout.write(sqlString)
        fout.close()

if __name__ == '__main__':
    df   = pd.read_excel("./ExampleData.xlsx") #, dtype="string")
    for columnName, columnData in df.iteritems():
        df[columnName] = df[columnName].astype(str)


    as_null = ['dates']
    column_types={"id":"int"}

    csqlx  = SqlDDL(df,"schema_name", "test", "create_insert",  "./test/create.sql",  as_null = as_null, column_types = column_types)
    csqlx.CreateFiles()

    # column_types={"id":"integer"},

    # cisqlx = SqlDDL(df,"schema_name", "test", "create_insert",  "./test/create_insert.sql", column_types={"id":"varchar(255)", "dates": "date" })
    # cisqlx.CreateFiles()

    isqlx = SqlDDL(df,"schema_name", "test", "insert",  "./test/insert.sql", column_types={"id":"int", "dates": "date" })
    isqlx.CreateFiles()
    # usqlx = SqlDDL(df,"schema_name", "test", "update",  "./test/update.sql", column_types={"id":"varchar(255)", "dates": "date" }, set_fields=["department"], where_fields=["id"])
    # usqlx.CreateFiles()
    # dsqlx = SqlDDL(df,"schema_name", "test", "delete",  "./test/delete.sql", column_types={"id":"varchar(255)", "dates": "date" }, where_fields=["id"])
    # dsqlx.CreateFiles()