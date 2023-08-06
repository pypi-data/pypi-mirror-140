"""Interact with hive through JDBC

Reference:
- https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.5/integrating-hive/content/hive_connection_string_url_syntax.html
"""
from pathlib import Path
import jaydebeapi
from loguru import logger
from typing import Union
from khalinox import config, utils
from urllib.parse import urlencode, urlparse


def connect(myconfig: config.Config) -> Union[jaydebeapi.Connection, None]:
    """Interact with hive using jdbc

    Raises:
        ValueError: for bad user/password
    """
    host = urlparse(myconfig.knox_url)
    url = _make_connection_str(host.netloc, myconfig.hive_jdbc)
    try:
        return jaydebeapi.connect(
            myconfig.hive_jdbc.driver_class,
            url,
            {
                "user": myconfig.user,
                "password": utils.decrypt(myconfig._key, myconfig.password),
            },
        )

    # this kind of exception seems to come from java somehow
    # and does not raise a specific one in python
    # pylint: disable=broad-except
    except Exception as e:
        if "code: 401" in str(e):
            user = myconfig.user
            basemsg = (
                "\nCannot authenticate against Knox/HiveServer (401).\n"
                "Please check your user/password"
            )
            # common mistake, user provide `MYUSER` instead of `myuser`
            if user.isupper():
                extra = (
                    f"\nSuggestion: your login `{user}` is in upper case,"
                    f"try in lower case (`{user.lower()}`)"
                )
                msg = basemsg + extra
            else:
                msg = basemsg
            logger.critical(msg)
            raise ValueError("Bad credential") from None
        elif "code: 500" in str(e):
            logger.critical("Internal error with Hive. Most Likely due to Hive outage")
            raise ValueError("Hive server Error") from None
        else:
            raise e


def _make_connection_str(host: str, hiveconf: config.HiveJDBC) -> str:
    """Build JDBC connection string
    `jdbc:hive2://<host>:<port>/<dbName>;<sessionConfs>?<hiveConfs>#<hiveVars>`

    Args:
        host: include port,e.g `myhost.com:8884`
    """
    hive_vars = urlencode(hiveconf.hive_vars)
    return (
        f"jdbc:hive2://{host}/;"
        f"ssl=true;sslTrustStore={hiveconf.trust_store};"
        f"trustStorePassword={hiveconf.store_password};"
        f"transportMode=http;httpPath=gateway/default/hive?{hive_vars}"
    )
