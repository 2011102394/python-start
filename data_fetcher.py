import requests
from typing import Dict, List, Optional
import time


class DataVFetcher:
    BASE_URL = "https://geo.datav.aliyun.com/areas_v3/bound"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_area_data(self, adcode: str, full: bool = False) -> Optional[Dict]:
        url = f"{self.BASE_URL}/{adcode}.json"
        if full:
            url = f"{self.BASE_URL}/{adcode}_full.json"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取数据失败 (adcode={adcode}): {e}")
            return None
    
    def fetch_national_data(self) -> Optional[Dict]:
        return self.fetch_area_data("100000", full=True)
    
    def fetch_province_data(self, adcode: str) -> Optional[Dict]:
        return self.fetch_area_data(adcode, full=True)
    
    def fetch_city_data(self, adcode: str) -> Optional[Dict]:
        return self.fetch_area_data(adcode, full=True)
    
    def fetch_district_data(self, adcode: str) -> Optional[Dict]:
        return self.fetch_area_data(adcode, full=False)
    
    def drill_down(self, adcode: str = "100000", max_level: int = 3) -> List[Dict]:
        results = []
        
        def _fetch_recursive(current_adcode: str, level: int):
            if level > max_level:
                return
            
            data = self.fetch_area_data(current_adcode, full=True)
            if not data:
                return
            
            results.append(data)
            
            if 'features' in data and level < max_level:
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    child_adcode = properties.get('adcode')
                    if child_adcode:
                        _fetch_recursive(child_adcode, level + 1)
                        time.sleep(0.1)
        
        _fetch_recursive(adcode, 0)
        return results
    
    def get_all_areas(self) -> List[Dict]:
        return self.drill_down("100000", max_level=3)
    
    def close(self):
        self.session.close()