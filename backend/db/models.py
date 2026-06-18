from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Campaign(Base):
    __tablename__ = "campaigns"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal       = Column(Text, nullable=False)
    brief      = Column(JSONB)
    status     = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True))

class Post(Base):
    __tablename__ = "posts"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id  = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    platform     = Column(String(50))
    content      = Column(Text)
    image_url    = Column(Text)
    status       = Column(String(20), default="draft")
    feedback     = Column(Text)
    published_at = Column(DateTime(timezone=True))
    created_at   = Column(DateTime(timezone=True))

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id      = Column(String(100))
    post_id     = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    agent_name  = Column(String(50))
    input       = Column(JSONB)
    output      = Column(JSONB)
    tokens_used = Column(Integer)
    duration_ms = Column(Integer)
    created_at  = Column(DateTime(timezone=True))

class Analytics(Base):
    __tablename__ = "analytics"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id     = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    platform    = Column(String(50))
    likes       = Column(Integer, default=0)
    comments    = Column(Integer, default=0)
    shares      = Column(Integer, default=0)
    clicks      = Column(Integer, default=0)
    reach       = Column(Integer, default=0)
    recorded_at = Column(DateTime(timezone=True))

class ImageIteration(Base):
    __tablename__ = "image_iterations"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id    = Column(UUID(as_uuid=True), ForeignKey("posts.id"))
    iteration  = Column(Integer, default=1)
    prompt     = Column(Text)
    image_url  = Column(Text)
    feedback   = Column(Text)
    status     = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True))
