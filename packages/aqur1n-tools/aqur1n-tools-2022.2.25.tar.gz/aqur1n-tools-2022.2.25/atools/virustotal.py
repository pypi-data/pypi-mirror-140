'''
...
'''

try:
    import requests
except: 
    print("This module needs the following packages: requests")
    exit(1)

API_URL = r'https://www.virustotal.com/vtapi/v2/'

class VirusTotal:
    '''
    ...
    '''
    def __init__(self, api_key):
        self.params = dict(apikey=api_key)

    def _check(self, scan_id):
        url = API_URL + r"file/report"
        self.params["resource"] = scan_id

        response = requests.get(url, params=self.params)
        if response.status_code == 200: return response.json()
        else: 
            self._check(scan_id)
            

    def file(self, path):
        '''
        ...
        '''
        url = API_URL + r"file/scan"

        with open(path, 'rb') as file:
            files = dict(file=(path, file))
            response = requests.post(url, files=files, params=self.params)

            if response.status_code == 200: return self._check(response.json()["scan_id"])
            else: return response.status_code
        