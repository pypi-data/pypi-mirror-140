import inspect
import asyncio
import datetime

count = 5.0


async def display_date():
    loop = asyncio.get_running_loop()
    end_time = loop.time() + count
    while True:
        print(datetime.datetime.now())
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(1)

# asyncio.run(display_date())


print(inspect.iscoroutinefunction(display_date))


class Base(object):
    def a():
        pass


class A(Base):
    async def a():
        pass


print(inspect.iscoroutinefunction(Base().a))

print(inspect.iscoroutinefunction(A().a))


async def main():
    # no await
    task = asyncio.create_task(display_date())
    # display_date()
    print(task)

    await asyncio.sleep(count)
    # display_date()

asyncio.run(main())
# asyncio.create_task(display_date())

print('++++++++++')
