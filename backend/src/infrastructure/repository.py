"""Reusable asynchronous repository primitives for ORM models."""

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase

from src.infrastructure.base import SoftDeleteMixin

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository with optional soft-delete support.

    Write operations commit by default. Pass ``commit=False`` to combine several
    operations in a caller-managed transaction.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    def _supports_soft_delete(self) -> bool:
        return issubclass(self.model, SoftDeleteMixin)

    def _query(self, *, include_deleted: bool = False) -> Select[tuple[ModelType]]:
        statement = select(self.model)
        if self._supports_soft_delete() and not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        return statement

    async def get(self, identifier: UUID, *, include_deleted: bool = False) -> ModelType | None:
        """Return one entity by primary key, or ``None`` when it is absent."""

        result = await self.session.execute(
            self._query(include_deleted=include_deleted).where(self.model.id == identifier)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[ModelType]:
        """Return a bounded collection of entities."""

        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")
        if not 1 <= limit <= 1_000:
            raise ValueError("limit must be between 1 and 1000")
        result = await self.session.execute(
            self._query(include_deleted=include_deleted).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        values: Mapping[str, Any],
        *,
        commit: bool = True,
    ) -> ModelType:
        """Create and persist an entity from validated column values."""

        entity = self.model(**dict(values))
        self.session.add(entity)
        await self._persist(entity, commit=commit)
        return entity

    async def update(
        self,
        entity: ModelType,
        values: Mapping[str, Any],
        *,
        commit: bool = True,
    ) -> ModelType:
        """Update mapped, non-primary-key attributes and persist the entity."""

        mapper = inspect(self.model)
        valid_columns = {column.key for column in mapper.columns if not column.primary_key}
        invalid_columns = set(values).difference(valid_columns)
        if invalid_columns:
            raise ValueError(f"Unknown or immutable fields: {sorted(invalid_columns)}")
        for key, value in values.items():
            setattr(entity, key, value)
        await self._persist(entity, commit=commit)
        return entity

    async def delete(
        self,
        entity: ModelType,
        *,
        commit: bool = True,
        hard_delete: bool = False,
    ) -> None:
        """Soft-delete supported models; otherwise permanently remove the row."""

        if self._supports_soft_delete() and not hard_delete:
            soft_deleted_entity = entity
            assert isinstance(soft_deleted_entity, SoftDeleteMixin)
            soft_deleted_entity.deleted_at = datetime.now(timezone.utc)
            await self._persist(entity, commit=commit)
            return
        await self.session.delete(entity)
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()

    async def restore(self, entity: ModelType, *, commit: bool = True) -> ModelType:
        """Restore a soft-deleted entity."""

        if not self._supports_soft_delete():
            raise TypeError(f"{self.model.__name__} does not support soft deletion")
        restorable_entity = entity
        assert isinstance(restorable_entity, SoftDeleteMixin)
        restorable_entity.restore()
        await self._persist(entity, commit=commit)
        return entity

    async def _persist(self, entity: ModelType, *, commit: bool) -> None:
        if commit:
            await self.session.commit()
            await self.session.refresh(entity)
        else:
            await self.session.flush()
