from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Works(Base):
    __tablename__ = 'works'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_break = Column(Boolean, default=False)

    @hybrid_property
    def start_time_year(self):
        return self.start_time.year

    @start_time_year.expression
    def start_time_year(cls):
        return extract('year', cls.start_time)

    @hybrid_property
    def start_time_month(self):
        return self.start_time.month

    @start_time_month.expression
    def start_time_month(cls):
        return extract('month', cls.start_time)

    @hybrid_property
    def start_time_day(self):
        return self.start_time.day

    @start_time_day.expression
    def start_time_day(cls):
        return extract('day', cls.start_time)

    @hybrid_property
    def end_time_year(self):
        return self.end_time.year

    @end_time_year.expression
    def end_time_year(cls):
        return extract('year', cls.end_time)

    @hybrid_property
    def end_time_month(self):
        return self.end_time.month

    @end_time_month.expression
    def end_time_month(cls):
        return extract('month', cls.end_time)

    @hybrid_property
    def end_time_day(self):
        return self.end_time.day

    @end_time_day.expression
    def end_time_day(cls):
        return extract('day', cls.end_time)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    work_duration = Column(Integer, default=1500)
    break_duration = Column(Integer, default=300)



