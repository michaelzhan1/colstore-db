#!/usr/bin/python
import os


class TestFileWriter:
    """ A context manager for handling test files. It opens a file in the specified mode and ensures that it is properly closed after use.
    
    ### Attributes:
    - fname (str): The name of the file to be handled.
    - file (file object): The file object that is opened and handled by the context manager.
    """
    def __init__(self, n, ext, test_dir=""):
        """ Initializes the TestFileHandler with the specified mode, file number, extension, and optional test directory.
        
        ### Args:
        - n (int): The number to be included in the file name, formatted as a two-digit number.
        - ext (str): The extension of the file (e.g., 'txt', 'csv').
        - test_dir (str, optional): The directory where the test file is located. Defaults to an empty string, which means the current directory.
        """
        self.fname = os.path.join(test_dir, f"test{n:02d}gen.{ext}")
        self.file = None

    def __enter__(self):
        """ Opens the file in the write mode and returns the file object."""
        self.file = open(self.fname, 'w')
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        """ Ensures that the file is properly closed after use, even if an exception occurs.
        
        ### Args:
        - exc_type: The type of the exception (if any) that occurred within the context.
        - exc_value: The value of the exception (if any) that occurred within the context.
        - traceback: The traceback object (if any) that occurred within the context.
        """
        if self.file:
            self.file.flush()
            self.file.close()

class InputFileWriter(TestFileWriter):
    def __init__(self, n, test_dir=""):
        super().__init__(n, 'dsl', test_dir)

class ExpectedFileWriter(TestFileWriter):
    def __init__(self, n, test_dir=""):
        super().__init__(n, 'exp', test_dir)


def write_multiple(msg, *fs):
    """ Write a message to multiple file objects. Assumes file objects are opened."""
    for f in fs:
        f.write(msg)


def generate_header(dbName, tableName, numColumns):
    """ Generates a header line for a table with the specified number of columns.
    The header line will be in the format: dbName.tableName.col1, dbName.tableName.col2, ..., dbName.tableName.colN

    ### Args:
    - dbName (str): The name of the database.
    - tableName (str): The name of the table.
    - numColumns (int): The number of columns in the table.

    ### Returns:
    - list: A list of column names in the format dbName.tableName.colX where X is the column number starting from 1.
    """
    return [f"{dbName}.{tableName}.col{i}" for i in range(1, numColumns+1)]


def print_table(pandasArray):
    """ Converts a pandas DataFrame or Series to a string representation without headers and index.
    If the DataFrame or Series is empty, it returns an empty string.

    ### Args:
    - pandasArray (pd.DataFrame or pd.Series): The pandas DataFrame or Series to convert to a string.

    ### Returns:
    - str: A string representation of the DataFrame or Series without headers and index, or an empty string if the DataFrame or Series is empty.
    """
    if pandasArray.shape[0] == 0:
        return ''
    else:
        return pandasArray.to_string(header=False, index=False)
