from binance import Client, SubType, \
    TickerHandlerBase, KlineHandlerBase, AggTradeHandlerBase, TradeHandlerBase, \
    OrderBookHandlerBase, AllMarketMiniTickersHandlerBase, AllMarketTickersHandlerBase, HandlerExceptionHandlerBase, \
    OrderBook
import asyncio
print(__name__)


api_key = 'rlw4hb6MHcwePBFtNh8xMTRtwhKY7o2sCRnzBUbA74eJm0Z3R4z81stp3ufBAz7O'
api_secret = 'slcjNSnBJNfOrzwuAnA7pRzxfHHFUbUKfwRgWgdTXfoWUliHLM0EfFXQWKj77CTy'

# , SocketManager
# from binance.request.websockets import BinanceSocketManager

# import logging


async def main():
    # logging.basicConfig(filename='myapp.log', level=logging.DEBUG)

    client = Client(api_key)
    # client = Client()
    # print(await client.get_order_book(symbol='BTCUSDT'))
    # print(await client.get_products())

    class Handler(TradeHandlerBase):
        def receive(self, msg):
            data = super(Handler, self).receive(msg)
            print('depth')
            print(data)

    # class Handler(AllMarketTickersHandlerBase):
    #     def receive(self, msg):
    #         data = super().receive(msg)
    #         # print(a)
    #         print('tickers')
    #         print(data)

    # class KlineHandler(KlineHandlerBase):
    #     def receive(self, msg):
    #         data = super().receive(msg)
    #         print('Kline')
    #         print(data)

    # class Handler(OrderBookHandlerBase):
    #     def receive(self, msg):
    #         info, [bids, asks] = super(Handler, self).receive(msg)
    #         print(info)
    #         print(bids)
    #         print(asks)

    client.start()
    client.handler(Handler(), HandlerExceptionHandlerBase())

    await client.subscribe(SubType.TRADE, 'BTCUSDT')
    # print('subscriptions', await client.list_subscriptions())

    # orderbook = OrderBook('BTCUSDT', client=client)
    # await orderbook.updated()
    # print(orderbook.asks)

# asyncio.run(main())

loop = asyncio.get_event_loop()

loop.run_until_complete(main())
loop.run_forever()
