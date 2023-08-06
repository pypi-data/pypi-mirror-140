import asyncio

from classiq._internals.client import client


def authenticate(overwrite: bool = False):
    asyncio.run(authenticate_async(overwrite))


async def authenticate_async(overwrite: bool = False):
    """Async version of `register_device`"""
    await client().authenticate(overwrite)
