'''
Modification of sqlite3 to improve code visibility.

What does it have:
* class `Sql`
* function `secure_insert`

'''
try:
    import sqlite3
except: 
    print("This module needs the following packages: sqlite3")
    exit(1)

def secure_insert(cortege:tuple) -> tuple:
    '''
    Filters the tuple from forbidden words.
    Throws an exception if found.

    Parameters:
    * `cortege`: tuple - tuple.

    Returns:
    * tuple - a verified tuple.
    '''
    blocked = ["DROP", "DELETE", "INSERT"]
    for item in cortege:
        if isinstance(item, str):
            item = item.upper()
            for block in blocked:
                if block in item:
                    raise Exception("Forbidden expression in the tuple: {0}".format(str(block)))
    return cortege

class Sql:
    '''
    Initializes the sql class.

    Parameters:
    * `name`: str|None - your connection name.

    Attributes:
    * `name`: str - your connection name.
    * `queue`: list[int] - Request queue.

    Methods:
    * `connect`
    * `execute`
    * `commit`
    '''

    def __init__(self, name:str=None) -> None:
        self.queue = []
        self.name = name

    def connect(self, path:str=None) -> None: # ------------------------------------------------------------------------------------
        '''
        Connects the file to an instance of the class.

        Also creates some attributes in the class:
        * `connection`: sqlite3.Connection - sqlite3 connections
        * `cursor`: sqlite3.Cursor - sqlite3 cursor
        '''
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def execute(self, request:str, cortege:tuple=(), func=None) -> list:
        '''
        Executes the specified query in sqlite3.

        Parameters:
        * `request`: str - sql query.
        * `cortege`: tuple - tuple for inserting data using '?'.
        * `func`: function|None - the function that will be executed after the request is executed.

        Returns:
        * list - response to the request.
        '''
        id = len(self.queue) - 1
        self.queue.append(id)

        while True:
            if self.queue[0] == id:
                del self.queue[0]
                self.cursor.execute(request, cortege)
                _return = self.cursor.fetchall()
                if not func is None:
                    func()

                return _return

    def secure_execute(self, request:str, cortege:tuple=(), func=None) -> list:
        '''
        Executes the specified query in sqlite3 using its protection against database injections.

        Parameters:
        * `request`: str - sql query.
        * `cortege`: tuple - tuple for inserting data using '?'.
        * `func`: function|None - the function that will be executed after the request is executed.

        Returns:
        * list - response to the request.
        '''
        return self.execute(request, secure_insert(cortege), func)

    def commit(self) -> bool:
        '''
        confirm and save all changes to the database.

        Returns:
        * bool - are the saves successful.
        '''
        try:
            self.connection.commit()
            return True
        except:
            return False
