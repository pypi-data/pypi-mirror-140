'''
Easy work with paths.

What does it have:
* class `Path`
* class `File`

'''

try:
    from sys import platform
    import os.path
except: 
    print("This module needs the following packages: sys, os")
    exit(1)

class File:
    '''
    Initializes the file class.

    Parameters:
    * `file`: str - file name.
    * `path`: str|None - path to file.

    Attributes:
    * `file`: list - full file name.
    * `name`: str - file name.
    * `extension`: str|None - file extension.
    '''
    def __init__(self, file:str, path:str|None=None):
        self.path = path
        self.file = file.split(".")
        self.name = self.file[0]
        try: self.extension = self.file[1]
        except: self.extension = None

    def open(self, mode:str="r", encoding:str="utf-8"):
        '''
        Opens a file.

        Parameters:
        * `mode`: str - opening mode.
        * `encoding`: tuple - file encoding mode.

        Returns:
        * IO - file object.
        '''
        return open(file=self.path + '.'.join(self.file), mode=mode, encoding=encoding)

class Win_path:
    '''
    Initializes the path class.

    Parameters:
    * `path`: str - full path.

    Attributes:
    * `all`: list - full path.
    * `file`: atools.path.file|None - file.
    * `directory`: list - directory to file.
    * `disk`: str|None - the drive letter.

    Supported operations:
    * `str(x)` - returns all path.
    * `x + y` - connects the paths into one.
    '''
    def __init__(self, path:str):
        self.all = path.replace("/", "\\").split("\\")

        if not os.path.isfile(path): 
            self.file = File("None")
            self.directory = self.all
        else:
            self.directory = self.all[:-1]
            self.file = File(self.all[len(self.all)-1], '\\'.join(self.directory))
            
        try: 
            if self.directory[0][-1:] == ":": 
                self.disk = self.all[0]
            else: self.disk = None
        except: pass

    def add(self, path:str) -> None:
        '''
        Adds another path to the path.

        Parameters:
        * `path`: str - path.
        '''
        self.__init__(str(self.__add__(type(self)(path))))

    def go_parent(self) -> None:
        '''
        Goes to the parent folder. 

        The file will be deleted at the same time.
        '''
        if len(self.directory) > 1:
            del self.directory[-1]
            if not self.file is None:
                self.file = None
    
    def __str__(self): return "\\".join(self.all)

    def __add__(self, other): 
        if isinstance(other, type(self)):
            directory = self.directory
            for i in other.directory:
                if i[-1:] == ":": pass
                else: directory.append(i)
            return Win_path("\\".join(directory))

class Lin_path(Win_path):
    '''
    Initializes the path class.

    Parameters:
    * `path`: str - full path.

    Attributes:
    * `all`: list - full path.
    * `file`: atools.path.file|None - file.
    * `directory`: list - directory to file.

    Supported operations:
    * `str(x)` - returns all path.
    * `x + y` - connects the paths into one.
    '''
    def __init__(self, path:str):
        self.all = path.replace("/", "\\").split("\\")

        if not os.path.isfile(path): 
            self.file = File("None")
            self.directory = self.all
        else:
            self.directory = self.all[:-1]
            self.file = File(self.all[len(self.all)-1], '\\'.join(self.directory))

    def __add__(self, other): 
        if isinstance(other, type(self)):
            directory = self.directory
            for i in other.directory:
                if i == "..": 
                    del directory[-1]
                elif i == ".": pass
                elif i == "~":
                    return other
                else: directory.append(i)
            return Lin_path("\\".join(directory).replace("\\\\", "\\"))

if platform == "win32": Path = Win_path
elif platform.replace("2", "") == "linux": Path = Lin_path
else: print("This platform has not been checked for errors in this module.")
