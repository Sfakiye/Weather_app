import sqlite3
class DBCM:
    """
    Database Context Manager (DBCM) for handling SQLite database connections.
    This class simplifies database interactions by automatically managing
    connections, cursors, and transactions.
    """
    def __init__(self, db_name):
        """
        Initialize the database context manager with the database name.
        :param db_name: Name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = None  # Database connection object
        self.cursor = None  # Cursor for executing SQL queries
    def __enter__(self):
        """
        Open a connection to the database and return a cursor.
        :return: SQLite cursor for executing queries.
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Handle exit operations for the context manager.
        Commits changes if no exceptions occur; otherwise, rolls back transactions.
        Closes the cursor and the database connection.
        :param exc_type: Exception type, if an exception occurred.
        :param exc_value: Exception value, if an exception occurred.
        :param exc_traceback: Exception traceback, if an exception occurred.
        """
        if exc_type is None:
            self.conn.commit()  # Commit changes if no error
        else:
            self.conn.rollback()  # Rollback changes in case of an error
        self.cursor.close()
        self.conn.close()