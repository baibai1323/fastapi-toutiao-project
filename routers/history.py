from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response
from crud import history
from schemas.history import HistoryAddRequest, HistoryNewsItemResponse, HistoryListResponse


router=APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(data: HistoryAddRequest,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """
    添加历史记录
    """
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=result)

@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    """
    获取历史记录列表
    """
@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    
    history_list = []
    for news,view_time, history_id in rows:
    # 使用 model_validate 从 ORM 对象转换（利用 from_attributes=True）
    # 避免手动构造字典导致类型不匹配（dict vs Pydantic model）
        item = HistoryNewsItemResponse.model_validate(news)
    # 补上收藏专用字段（不在 News 模型中）
        item.history_id = history_id
        item.view_time = view_time
        history_list.append(item)
    
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取历史浏览列表成功", data=data)

@router.delete("/delete/{news_id}")
async def delete_history(
    news_id: int,                        # 改：参数名与路径参数一致
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除历史记录（根据新闻ID，因为前端传的是 news_id）
    注意：一个用户对同一篇新闻只有一条历史记录，所以可以直接按 user_id + news_id 删除
    """
    result = await history.delete_history_by_news(db, user.id, news_id)  # 改：调用新函数
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message="删除成功")

@router.delete("/clear")
async def delete_history_all(
    news_id: int,                        # 改：参数名与路径参数一致
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count=await history.clear_history(db,user.id)
    return {success_response(message=f"清空了{count}条记录")}