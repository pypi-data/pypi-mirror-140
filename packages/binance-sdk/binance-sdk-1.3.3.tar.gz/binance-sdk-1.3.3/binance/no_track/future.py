# from concurrent.futures import Future
import asyncio


async def wait(f):
    print('before wait f')
    ret = await f
    print('f done')
    return ret


async def make_complete(f):
    print('make complete begin')
    await asyncio.sleep(2)
    f.set_result(1)
    return 2


async def main():
    f = asyncio.Future()
    ret = await asyncio.gather(f, make_complete(f))
    print(ret)

asyncio.run(main())
