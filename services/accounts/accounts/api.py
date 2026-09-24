"""Запросы, которые умеет обрабатывать сервис клиентов."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from accounts.db import get_session
from accounts.models import Account
from accounts.schemas import AccountCreate, AccountRead, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Клиенты"])


def _get_or_404(session: Session, account_id: int) -> Account:
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент {account_id} не найден",
        )
    return account


@router.post(
    "",
    response_model=AccountRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать клиента",
)
def create_account(payload: AccountCreate, session: Session = Depends(get_session)) -> Account:
    account = Account(**payload.model_dump())
    session.add(account)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Клиент с адресом {payload.email} уже существует",
        ) from None
    session.refresh(account)
    return account


@router.get("", response_model=list[AccountRead], summary="Список клиентов")
def list_accounts(
    session: Session = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Account]:
    stmt = select(Account).order_by(Account.id).limit(limit).offset(offset)
    return list(session.scalars(stmt))


@router.get("/{account_id}", response_model=AccountRead, summary="Получить клиента")
def get_account(account_id: int, session: Session = Depends(get_session)) -> Account:
    return _get_or_404(session, account_id)


@router.patch("/{account_id}", response_model=AccountRead, summary="Изменить клиента")
def update_account(
    account_id: int,
    payload: AccountUpdate,
    session: Session = Depends(get_session),
) -> Account:
    account = _get_or_404(session, account_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Клиент с таким адресом уже существует",
        ) from None
    session.refresh(account)
    return account


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить клиента",
)
def delete_account(account_id: int, session: Session = Depends(get_session)) -> None:
    account = _get_or_404(session, account_id)
    session.delete(account)
    session.commit()
