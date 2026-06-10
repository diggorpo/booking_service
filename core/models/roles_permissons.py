from sqlalchemy import Column, ForeignKey, Table

from core.models.base import Base

roles_permissions = Table(
    "roles_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permissions_id", ForeignKey("permissions.id"), primary_key=True),
)
