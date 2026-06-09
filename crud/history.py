from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News

async def add_history(
        db:AsyncSession,
        user_id:int,
        new_id:int
):
    query=select(History).where(History.user_id==user_id,History.news_id==new_id)
    result=await db.execute(query)
    existing_history=result.scalar_one_or_none
    if not existing_history:
        return existing_history
    else:
        history=History(user_id=user_id,new_id=new_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):

    offset = (page - 1) * page_size
    count_query=select(func.count(History.id)).where(History.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one()
    query = (select(News, History.view_time.label("view_time"), History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size))

    result = await db.execute(query)
    rows = result.all()
    return rows, total

# crud/history.py

async def delete_history_by_news(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """
    根据用户ID和新闻ID删除历史记录（前端传的是 news_id）
    
    使用 returning 子句让数据库返回被删除行的 id，
    然后通过 result.first() 是否有值来判断是否删除了记录。
    这样避免了 .rowcount 的类型警告问题。
    """
    stmt = (
        delete(History)
        .where(History.user_id == user_id, History.news_id == news_id)
        .returning(History.id)   # 返回被删除行的 id
    )
    result = await db.execute(stmt)
    await db.commit()
    
    # result.first() 返回第一行的第一列值（即被删除的 history.id）
    # 如果不为 None，说明成功删除了一条记录
    deleted = result.first() is not None
    return deleted

async def clear_history(db: AsyncSession, user_id: int) -> int:
    """
    清空当前用户的所有历史记录
    返回被删除的记录条数
    """
    # 删除后返回被删除行的 id，用于计数
    stmt = delete(History).where(History.user_id == user_id).returning(History.id)
    result = await db.execute(stmt)
    await db.commit()
    
    # fetchall() 返回所有被删除行的 id 列表，长度即为删除行数
    return len(result.fetchall())

  
   
    
 
        