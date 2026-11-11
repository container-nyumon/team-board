"""チームの連絡板（team-board）。チームへの連絡を書き込むと一覧に出る。表示した回数を Redis で数える。"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import redis
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logger = logging.getLogger("uvicorn.error")

# 設定は環境変数で受け取る（値は .env に書く。.env.example を見本にする）
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
if not ADMIN_TOKEN:
    print("エラー: ADMIN_TOKEN が設定されていません（.env を確かめてください）", file=sys.stderr)
    sys.exit(1)

JST = timezone(timedelta(hours=9), "JST")
templates = Jinja2Templates(directory="templates")
engine = create_engine(
    f"postgresql+psycopg://postgres:{DB_PASSWORD}@db:5432/postgres", pool_pre_ping=True
)
cache = redis.Redis(host="cache", port=6379)


class Base(DeclarativeBase):
    pass


class Notice(Base):
    __tablename__ = "notices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(140))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(JST)
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    logger.info("データベース db と キャッシュ cache につながりました")
    yield


app = FastAPI(title="チームの連絡板", lifespan=lifespan)


@app.get("/")
def index(request: Request):
    views = cache.incr("views")
    with Session(engine) as session:
        notices = list(session.scalars(select(Notice).order_by(Notice.id.desc()).limit(50)))
    return templates.TemplateResponse(
        request, "index.html", {"notices": notices, "views": views, "jst": JST}
    )


@app.post("/")
def post(text: str = Form(..., min_length=1, max_length=140)):
    with Session(engine) as session:
        session.add(Notice(text=text.strip() or "（空白）"))
        session.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/admin")
def admin(request: Request, token: str = ""):
    ok = token == ADMIN_TOKEN
    with Session(engine) as session:
        count = len(list(session.scalars(select(Notice.id)))) if ok else 0
    return templates.TemplateResponse(
        request, "admin.html",
        {"ok": ok, "count": count, "views": int(cache.get("views") or 0)},
        status_code=200 if ok else 403,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
