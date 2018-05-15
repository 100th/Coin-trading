import requests
import time
from autotrading.machine.base_machine import Machine
import configparser

class KorbitMachine(Machine):
    """
    코빗 거래소와 거래를 위한 클래스입니다.
    BASE_API_URL은 REST API호출의 기본 URL입니다.
    TRADE_CURRENCY_TYPE은 코빗에서 거래가 가능한 화폐의 종류입니다.
    """
    BASE_API_URL = "https://api.korbit.co.kr"
    TRADE_CURRENCY_TYPE = ["btc", "bch", "btg", "eth", "etc", "xrp", "krw"]

    def __init__(self):
        """
        KorbitMachine 클래스의 최초 호출 메소드입니다.
        config.ini에서 client_id, client_secret, username, password 정보를 읽어옵니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.CLIENT_ID = config['KORBIT']['client_id']
        self.CLIENT_SECRET = config['KORBIT']['client_secret']
        self.USER_NAME = config['KORBIT']['username']
        self.PASSWORD = config['KORBIT']['password']
        self.access_token = None
        self.refresh_token = None
        self.token_type = None

    def get_token(self):
        """액세스토큰 정보를 받기 위한 메소드입니다.
        Returns:
            인증토큰(asscee_token)이 있는 경우 반환합니다.

        Raises:
            access_token이 없는 경우 Exception을 발생시킵니다.
        """

        if self.access_token is not None:
            return self.access_token
        else:
            raise Exception("Need to set_token")

    def set_token(self, grant_type="password"):
        """액세스토큰 정보를 만들기 위한 메소드입니다.

        Returns:
            만료시간(expire),인증토큰(access_token),리프레쉬토큰(refresh_token) 을 반환합니다.

        Raises:
            grant_type이 password나 refresh_token이 아닌 경우 Exception을 발생시킵니다.
        """
        token_api_path = "/v1/oauth2/access_token"

        url_path = self.BASE_API_URL + token_api_path
        if grant_type == "password":
            data = {"client_id":self.CLIENT_ID,
                    "client_secret":self.CLIENT_SECRET,
                    "username":self.USER_NAME,
                    "password":self.PASSWORD,
                    "grant_type":grant_type}
        elif grant_type == "refresh_token":
            data = {"client_id":self.CLIENT_ID,
                    "client_secret":self.CLIENT_SECRET,
                    "refresh_token":self.refresh_token,
                    "grant_type":grant_type}
        else:
            raise Exception("Unexpected grant_type")

        res = requests.post(url_path, data=data)
        result = res.json()
        self.access_token = result["access_token"]
        self.token_type = result["token_type"]
        self.refresh_token = result["refresh_token"]
        self.expire = result["expires_in"]
        return self.expire, self.access_token, self.refresh_token

    def get_ticker(self, currency_type=None):
        """마지막 체결정보(Tick)을 얻기 위한 메소드입니다.

        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.

        Returns:
            결과를 딕셔너리로 반환합니다.
            결과의 필드는 timestamp, last, bid, ask, high, low, volume이 있습니다.

        Raise:
            currency_type이 없으면 Exception을 발생시킵니다.
        """
        if currency_type is None:
            raise Exception('Need to currency type')
        time.sleep(1)
        params = {'currency_pair':currency_type}
        ticker_api_path = "/v1/ticker/detailed"
        url_path = self.BASE_API_URL + ticker_api_path
        res = requests.get(url_path, params=params)
        response_json = res.json()
        result={}
        result["timestamp"] = str(response_json["timestamp"])
        result["last"] = response_json["last"]
        result["bid"] = response_json["bid"]
        result["ask"] = response_json["ask"]
        result["high"] = response_json["high"]
        result["low"] = response_json["low"]
        result["volume"] = response_json["volume"]
        return result
