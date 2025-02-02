
from ..event import OrderEvent
from ..utils.log import logger

import os
import pandas as pd
import numpy as np
from collections import deque
import yaml
import pdb
#from numba import jit
log = logger('[OrderHandler]')



class OrderHandler(object):
    """
    1. 初始化持仓上限
    2. 查询并获得当前仓位
    3. 接受tick_event, 并决定是否生成OrderEvent, 加入队列
    """
    def __init__(self, event_queue, tick_handler, position_handler, limit_position, store_path=None):
        self.event_queue = event_queue
        self.tick_handler = tick_handler
        self.position_handler = position_handler
        self.store_path = store_path
        self.limit_position = limit_position
        self.init_order()


    def init_order(self):
        self.history_order_dict = {}
        self.history_order_quantity_df = pd.DataFrame()
        self.history_order_action_df = pd.DataFrame()
        

    def on_algo(self, event):
        if event.event_type == 'ALGO':
            self._update_timestamp(event)
            self._query_last_price()
            # 查询并获得当前仓位
            self._query_position()

            # 计算仓位变化，并生成OrderEvent，加入队列
            self._gen_order_event(event)

            self._update_order()



    def _query_last_price(self):
        self.sell_price_01 = self.tick_handler.get_sell_price_01()
        self.buy_price_01 = self.tick_handler.get_buy_price_01()
        self.ticker_names = self.tick_handler.get_ticker_names()


    def _query_position(self):
        """
        通过position_handler查询当前持仓
        """
        self.position = self.position_handler.get_position()
        self.book = self.position_handler.get_book()


    def _gen_order_event(self, event):
        """
        接受tick_event, 并决定是否生成OrderEvent, 加入队列
        """
        self.order_dict = {}
        for ticker in event.algo:
#             if event.algo[ticker] > 0 and self.book['现金'] > event.algo[ticker] * self.sell_price_01[ticker] * 50\
#                                       and self.sell_price_01[ticker] > 0:
            if event.algo[ticker] > 0 and self.sell_price_01[ticker] > 0:
                self.order_dict[ticker]={}
                self.order_dict[ticker]['证券代码'] = ticker
                self.order_dict[ticker]['委托日期'] = self.timestamp
                self.order_dict[ticker]['买卖方向'] = '买'
                self.order_dict[ticker]['委托数量'] = int(event.algo[ticker])
                self.order_dict[ticker]['委托状态'] = "未成交"
                self.order_dict[ticker]['订单类型'] = "正常委托"
                self.order_dict[ticker]['委托价格'] = self.sell_price_01[ticker]

            #elif event.algo[ticker] < 0 and self.position[ticker]['可用'] > 0 and self.buy_price_01[ticker]>0:
            elif event.algo[ticker] < 0 and self.buy_price_01[ticker]>0:

                self.order_dict[ticker]={}
                self.order_dict[ticker]['证券代码'] = ticker
                self.order_dict[ticker]['委托日期'] = self.timestamp
                self.order_dict[ticker]['买卖方向'] = '卖'
                self.order_dict[ticker]['委托数量'] = int(-1 * event.algo[ticker])
                self.order_dict[ticker]['委托状态'] = "未成交"
                self.order_dict[ticker]['订单类型'] = "正常委托"
                self.order_dict[ticker]['委托价格'] = self.buy_price_01[ticker]

        #if len(self.order_dict) > 0:
        order_event = OrderEvent(order_name=event.algo_name,
                                    order_dict=self.order_dict,
                                    timestamp=self.timestamp)
        self.event_queue.put(order_event)
        log.info(len(self.order_dict))
        return




    def _update_order(self):
        self.history_order_dict.update({self.timestamp:self.order_dict})




    def store(self):
        """
        存储order
        """
        log.info('store ...')
        store_path = os.path.join(self.store_path, 'order')
        if not os.path.exists(store_path):
            os.mkdir(store_path)

        order_df = pd.DataFrame()
        for timestamp in self.history_order_dict:
            order_df = order_df.append(pd.DataFrame(self.history_order_dict[timestamp]).T)
        order_df.to_csv(os.path.join(store_path, 'history_order.csv'))



    def _update_timestamp(self, event):
        self.timestamp = event.timestamp


    # 外部调用 ------------------------------------------------------------------------------------
    def get_order_dict(self):
        return self.order_dict


    def get_target_position(self):
        return self.target_position


    def get_hold_position(self):
        return self.hold_position


