"""
配置管理模块

提供应用配置管理功能，包括数据库连接、API 参数等配置项
"""

import os
from typing import Optional
from urllib.parse import quote_plus


class Config:
    """
    应用配置类
    
    管理应用的各种配置参数，支持环境变量配置
    """
    
    # 数据库连接字符串（优先使用环境变量）
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    
    # 数据库连接参数
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')  # 数据库主机地址
    DB_PORT: str = os.getenv('DB_PORT', '5432')      # 数据库端口
    DB_NAME: str = os.getenv('DB_NAME', 'geo_data')  # 数据库名称
    DB_USER: str = os.getenv('DB_USER', 'postgres')  # 数据库用户名
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'arsc123!@#')  # 数据库密码
    
    # 应用配置参数
    START_ADCODE: str = os.getenv('START_ADCODE', '100000')  # 起始区域编码（默认全国）
    MAX_LEVEL: int = int(os.getenv('MAX_LEVEL', '3'))         # 最大下钻层级
    DELAY_SECONDS: float = float(os.getenv('DELAY_SECONDS', '0.2'))  # 请求间隔时间
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        获取数据库连接字符串
        
        如果设置了 DATABASE_URL 环境变量，则直接返回；
        否则使用各单独配置项构建连接字符串，并对密码进行 URL 编码
        
        Returns:
            格式化后的数据库连接字符串
        """
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        # 对密码进行 URL 编码以处理特殊字符
        encoded_password = quote_plus(cls.DB_PASSWORD)
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证配置是否有效
        
        Returns:
            配置是否有效
        """
        if not cls.DATABASE_URL and not cls.DB_PASSWORD:
            print("错误: 请设置 DATABASE_URL 或 DB_PASSWORD 环境变量")
            return False
        return True
    DELAY_SECONDS: float = float(os.getenv('DELAY_SECONDS', '0.2'))
    
    @classmethod
    def get_database_url(cls) -> str:
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        encoded_password = quote_plus(cls.DB_PASSWORD)
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.DATABASE_URL and not cls.DB_PASSWORD:
            print("错误: 请设置 DATABASE_URL 或 DB_PASSWORD 环境变量")
            return False
        return True