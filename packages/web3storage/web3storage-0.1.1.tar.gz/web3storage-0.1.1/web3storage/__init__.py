import requests
from hashlib import sha256
# https://docs.web3.storage/reference/http-api/
# https://web3.storage/

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class Client:
    """
    Client to the web3.storage API
    """
    def __init__(self, api_key: str, endpoint: str='https://api.web3.storage'):
        self._endpoint = endpoint
        self._api_key = api_key
        self._request_auth = BearerAuth(api_key)

    def _set_api_key(self, new_api_key: str, return_old: bool=False):
        value = self._api_key if return_old else None
        self._api_key = new_api_key
        self._request_auth = BearerAuth(new_api_key)
        return value

    def upload_file(self, filename: str):
        """
        Upload a file to the web3.storage network.
        Takes a filename as an argument, returns json with a CID
        """
        encoded_filename = sha256(filename.encode()).hexdigest()
        r = requests.post(
            f'{self._endpoint}/upload',
            auth=self._request_auth,
            files={
                'file': open(filename, 'rb')
            }
        )
        return self._handle_response(r)

    def _handle_response(self, r: requests.Response) -> dict:
        if r.status_code == 200:
            data = r.json()
            return data
        try:
            data = r.json()
        except:
            pass
        if r.status_code == 400:
            raise RuntimeError(data or 'Response code 400')
        if r.status_code == 401:
            raise RuntimeError('401 Unauthorized')
        if r.status_code == 403:
            raise RuntimeError('403 Forbidden, make new session')
        if str(r.status_code).startswith('5'):
            raise RuntimeError(data or r.status_code)
        return data

    def list_uploads(self) -> list:
        """
        List all uploads to web3.storage from this user.
        Returns a list of CAR objects which can be accessed
        also like dicts but have more functionality
        """
        r = requests.get(f'{self._endpoint}/user/uploads', auth=self._request_auth)
        data = self._handle_response(r)
        return list(map((lambda c: CAR(self, c)), data))

    def download(self, cid: str) -> bytes:
        """
        Get the raw contents of a CAR from web3.storage
        via it's CID
        """
        r = requests.get(f'{self._endpoint}/car/{cid}', auth=self._request_auth)
        if not r.status_code == 200:
            self._handle_response(r)
        return r.content

class CAR:
    """
    Content Archive Object
    Attributes can be accessed like a dict
    """
    def __init__(self, client: Client, json: dict):
        self._client = client
        self._json = json
        self.cid = json['cid']
        self.dagSize = json['dagSize']
        self.created = json['created']
        self.pins = json['pins']
        self.deals = json['deals']

    def __getitem__(self, item):
        return self._json[item]

    def get_content(self) -> bytes:
        """
        Downloads the raw content from web3.storage
        """
        return self._client.download(self.cid)