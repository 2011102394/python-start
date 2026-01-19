import os
from typing import Optional


class Config:
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:arsc123!@#@localhost:5432/geo_data'
    )
    
    START_ADCODE: str = os.getenv('START_ADCODE', '100000')
    MAX_LEVEL: int = int(os.getenv('MAX_LEVEL', '3'))
    DELAY_SECONDS: float = float(os.getenv('DELAY_SECONDS', '0.2'))
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.DATABASE_URL:
            print("错误: DATABASE_URL 环境变量未设置")
            return False
        return True