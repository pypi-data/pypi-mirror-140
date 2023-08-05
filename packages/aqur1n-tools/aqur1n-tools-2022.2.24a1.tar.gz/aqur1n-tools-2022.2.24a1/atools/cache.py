'''
Adds the "Cache" class, which makes it possible to quickly save and receive data.

What does it have:
* class `Cache`
'''

try:
    from datetime import datetime
except: 
    print("This module needs the following packages: datetime")
    exit(1)

class Cache:
    '''
    Initializes the cache class.

    Parameters:
    * `type`: any - list type.

    Attributes:
    * `type`: any - list type.
    * `cached`: list - list.

    Methods:
    * `add`
    * `get`
    * `delete`
    * `clear`
    '''

    def __init__(self, type):
        self.cached = []
        self.type = type

    def _error(self):
        raise Exception("Another type of data.")

    async def add(self, item):
        '''
        Adds time-bound data to the end of the cache. 

        It is possible to send a list with data for quick insertion.

        Parameters:
        * `item`: Cache.type|list - The item to insert.

        Returns:
        * if the type is "Cache.type": `int` - index of the element.
        '''
        if isinstance(item, self.type): 
            self.cached.append([item, datetime.now()])
            return len(self.cached)-1
        elif isinstance(item, list):
            [self.cached.append([x, datetime.now()]) if isinstance(x, self.type) else self._error() for x in item]
        else: raise self._error()
    
    def get(self, index:int) -> any:
        '''
        Get data from the cache.

        Parameters:
        * `index`: int - the index of the desired item.

        Returns:
        * Cache.type - object.
        '''
        return self.cached[index][0]

    def delete(self, index:int) -> None:
        '''
        Deletes an item from the cache under the desired index.

        Parameters:
        * `index`: int - item index.
        '''
        del self.cached[index]

    async def clear(self, date:datetime) -> None:
        '''
        Clear items that are older than the specified time.

        Parameters:
        * `date`: datetime.datetime - Date.
        '''
        i = len(self.cached)-1
        while True: 
            if self.cached[i][1] <= date: 
                del self.cached[i]
            else: break

            if i >= 1: i -= 1
            else:break