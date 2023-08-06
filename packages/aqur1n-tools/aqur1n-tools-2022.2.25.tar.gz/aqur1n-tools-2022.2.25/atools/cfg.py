'''
Module for working with "cfg" files

What does it have:
* class `Cfg`
'''
from .basic import start_with, split

class Cfg:
    '''
    Class for working with cfg files

    Parameters:
    * `path`: str|None - the path to the cfg file.
    * `data`: str|None - if the "path" attribute is equal to ":data:" then this attribute is used as a config as a string.
    * `splt`: str|None - ...

    Attributes:
    * `parameters`: dict - parameters with sections.
    * `data`: str - config as a string.

    Methods:
    * `open`
    * `get`
    * `save`

    Supported operations:
    * `self[i]` - getting data using an index.
    * `self[i] = y` - assigning data using an index.
    * `del self[i]` - deleting data using an index.
    * `str(self)`
    * `iter(self)`
    * `reverse(self)`
    '''
    def __init__(self, path:str=None, data:str=None, splt:str="\n"):
        self.parameters = {}
        self.path = path
        self.split = splt

        def _read(lines:list):
            section = None
            ignore = False

            for line in lines:
                if start_with(line, ["!", "//"]): continue
                elif start_with(line, "/*"): ignore = True
                elif "*/" in line: 
                    ignore = False
                    continue
                    
                if start_with(line, "["): section = line[1:].split("]")[0]
                else: 
                    line = line.split("=")
                    if len(line) < 2: pass
                    elif not section is None and not ignore:
                        # Проверка существования секции в списке.
                        try: self.parameters[section] 
                        except: self.parameters[section] = {}

                        if start_with(line[1], ["'", '"']): self.parameters[section][line[0]] = split(line[1], ["'", '"'])[1]
                        else: self.parameters[section][line[0]] = split(line[1], ["//", "!"])[0]

                    elif not ignore:
                        
                        if start_with(line[1], ["'", '"']): 
                            self.parameters[line[0]] = split(line[1], ["'", '"'])[1]
                        else: self.parameters[line[0]] = split(line[1], ["//", "!"])[0]

        if path is None: return
        elif path == ":data:":
            _read(data.split(splt))
        else:
            with open(path, "r", encoding="utf-8") as file: 
                _read(file.read().split(splt))

    def open(path:str=None):
        '''
        This is an alias to `self.__init__()`.

        Parameters:
        * `path`: str|None - the path to the cfg file.

        Returns:
        * Cfg - instance of the class.
        '''
        return Cfg(path)

    def save(self, path:str=None) -> bool:
        '''
        Saves the class to a file.

        Parameters:
        * `path`: str|None - path to save.

        Returns:
        * bool - is it successful.
        '''
        _return = False
        if path is None: path = self.path

        text = ""

        for item in self.parameters:
            if type(self.parameters[item]) == dict: 
                text += "[{0}]\n".format(item)
                for i in self.parameters[item]:
                    if " " in str(self.parameters[item][i]): text += "{0}=\"{1}\"\n".format(str(i), str(self.parameters[item][i]))
                    else: text += "{0}={1}\n".format(str(i), str(self.parameters[item][i]))
            else:
                if " " in str(self.parameters[item]): text += "{0}=\"{1}\"\n".format(str(item), str(self.parameters[item]))
                else: text += "{0}={1}\n".format(str(item), str(self.parameters[item]))

        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
            _return = True
            
        return _return
        

    def get(self, key:int):
        '''
        Getting a parameter or section.

        Parameters:
        * `key`: int - the key of the parameter or section.

        Returns:
        * str|dict - parameter or section.
        '''
        return self.__getitem__(key)

    def __str__(self):
        string = ""
        for item in self.parameters:

            if type(self.parameters[item]) == dict:
                string += "[{0}]{1}".format(str(item), self.split)

                for i in self.parameters[item]: 
                    if " " in str(self.parameters[item][i]): value = '"{0}"'.format(str(self.parameters[item][i]))
                    else: value = str(self.parameters[item][i])

                    string += "{0}={1}{2}".format(str(i), value, self.split) 

            else: 
                if " " in str(self.parameters[item]): value = '"{0}"'.format(str(self.parameters[item][i]))
                else: value = str(self.parameters[item])
                
                string += "{0}={1}{2}".format(str(item), value, self.split)

        return string[:-len(self.split)]

    def __getitem__(self, key):
        return self.parameters[key]

    def __setitem__(self, key, value):
        self.parameters[key] = value

    def __delitem__(self, key):
        del self.parameters[key]

    def __iter__(self):
        return iter(self.parameters)

    def __reversed__(self):
        return list(reversed(self.parameters))
