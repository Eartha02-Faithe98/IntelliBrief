import os
from google import genai
from google.genai import types

def get_gemini_client(api_key: str = None):
    """取得 Gemini Client，若無提供 key 則嘗試從環境變數讀取"""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("未提供 GEMINI_API_KEY")
    return genai.Client(api_key=key)

def generate_summary(text: str, api_key: str = None) -> str:
    """
    使用 Gemini 模型將長文本摘要為 3-5 點繁體中文。
    """
    # 針對沒有抓取到正文的狀況直接回傳原始提示
    if text.startswith("(無法自動提取") or text.startswith("(連線超時") or text.startswith("(請求失敗") or text.startswith("(提取內文發生"):
        return text
        
    try:
        client = get_gemini_client(api_key)
        
        prompt = (
            "請將以下新聞內文整理成 3 到 5 個關鍵重點的摘要。\n"
            "要求：\n"
            "1. 必須使用「繁體中文」輸出。\n"
            "2. 以條列式呈現（如：- 重點一）。\n"
            "3. 語氣專業、客觀。\n"
            "4. 如果內容過短或無意義，請簡單回覆「無法從提供內容產生有效摘要」。\n\n"
            f"新聞內文：\n{text[:4000]}" # 限制字數避免超過 token 上限
        )
        
        # 使用 gemini-2.5-flash 模型以兼顧速度與成本
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                "你是一位專業的產業分析師與新聞編輯。",
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500
            )
        )
        
        return response.text.strip()
        
    except ValueError as ve:
         return f"(AI 摘要產生失敗：{ve})"
    except Exception as e:
        print(f"產生摘要時發生錯誤: {e}")
        return f"(AI 摘要產生失敗：{e})"

