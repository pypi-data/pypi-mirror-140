"""pythonic hdfs client
"""
import requests

# from hdfs import InsecureClient,Client
import hdfs
from khalinox import config, utils
from urllib.parse import urljoin
import os

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _webhdfs_url(knox_url: str, path="gateway/default/webhdfs/v1") -> str:
    # return "https://obitedhs-vcs001.equant.com:8443/gateway/default/webhdfs/v1"
    return urljoin(knox_url, path)


def hdfs_client(myconfig: config.Config) -> hdfs.InsecureClient:
    # context to use with knox simple user/password auth
    session = requests.Session()
    session.verify = myconfig.verify
    # https://docs.python-requests.org/en/master/user/advanced/#session-objects
    session.auth = (myconfig.user, utils.decrypt(myconfig._key, myconfig.password))
    return hdfs.InsecureClient(url=_webhdfs_url(myconfig.knox_url), session=session)


class KnoxHdfs(hdfs.Client):
    """Use login/password from ENV variable to authenticate via Knox

    ENV variables expected:
    - HDFSCLI_USER
    - HDFSCLI_PASSWORD
    - HDFSCLI_URL
    - HDFSCLI_VERIFY (False by default)
    """

    def __init__(self, url, **kwargs):
        user = os.environ.get("HDFSCLI_USER")
        password = os.environ.get("HDFSCLI_PASSWORD")
        verify = os.environ.get("HDFSCLI_VERIFY", False)
        session = requests.Session()
        session.verify = verify
        # https://docs.python-requests.org/en/master/user/advanced/#session-objects
        session.auth = (user, password)
        super(KnoxHdfs, self).__init__(url, session=session, **kwargs)
