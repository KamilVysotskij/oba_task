from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Numeric,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

organization_activities = Table(
    'organization_activities',
    Base.metadata,
    Column(
        'organization_id',
        ForeignKey('organizations.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'activity_id',
        ForeignKey('activities.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Building(Base):
    __tablename__ = 'buildings'
    __table_args__ = (
        Index('ix_buildings_latitude_longitude', 'latitude', 'longitude'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(255), unique=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))

    organizations: Mapped[list[Organization]] = relationship(
        back_populates='building',
        cascade='all, delete-orphan',
    )


class Organization(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    building_id: Mapped[int] = mapped_column(
        ForeignKey('buildings.id', ondelete='RESTRICT'),
        index=True,
    )

    building: Mapped[Building] = relationship(back_populates='organizations')
    phones: Mapped[list[OrganizationPhone]] = relationship(
        back_populates='organization',
        cascade='all, delete-orphan',
    )
    activities: Mapped[list[Activity]] = relationship(
        secondary=organization_activities,
        back_populates='organizations',
    )


class OrganizationPhone(Base):
    __tablename__ = 'organization_phones'
    __table_args__ = (
        UniqueConstraint(
            'organization_id', 'phone', name='uq_organization_phones_org_phone'
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey('organizations.id', ondelete='CASCADE'),
        index=True,
    )
    phone: Mapped[str] = mapped_column(String(32), index=True)

    organization: Mapped[Organization] = relationship(back_populates='phones')


class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = (
        CheckConstraint(
            'level >= 1 AND level <= 3', name='ck_activities_level'
        ),
        UniqueConstraint(
            'parent_id', 'name', name='uq_activities_parent_name'
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('activities.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column()

    parent: Mapped[Activity | None] = relationship(
        'Activity',
        remote_side=lambda: Activity.id,
        back_populates='children',
    )
    children: Mapped[list[Activity]] = relationship(
        'Activity',
        back_populates='parent',
        cascade='all, delete-orphan',
    )
    organizations: Mapped[list[Organization]] = relationship(
        secondary=organization_activities,
        back_populates='activities',
    )
