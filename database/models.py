from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    caption = Column(String, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    is_published = Column(Boolean, default=False)
    is_media_group = Column(Boolean, default=False)
    send_type = Column(String, nullable=True)
    buttons = relationship("Button", back_populates="post")
    medias = relationship("Media", back_populates="post")
    
class Button(Base):
    __tablename__ = 'buttons'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    button_name = Column(String, nullable=True)
    button_url = Column(String, nullable=True)
    post = relationship("Post", back_populates="buttons")


class Media(Base):
    __tablename__ = 'medias'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    photo_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)

    post = relationship("Post", back_populates="medias")
