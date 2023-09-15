# from sqlalchemy.ext import asyncio
# from sqlalchemy.orm import sessionmaker
#
# from src.api.database import (
#     # SQLALCHEMY_TEST_DATABASE_URL_async,
#     SQLALCHEMY_DATABASE_URL_async,
# )
#
# async_engine = asyncio.create_async_engine(
#     SQLALCHEMY_DATABASE_URL_async,
#     pool_pre_ping=True,
#     # echo=True,
#     # echo=settings.db_echo_log,
#     future=True,
# )
#
#
# AsyncSession = sessionmaker(  # type: ignore
#     autocommit=False,
#     autoflush=False,
#     bind=async_engine,
#     class_=asyncio.AsyncSession,
#     expire_on_commit=False
# )
