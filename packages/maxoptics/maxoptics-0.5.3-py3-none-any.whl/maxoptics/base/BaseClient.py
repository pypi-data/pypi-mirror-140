import atexit
import getpass
from maxoptics.common.httpio import HttpIO
from maxoptics.config import Config
from maxoptics.utils.base import error_print, info_print, success_print, warn_print


class BaseClient(HttpIO):
    def __init__(self, url_key, api_config_key, port_config_key, no_login=False) -> None:
        super().__init__(url_key, api_config_key, port_config_key)
        self.token = Config.Token
        if not self.token:
            if self.ping():
                if not no_login:
                    self.login()

    def ping(self):
        """ """
        params = {}

        info_print("Connecting to Server  %s" % Config.SERVERAPI, end=" ")
        result = self.post(**params)
        if result["success"] is False:
            error_print("Connection Failed, %s" % result["result"]["msg"])
            exit(0)
            # return False
        else:
            success_print("Succeed.")
            return True

    def login(self):
        """ """
        if Config.DEFAULTUSER:
            username = Config.DEFAULTUSER
        else:
            username = input("MaxOptics Studio Username:")
        if Config.DEFAULTPASSWORD:
            passwd = Config.DEFAULTPASSWORD
        else:
            passwd = getpass.getpass("Password:")
        params = {
            "name": username,
            "password": passwd,
        }
        result = self.post(**params)
        # self.thread_status = False
        if result["success"] is False:
            warn_print("Login failed, %s" % result["result"]["msg"])
            if Config.DEBUG:
                raise TimeoutError
            else:
                exit(0)
        else:
            self.token = result["result"]["token"]
            Config.Token = self.token
            info_print(username, " ", end=" ")
            success_print("Login Success.")
            info_print("Welcome to use MaxOptics Studio SDK")

    # @atexit.register(self)
    def logout(self):
        if self.token:
            params = {"token": self.token}
            self.post(**params)
            self.token = ""
            info_print("Logout successfully.")
        else:
            warn_print("You haven't login yet")
