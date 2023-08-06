import asyncio


async def main():
    f = asyncio.Future()
    f.set_result(1)

    print(await f)


asyncio.run(main())
