from asyncio import wrap_future

from argon2 import PasswordHasher

from src.security.exceptions import AppException

hasher = PasswordHasher()

async def hash_password(password, threadpool):
    """

    :param password:
    :param threadpool: app global threadpool
    :return:hashed password
    """
    # hashing is heavily cpu bound
    # wrapping this future to
    # event loop will prevent
    # api blocking
    return await wrap_future(threadpool.submit(hasher.hash, password))


async def verify_password(password, provided_password, threadpool):
    is_verified = await wrap_future(threadpool.submit(hasher.verify, password, provided_password))
    if not is_verified:
        raise AppException(
            error_message="Email or password missmatch",
            error_code="exceptions.emailOrPasswordMissmatch",
            status_code=401
        )
    return
