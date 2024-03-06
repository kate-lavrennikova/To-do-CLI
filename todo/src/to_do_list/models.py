from sqlalchemy import ForeignKey, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from .database import Base 

class User(Base):
    __tablename__ = "app_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(20), unique=True)
    user_password: Mapped[str] = mapped_column(String(20))
    

class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"))
    task_date: Mapped[date]
    task_description: Mapped[str] = mapped_column(String(150))
    done: Mapped[bool]
    important: Mapped[bool]
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now())

    def __str__(self):
        done = "\u2611" if self.done else "\u2610"
        important = "\u22C6" if self.important else " "
        return f"{self.task_date}  {self.id}  {done}  {self.task_description}  {important}"
    
    def __eq__(self, obj) -> bool:
        return self.user_id == obj.user_id and \
        self.task_date == obj.task_date and \
        self.task_description == obj.task_description and \
        self.done == obj.done and \
        self.important == obj.important and \
        self.timestamp == obj.timestamp

class UserSession(Base):
    __tablename__ = "user_session"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"))
    last_updated: Mapped[datetime]