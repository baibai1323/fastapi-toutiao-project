from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI代理"])

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

class ChatRequest(BaseModel):
    messages: list
    model: str = "qwen-plus"

@router.post("/chat")
async def proxy_chat(request: ChatRequest):
    if not DASHSCOPE_API_KEY:
        raise HTTPException(status_code=500, detail="API Key 未配置")
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-SSE": "enable"   # 保持流式
    }
    payload = {
        "model": request.model,
        "messages": request.messages,
        "stream": True
    }
    
    # 使用 httpx 转发流式响应
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(DASHSCOPE_URL, json=payload, headers=headers)
    
    # 直接返回响应内容（流式）
    return Response(content=resp.content, media_type="text/event-stream")