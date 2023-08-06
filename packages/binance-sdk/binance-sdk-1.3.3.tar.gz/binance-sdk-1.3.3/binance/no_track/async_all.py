import asyncio


async def b():
    print('b')
    c


async def a():
    print('a')
    await asyncio.sleep(1)
    print('a end')


async def main():
    ta = asyncio.create_task(a())
    tb = asyncio.create_task(b())

    try:
        await asyncio.gather(tb, ta)
    except Exception as e:
        print(e)

    # print(ta)

# asyncio.run(main())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
