from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News

async def is_news_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query=select(Favorite).where(Favorite.user_id==user_id,Favorite.news_id==news_id)
    result=await db.execute(query)
    #是否有收藏记录
    return result.scalar_one_or_none() is not None


async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 1. result.rowcount 报错：异步 SQLAlchemy Result 类型定义缺失 rowcount
#    解决：在行尾加 # type: ignore 或使用 returning + fetchall()
#这里原本是这样的
"""
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
    # 注意：异步 SQLAlchemy 的 Result 对象类型注解不含 rowcount，
    # 但运行时实际存在，所以加 # type: ignore 忽略 Pylance 检查。
"""
async def remove_news_favorite(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id).returning(Favorite.id)
    result = await db.execute(stmt)
    await db.commit()
    affected_rows = len(result.fetchall())  # 或 result.rowcount（运行时可用的）
    return affected_rows > 0

# 获取收藏列表：获取的是某个用户的收藏列表 + 分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 获取收藏列表 - 联表查询 join() + 收藏时间排序 + 分页
    # select(查询主体模型类, 字段别名).join(联合查询的模型类, 联合查询的条件).where().order_by().offset().limit()
    # 别名： Favorite.created_at.label("favorite_time")
    offset = (page - 1) * page_size
    # [
    #   (新闻对象, 收藏时间, 收藏id)
    # ]
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
             .join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
             .order_by(Favorite.created_at.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    #为什么用 result.all() 而不是 scalars().all()？
    #因为 scalars() 只会取第一列（即 News 对象），而你需要同时拿到 favorite_time 和
    # favorite_id。用 all() 返回的就是包含多个列的元组。
    rows = result.all()
    return rows, total

# 清空收藏列表：当前用户的收藏列表
async def remove_all_favorites(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id).returning(Favorite.id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回一个删除的数量
    affected_rows = len(result.fetchall())  # 或 result.rowcount（运行时可用的）
    return affected_rows or 0