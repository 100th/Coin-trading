from autotrading.strategy.base_strategy import Strategy
from autotrading.machine.korbit_machine import KorbitMachine
from autotrading.machine.coinone_machine import CoinOneMachine
from autotrading.db.mongodb.mongodb_handler import MongoDBHandler
from autotrading.pusher.slack import PushSlack
import configparser, datetime, traceback, sys
from autotrading.logger import get_logger
import redis

logger = get_logger("step_trade")

class StepTrade(Strategy):

    def __init__(self, machine=None, db_handler=None, strategy=None, currency_type=None, pusher=None):
        if machine is None or db_handler is None or currency_type is None or strategy is None:
            raise Exception("Need to machine, db, currecy type, strategy")
        if isinstance(machine, KorbitMachine): #코빗 거래소 : 여기에 추가해야함
            logger.info("Korbit machine")
            self.currency_type = currency_type + "_krw"
        elif isinstance(machine, CoinOneMachine): #코인원 거래소 p198
            logger.info("CoinOne machine")
        self.machine = machine
        self.pusher = pusher
        self.db_handler = db_handler
        result = self.db_handler.find_item({"name":strategy},"trader","trade_strategy")
        self.params = result
        #prevent token call
        if self.params["is_active"]=="inactive":
            logger.info("inactive")
            return
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.token = self.redis.get(str(self.machine)+self.machine.get_username())

        if self.token == None:
            logger.info("set new token")
            saved_refresh_token = self.redis.get(str(self.machine)+self.machine.get_username()+"refresh")
            if saved_refresh_token is None:
                expire, token, refresh = self.machine.set_token(grant_type="password")
            else:
                self.machine.refresh_token = saved_refresh_token.decode("utf-8")
                expire, token, refresh = self.machine.set_token(grant_type="refresh_token")
            self.redis.set(str(self.machine)+self.machine.get_username(), token, expire)
            self.redis.set(str(self.machine)+self.machine.get_username()+"refresh", refresh, 3500)
            self.token = token
        else:
            self.token = self.token.decode("utf-8")
            self.machine.access_token = self.token

        logger.info(self.token)
        logger.info(self.currency_type)
        last = self.machine.get_ticker(self.currency_type)
        self.last_val=int(last["last"])
        self.last_24h_volume = float(last["volume"])

    def check_my_order(self):
        self.check_buy_ordered()
        self.check_buy_completed()
        self.check_sell_ordered()
        self.check_sell_completed()
        self.check_keep_ordered()

    def run(self):
        if self.params["is_active"]=="active":
            self.check_my_order()
            self.scenario()
        else:
            logger.info("inactive")

if __name__ == "__main__":
    mongodb = MongoDBHandler(mode="local", db_name="coiner", collection_name="price_info")
    korbit_machine = KorbitMachine()
    pusher = PushSlack()

    if len(sys.argv) > 0:
        trader = StepTrade(machine=korbit_machine, db_handler=mongodb, strategy=sys.argv[1], currency_type=sys.argv[2], pusher=pusher)
        trader.run()
