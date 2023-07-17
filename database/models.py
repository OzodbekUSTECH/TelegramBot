from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey, DateTime
from datetime import datetime

from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger, index=True, nullable=True)
    email = Column(String, index=True)
    password = Column(String)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="admin")
    posts = relationship("Post", back_populates="admin")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    name = Column(String)
    has_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_id = Column(Integer, ForeignKey('admins.id'))  # Добавлен внешний ключ admin_id
    admin = relationship("Admin", back_populates="users")
   


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
    
    admin_id = Column(Integer, ForeignKey('admins.id'))
    admin = relationship("Admin", back_populates="posts")

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
    photo_dir = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)

    video_dir = Column(String, nullable=True)
    video_url = Column(String, nullable=True)

    post = relationship("Post", back_populates="medias")
