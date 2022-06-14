import asyncio
import datetime


async def do_stuff_periodically(interval, periodic_function, *args, **kwargs):
    """
    Раз в interval запускает задание periodic_function с аргументами args, kwargs.
    """
    while True:
        await asyncio.gather(
            asyncio.sleep(interval),
            periodic_function(*args, **kwargs),
        )


def utcnow() -> datetime.datetime:
    """Возвращает текущие дату и время в UTC с указанием часового пояса."""
    return datetime.datetime.now(datetime.timezone.utc)
