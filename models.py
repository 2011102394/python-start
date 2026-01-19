"""
数据库模型定义模块

定义 SQLAlchemy ORM 模型类，用于映射到 PostgreSQL/PostGIS 数据库表
"""

from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from typing import Optional

# 创建 SQLAlchemy 基类
Base = declarative_base()


class AdministrativeArea(Base):
    """
    行政区域表模型
    
    映射到 administrative_areas 表，存储行政区划的基本信息和几何数据
    """
    
    # 表名
    __tablename__ = 'administrative_areas'
    
    # 主键 ID，自增长
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 行政区划编码，唯一约束，用于索引
    adcode = Column(String(20), unique=True, nullable=False, index=True)
    
    # 区域名称，用于索引
    name = Column(String(100), nullable=False, index=True)
    
    # 行政级别（country/province/city/district），用于索引
    level = Column(String(20), nullable=False, index=True)
    
    # 父级行政区划编码，用于建立层级关系，用于索引
    parent_adcode = Column(String(20), nullable=True, index=True)
    
    # 父级区域名称
    parent_name = Column(String(100), nullable=True)
    
    # 中心点坐标（JSON格式存储）
    center = Column(String(100), nullable=True)
    
    # 几何数据，使用 PostGIS 的 MULTIPOLYGON 类型，SRID 为 4326（WGS84）
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)
    
    # 子区域数量
    children_num = Column(Integer, default=0)
    
    # 原始 JSON 数据，用于存储完整的 GeoJSON 特征数据
    raw_data = Column(Text, nullable=True)
    
    def __repr__(self):
        """返回对象的字符串表示"""
        return f"<AdministrativeArea(adcode={self.adcode}, name={self.name}, level={self.level})>"


class DatabaseManager:
    """
    数据库管理器
    
    封装数据库连接、会话管理和表操作功能
    """
    
    def __init__(self, database_url: str):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接字符串
        """
        # 创建数据库引擎
        self.engine = create_engine(database_url, echo=False)
        # 创建会话工厂
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """创建数据库表"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """删除数据库表"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库引擎，释放资源"""
        self.engine.dispose()