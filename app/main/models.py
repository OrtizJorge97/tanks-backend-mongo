"""from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship

Base = declarative_base()


class Users(Base):  # child table of companies
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    name = Column(String(20))
    last_name = Column(String(50))
    email = Column(String(40), unique=True, nullable=False)
    password = Column(Text)
    user_verified = Column(Boolean())
    role = Column(String(20))
    company_id = Column(Integer, ForeignKey('companies.id'))
    sessions = relationship('Sessions')


class Sessions(Base):  # child table of users
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    session_identifier = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))


class Companies(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    company = Column(String(30), nullable=False)
    address = Column(Text)
    users = relationship('Users')
    tanks = relationship('Tanks')


class Tanks(Base):  # child from companies
    __tablename__ = "tanks"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    tank_name = Column(String(30), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    tanks = relationship('Measures_Categories')
    measurements = relationship('Measurements')


class Measures_Categories(Base):  # child from tanks
    __tablename__ = "measures_categories"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    measure_type = Column(String(30), nullable=False)
    tank_min_value = Column(Float, nullable=False)
    tank_max_value = Column(Float, nullable=False)
    tank_id = Column(Integer, ForeignKey('tanks.id'))
    measurements = relationship('Measurements')


class Measurements(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    tank_id = Column(Integer, ForeignKey('tanks.id'))
    measures_categories_id = Column(Integer, ForeignKey('measures_categories.id'))"""
