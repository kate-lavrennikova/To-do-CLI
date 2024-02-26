from .database import Base 
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
class User(Base):
    __tablename__ = "app_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(20))
    user_password: Mapped[str] = mapped_column(String(20))
    

        

class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"))
    task_date: Mapped[date]
    task_description: Mapped[str] = mapped_column(String(150))
    done: Mapped[bool]
    important: Mapped[bool]

    def __repr__(self):
        done = "Done" if self.done else "Not done"
        important = "!" if self.important else " "
        return f"{self.id}  {self.task_description}  {self.task_date}  {done}  {important}"

class UserSession(Base):
    __tablename__ = "user_session"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"))
    last_updated: Mapped[datetime]