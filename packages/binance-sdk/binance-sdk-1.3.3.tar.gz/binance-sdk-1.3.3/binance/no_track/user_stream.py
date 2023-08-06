from binance import Client, SubType, BalanceUpdateHandlerBase, TradeHandlerBase
import asyncio

from test.private_no_track import (
    API_KEY,
    API_SECRET
)

client = Client(API_KEY, API_SECRET)


async def main():
    await client.subscribe(SubType.USER)

    class BalanceUpdateHandler(BalanceUpdateHandlerBase):
        def receive(self, msg):
            print('BalanceUpdateHandler', msg)

    client.handler(BalanceUpdateHandler())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.run_forever()


# class BalanceUpdateHandler(BalanceUpdateHandlerBase):
#     def receive(self, msg):
#         print('BalanceUpdateHandler', msg)


# print('is instance', isinstance(BalanceUpdateHandler(), TradeHandlerBase))
