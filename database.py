import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = 'news_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    url = Column(Text, unique=True, nullable=False)
    source = Column(String(100), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_selected = Column(Boolean, default=True)

class Setting(Base):
    __tablename__ = 'settings'

    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=True)

# 定義 SQLite 資料庫檔案路徑，放在專案根目錄
DB_PATH = os.path.join(os.path.dirname(__file__), 'news_brief.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 建立 SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=False)

# 建立 Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化資料庫與資料表"""
    Base.metadata.create_all(bind=engine)
    print("資料庫初始化完成。")

def clear_all_news():
    """清空所有新聞資料，確保每次抓取都是全新的列表"""
    db = SessionLocal()
    try:
        db.query(NewsItem).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清空資料庫時發生錯誤: {e}")
    finally:
        db.close()

def save_news_item(news_data: dict) -> bool:
    """
    儲存單筆新聞，包含去重邏輯（依據 url）。
    回傳 True 表示新增成功，回傳 False 表示已存在或發生錯誤。
    """
    db = SessionLocal()
    try:
        # 檢查是否已存在 (依據 URL 去重)
        existing_news = db.query(NewsItem).filter(NewsItem.url == news_data.get('url')).first()
        if existing_news:
            return False

        # 解析時間 (若有提供字串格式)
        pub_date = news_data.get('published_at')
        if isinstance(pub_date, str):
            try:
                # 嘗試簡單的日期解析，實際狀況可依爬蟲獲取的格式調整
                from dateutil import parser
                pub_date = parser.parse(pub_date)
            except Exception:
                pub_date = None

        # 新增
        new_item = NewsItem(
            title=news_data.get('title'),
            summary=news_data.get('summary'),
            category=news_data.get('category'),
            url=news_data.get('url'),
            source=news_data.get('source'),
            published_at=pub_date,
            is_selected=news_data.get('is_selected', True)
        )
        db.add(new_item)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"儲存新聞失敗: {e}")
        return False
    finally:
        db.close()

def get_news_by_category(category: str):
    """取得特定分類的新聞"""
    db = SessionLocal()
    try:
        return db.query(NewsItem).filter(NewsItem.category == category).order_by(NewsItem.published_at.desc()).all()
    finally:
        db.close()

def get_all_news():
    """取得所有新聞"""
    db = SessionLocal()
    try:
        return db.query(NewsItem).order_by(NewsItem.published_at.desc()).all()
    finally:
        db.close()
