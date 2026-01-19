import os
from typing import Optional
from urllib.parse import quote_plus


class Config:
    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_NAME: str = os.getenv('DB_NAME', 'geo_data')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'arsc123!@#')
    
    START_ADCODE: str = os.getenv('START_ADCODE', '100000')
    MAX_LEVEL: int = int(os.getenv('MAX_LEVEL', '3'))
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