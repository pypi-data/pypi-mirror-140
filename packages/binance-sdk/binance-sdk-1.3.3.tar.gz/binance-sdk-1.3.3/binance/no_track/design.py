from binance import Client

# host
#
c = Client()

c.start()

c.set_handler(b.TickerHandlerBase())

c.get_cur_kline()

c.get_order_book()

c.stop()

c.close()
