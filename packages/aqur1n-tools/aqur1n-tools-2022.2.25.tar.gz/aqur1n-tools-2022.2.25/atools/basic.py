'''
It includes several small functions.

What does it have:
* function `get_directory`
* function `start_with`
'''

def get_directory() -> str:
    '''
    Get the directory of the current file.

    Returns:
    * str - path
    '''
    return "\\".join(__file__.split("\\")[:-2])

def start_with(string:str, chunk) -> bool:
    '''
    Checks whether the string starts with the right characters.

    Parameters:
    * `string`: str|list - the string that needs to be checked.

    Returns:
    * bool - will it start with this.
    '''
    if isinstance(chunk, str):
        if string[:len(chunk)] == chunk: return True
        else: return False
    else:
        for i in chunk:
            if string[:len(i)] == i: return True
        return False

def split(string:str, separate:list) -> list:
    '''
    Divides the string into parts.

    Parameters:
    * `string`: str - a string to split.
    * `separate`: list - a delimited list.

    Returns:
    * list - a split list.
    '''
    list = string
    if isinstance(list, str): list = list.split(separate[0])
    
    for sep in separate:
        ls = []
        for i in list:
            [ls.append(x) for x in i.split(sep)]
        list = ls
    return list
