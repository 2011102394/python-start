from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from typing import Optional

Base = declarative_base()


class AdministrativeArea(Base):
    __tablename__ = 'administrative_areas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    adcode = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    parent_adcode = Column(String(20), nullable=True, index=True)
    parent_name = Column(String(100), nullable=True)
    center = Column(String(100), nullable=True)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)
    children_num = Column(Integer, default=0)
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AdministrativeArea(adcode={self.adcode}, name={self.name}, level={self.level})>"


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def close(self):
        self.engine.dispose()