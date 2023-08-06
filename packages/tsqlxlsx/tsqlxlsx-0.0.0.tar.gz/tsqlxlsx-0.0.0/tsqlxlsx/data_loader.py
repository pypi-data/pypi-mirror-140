import pandas as pd
import pathlib
import re

class DataLoader:
    """
    Used to load data from excel, csv or text file and add to pandas object

    All data in dataframe is stored as string. User should convert to specific type if needed.

    QuickStart:
    input_file_path = './ExampleData.xlsx' 
    x = DataLoader(input_file_path)
    df = x.LoadFile()
    print(df)

    Input Paramters:
    Load data into pandas dataframe. This data will be processed for creating transact sql files.

    input_file_path: file of input excel, csv or text file. Must have correct delimiter
    delimiter: deliminter for text or excel file
    formatFunction: Preprocessing done to excel or text files. All columns will be a string type.
    hasHeader: has header rows
    skipRows: list or row numbers to skip. starting from top. list of rows i.e. [1,2]
    skipFooter: list of row number to skip starting from botton. list of rows i.e. [1,2]
    df: pandas object that stores data from excel/text file
    alias: object with df column and name of column to rename it to. i.e. {"dept": "Department"} if dept is name
        of column in data frame will be replace with Department. Columns are renamed before custom format function is
        run. so make sure to use values in alias for columns if using format function
    """
    def __init__(self,input_file_path, delimiter = ',', formatFunction = None, hasHeader=True, skipHeaderRows=None, skipFooterRows=None, stripDateTime=True,
        alias=None  ):
        self.input_file_path = input_file_path
        self.delimiter = delimiter
        self.formatFunction = formatFunction #input is the dataframe for self.df
        self.hasHeader = hasHeader
        self.skipHeaderRows = skipHeaderRows
        self.skipFooterRows = skipFooterRows
        self.stripDateTime = stripDateTime #If true or list
        self.alias = alias
        self.df = None

    def LoadFile(self):
        """
        Main function to run and return data file in pandas format
        """
        self.RunDataPull()
        return self.df

    def RunFormatFunction(self):
        """
        Run user defined format function to add or modify rows pulled from text file or excel. The formatFunction passed
        should take a dataframe as an object and do any processing required before returning back to user.

        All changes to the dataframe should be saved in the input object dataframe. So if using pandas functions
        used the inplace=True flag.

        This is the final function ran when using LoadFile.
        """
        if self.formatFunction is None:
            return
        df = self.df
        self.formatFunction(df)

    def RunDataPull(self):
        """
        Load and process data from excel, csv or text file.
        """
        self.LoadDataFrame()
        self.FillNa()
        self.ReplaceSingleQuote()
        self.StripTimeFromDateTime()
        self.RenameColumns()
        self.RunFormatFunction()

    def RenameColumns(self):
        """
        self.alias is a dictionary. Key value pairs are the original column names in pandas dataframe
        and new column new to replace it with
        """
        if self.alias is None:
            return
        self.df.rename(columns=self.alias, inplace=True)

    def LoadDataFrame(self):
        """
        pulledDataFrame = None
        fext = pathlib.Path(self.input_file_path).suffix

        if fext in ['xls', 'xlsx']:
            pulledDataFrame = pd.read_excel(self.input_file_path)
        else:
            pulledDataFrame = pd.read_csv(self.input_file_path, delimiter = self.delimiter)        
        """
        fext = pathlib.Path(self.input_file_path).suffix
        params = self.LoadParams(fext)
        self.df = self.__LoadDataFrame__(params, fext)

    def LoadParams(self, fext):
        """
        Converts all columns to string. Add additional parameters for reading
        file by pandas
        """
        params = {'dtype': str, 'parse_dates': False}
        if not self.hasHeader:
            params['header'] = None
        if self.skipHeaderRows != None:
            params['skiprows'] = self.skipHeaderRows
        if self.skipFooterRows != None:
            params['skipfooter'] = self.skipHeaderRows
        if self.delimiter != '' and fext not in ['.xls', '.xlsx']:
            params['delimiter'] = self.delimiter
        return params

    def __LoadDataFrame__(self, params, fext):
        #read excel or text/csv based on file extension
        fext = pathlib.Path(self.input_file_path).suffix
        if fext in ['.xls', '.xlsx']:
            df = pd.read_excel(self.input_file_path , **params)
            for columnName, columnData in df.iteritems():
                df[columnName] = df[columnName].astype(str)
            return df
        else:
            df = pd.read_csv(self.input_file_path , **params)
            for columnName, columnData in df.iteritems():
                df[columnName] = df[columnName].astype(str)
            return df


    def FillNa(self):
        """
        Fill empty rows with empty string
        """
        self.df.fillna('', inplace=True)

    def ReplaceSingleQuote(self):
        """
        Checks to see if any value in the excel/text file contains a single quote. Single quotes need to be escaped
        for by '' for including in sql file
        """
        #if xlsx
        fext = pathlib.Path(self.input_file_path).suffix
        for columnName, columnData in self.df.iteritems():
            self.df[columnName] = self.df[columnName].str.replace(u"’", u"'")

        keys = self.df.keys()
        for index, row in self.df.iterrows():
            for key in keys:
                value = row[key]
                if "'" in value:
                    self.df.at[index,key] = value.replace("'","''")

    def StripTimeFromDateTime(self):
        """
        Checks to see if any value in the excel/text file contains a single quote. Single quotes need to be escaped
        for by '' for including in sql file

        Assumes trailing zeros should be ignored. Can specify columns if need to keep
        """
        if self.stripDateTime == False:
            return
        elif isinstance(self.stripDateTime, list):
            for columnName in self.stripDateTime:
                self.df[columnName] = self.df[columnName].str.replace('00:00:00$', '', regex=True)        

        for columnName, columnData in self.df.iteritems():
            self.df[columnName] = self.df[columnName].str.replace('00:00:00$', '', regex=True)

if __name__ == '__main__':
    input_file_path = './ExampleData.xlsx' 
    x = DataLoader(input_file_path, delimiter = ',', formatFunction = None, hasHeader=True, skipHeaderRows=None, skipFooterRows=None, stripDateTime=True  )
    df = x.LoadFile()
    x.StripTimeFromDateTime()
    df['concat'] = df['Billing'] + df['Collections']
    print(df)

    input_file_path = './ExampleData.csv' 
    x = DataLoader(input_file_path, delimiter = ',', formatFunction = None, hasHeader=True, skipHeaderRows=None, skipFooterRows=None)#, stripDateTime=False)
    df = x.LoadFile()
    x.StripTimeFromDateTime()
    print(df)