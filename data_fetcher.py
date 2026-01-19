"""
DataV 行政区划数据获取模块

提供从阿里云 DataV GeoAtlas 获取行政区划数据的功能，
支持逐级下钻获取不同层级的行政区域数据。
"""

import requests
from typing import Dict, List, Optional
import time


class DataVFetcher:
    """DataV 行政区划数据获取器"""
    
    # DataV GeoAtlas API 基础 URL
    BASE_URL = "https://geo.datav.aliyun.com/areas_v3/bound"
    
    def __init__(self):
        """
        初始化数据获取器
        
        设置请求会话和默认请求头
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_area_data(self, adcode: str, full: bool = False) -> Optional[Dict]:
        """
        获取指定行政区划的数据
        
        Args:
            adcode: 行政区划编码
            full: 是否获取完整数据（包含子区域信息）
            
        Returns:
            区域数据字典，如果获取失败则返回 None
        """
        # 构造请求 URL，full 参数决定是否获取包含子区域的完整数据
        url = f"{self.BASE_URL}/{adcode}.json"
        if full:
            url = f"{self.BASE_URL}/{adcode}_full.json"
        
        try:
            # 发送 GET 请求获取数据
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取数据失败 (adcode={adcode}): {e}")
            return None
    
    def fetch_national_data(self) -> Optional[Dict]:
        """
        获取全国数据
        
        Returns:
            全国行政区划数据
        """
        return self.fetch_area_data("100000", full=True)
    
    def fetch_province_data(self, adcode: str) -> Optional[Dict]:
        """
        获取省级数据
        
        Args:
            adcode: 省级行政区划编码
            
        Returns:
            省级行政区划数据
        """
        return self.fetch_area_data(adcode, full=True)
    
    def fetch_city_data(self, adcode: str) -> Optional[Dict]:
        """
        获取市级数据
        
        Args:
            adcode: 市级行政区划编码
            
        Returns:
            市级行政区划数据
        """
        return self.fetch_area_data(adcode, full=True)
    
    def fetch_district_data(self, adcode: str) -> Optional[Dict]:
        """
        获取区县级数据
        
        Args:
            adcode: 区县级行政区划编码
            
        Returns:
            区县级行政区划数据
        """
        return self.fetch_area_data(adcode, full=False)
    
    def drill_down(self, adcode: str = "100000", max_level: int = 3) -> List[Dict]:
        """
        逐级下钻获取数据
        
        从指定区域开始，递归获取其子区域数据
        
        Args:
            adcode: 起始区域编码，默认为全国（100000）
            max_level: 最大递归层级
            
        Returns:
            包含所有获取到的区域数据的列表
        """
        results = []
        
        def _fetch_recursive(current_adcode: str, level: int):
            """
            递归获取子区域数据的内部函数
            
            Args:
                current_adcode: 当前区域编码
                level: 当前递归层级
            """
            # 如果超过最大层级则停止递归
            if level > max_level:
                return
            
            # 获取当前区域数据
            data = self.fetch_area_data(current_adcode, full=True)
            if not data:
                return
            
            # 将当前区域数据添加到结果列表
            results.append(data)
            
            # 如果还有子层级且当前数据包含子区域，则继续递归
            if 'features' in data and level < max_level:
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    child_adcode = properties.get('adcode')
                    if child_adcode:
                        # 递归获取子区域数据
                        _fetch_recursive(child_adcode, level + 1)
                        # 添加延迟以避免请求过于频繁
                        time.sleep(0.1)
        
        # 开始递归获取
        _fetch_recursive(adcode, 0)
        return results
    
    def get_all_areas(self) -> List[Dict]:
        """
        获取所有行政区划数据（从全国开始下钻）
        
        Returns:
            所有行政区划数据列表
        """
        return self.drill_down("100000", max_level=3)
    
    def close(self):
        """关闭请求会话，释放资源"""
        self.session.close()