from abc import ABC, abstractmethod
import datetime
from autotrading.logger import get_logger

logger = get_logger("base_strategy")

class Strategy(ABC):
    @abstractmethod
    def run(self):
        pass

    def update_trade_status(self, db_handler=None, item_id=None, value=None):
        pass
    def order_buy_transaction(self, machine=None, db_handler=None, currency_type=None, item=None, order_type="limit"):
        pass
    def order_sell_transaction(self, machine=None, db_handler=None, currency_type=None, item=None, order_type="limit"):
        pass
    def order_cancel_transaction(self, machine=None, db_handler=None, currency_type=None, item=None):
        pass
