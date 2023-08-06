import requests
import requests
import ssl
from urllib3 import poolmanager


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)



class HttpRequest:
    def __init__(self):
        pass

    def get(self,url,data="",cookies=None):
        session = requests.session()
        if "https://" in url:
            session.mount('https://', TLSAdapter())
        if cookies!=None:
            for k in cookies:
                session.cookies.set(k,cookies[k])
        res = session.get(url,data=data)
        return res

    def post(self,url,data,cookies=None):
        session = requests.session()
        if cookies!=None:
            for k in cookies:
                session.cookies.set(k,cookies[k])
        # print(session.cookies)
        if "https://" in url:
            session.mount('https://', TLSAdapter())
        res = session.post(url,data=data)
        return res
