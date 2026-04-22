from sqlalchemy import Column, DateTime, ForeignKey, Float, Enum, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class SourceEnum(str, enum.Enum):
    NVD = "NVD"
    EXPLOIT_DB = "EXPLOIT_DB"
    HACKER_NEWS = "HACKER_NEWS"

# Родительская модель которая описывает поля принадлежащие каждой дочерней
class Threat(Base):
    __tablename__ = "threats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(Enum(SourceEnum), nullable=False)
    title = Column(String, nullable=False)
    link = Column(String, unique=True, nullable=False, index=True)
    published = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    cve_details = relationship("CVEDetails", back_populates="threat", uselist=False, cascade="all, delete-orphan")
    exploit_details = relationship("ExploitDetails", back_populates="threat", uselist=False, cascade="all, delete-orphan")

# Дочерние модели с уникальными полями
class CVEDetails(Base):
    __tablename__ = "cve_details"

    id = Column(UUID(as_uuid=True), ForeignKey("threats.id", ondelete="CASCADE"), primary_key=True)
    cve_id = Column(String, nullable=False, unique=True, index=True)
    cvss_score = Column(Float, nullable=True)
    vector = Column(String, nullable=True)

    threat = relationship("Threat", back_populates="cve_details")

class ExploitDetails(Base):
    __tablename__ = "exploit_details"

    id = Column(UUID(as_uuid=True), ForeignKey("threats.id", ondelete="CASCADE"), primary_key=True)
    platform = Column(String, nullable=True)
    exploit_code_link = Column(String, nullable=True, unique=True)

    threat = relationship("Threat", back_populates="exploit_details")