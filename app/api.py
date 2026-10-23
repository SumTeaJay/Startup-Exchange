from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Post, PostStatus, Response, ResponseStatus, User
from app.schemas import (LoginRequest, PostCreate, PostOut, ResponseCreate,
                          ResponseDecision, ResponseOut, TelegramAuthRequest,
                          TokenOut, UserOut)
from app.security import (create_access_token, decode_access_token,
                          validate_telegram_init_data, verify_password)
from app.config import get_settings

router = APIRouter(prefix="/api")
bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid access token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or missing")
    return user


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenOut(access_token=create_access_token(user.id), user=user)


@router.post("/auth/telegram", response_model=TokenOut)
def telegram_login(payload: TelegramAuthRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    try:
        telegram_user = validate_telegram_init_data(
            payload.init_data,
            settings.telegram_bot_token,
            settings.telegram_init_data_max_age_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    telegram_id = int(telegram_user["id"])
    user = db.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(
            telegram_id=telegram_id,
            email=f"telegram-{telegram_id}@local.invalid",
            password_hash="telegram-auth",
            name=telegram_user.get("first_name", "Telegram user"),
        )
        db.add(user)
    else:
        user.name = telegram_user.get("first_name", user.name)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@router.get("/posts", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list(db.scalars(select(Post).where(Post.status == PostStatus.PUBLISHED).order_by(Post.created_at.desc())))


@router.post("/posts", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    post = Post(author_id=user.id, **payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return post


@router.post("/posts/{post_id}/responses", response_model=ResponseOut, status_code=201)
def create_response(post_id: str, payload: ResponseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post.author_id == user.id:
        raise HTTPException(400, "Cannot respond to your own post")
    if post.status != PostStatus.PUBLISHED:
        raise HTTPException(409, "Post is closed")
    response = Response(post_id=post.id, applicant_id=user.id, **payload.model_dump())
    db.add(response)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "You already responded to this post") from exc
    db.refresh(response)
    return response


@router.get("/responses/sent", response_model=list[ResponseOut])
def sent_responses(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list(db.scalars(select(Response).where(Response.applicant_id == user.id).order_by(Response.created_at.desc())))


@router.get("/responses/received", response_model=list[ResponseOut])
def received_responses(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list(db.scalars(select(Response).join(Response.post).where(Post.author_id == user.id).order_by(Response.created_at.desc())))


@router.patch("/responses/{response_id}", response_model=ResponseOut)
def decide_response(response_id: str, payload: ResponseDecision, db: Session = Depends(get_db), user: User = Depends(current_user)):
    response = db.get(Response, response_id)
    if not response:
        raise HTTPException(404, "Response not found")
    if response.post.author_id != user.id:
        raise HTTPException(403, "Only the post author can decide")
    if payload.status == ResponseStatus.PENDING:
        raise HTTPException(400, "Decision must be accepted or rejected")
    response.status = payload.status
    db.commit()
    db.refresh(response)
    return response
