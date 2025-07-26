from sqlalchemy import Column, String, BigInteger
from .db import Base

class Image(Base):
    __tablename__ = "images"
    google_drive_id = Column(String(128), primary_key=True, index=True)
    name            = Column(String(512), nullable=False)
    size            = Column(BigInteger, nullable=False)
    mime_type       = Column(String(128), nullable=False)
    storage_path    = Column(String(1024), nullable=False)
    source          = Column(String(32), nullable=False, default="google-drive")
