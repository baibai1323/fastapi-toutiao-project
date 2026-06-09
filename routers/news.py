# routers/news.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from crud import news_cache

router = APIRouter(prefix="/api/news", tags=["news"])

# 接口实现流程说明
# 1. 模块化路由 → API 接口规范文档
# 2. 定义模型类 → 数据库表（数据库设计文档）
# 3. 在 crud 文件夹里面创建文件，封装操作数据库的方法
# 4. 在路由处理函数里面调用 crud 封装好的方法，响应结果


@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取新闻分类列表（已集成缓存）"""
    categories = await news_cache.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories
    }


@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取新闻列表（分页，已集成缓存）"""
    offset = (page - 1) * page_size
    # 优先从缓存读取列表（内部已处理异常，失败时回退数据库）
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻详情
    - 优先从缓存读取，未命中则查数据库并写入缓存
    - 浏览量增加独立提交，失败不影响本次返回
    - 相关新闻也走缓存
    """
    # 1. 获取新闻详情（缓存层内部已处理异常，不会因缓存失败而中断）
    news_detail = await news_cache.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 2. 增加浏览量（独立事务，内部 commit，失败只记录日志，不抛异常）
    try:
        await news.increase_news_views(db, news_detail.id)
    except Exception as e:
        # 浏览量更新失败不应该阻断返回，打印日志即可
        print(f"[WARN] 新闻 {news_id} 浏览量更新失败: {e}")

    # 3. 获取相关新闻（已集成缓存）
    related_news = await news_cache.get_related_news(db, news_detail.id, news_detail.category_id)

    # 4. 返回数据（注意：views 是缓存中的旧值，但无伤大雅，下次刷新会更新）
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }