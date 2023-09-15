from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession


async def ping_db(session: AsyncSession) -> bool:
    try:
        await session.execute(select(text('1')))
    except Exception:
        # TODO write to log
        return False

    return True
