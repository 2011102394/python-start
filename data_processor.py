"""
数据处理模块

负责解析 GeoJSON 数据并将其转换为数据库模型对象，
提供数据验证、转换和存储功能
"""

import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from shapely.geometry import shape, mapping
from geoalchemy2.shape import from_shape
from models import DatabaseManager, AdministrativeArea


class DataProcessor:
    """
    数据处理器
    
    负责解析、验证和存储行政区划数据
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化数据处理器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
    
    def parse_geojson_feature(self, feature: Dict, parent_adcode: Optional[str] = None, 
                             parent_name: Optional[str] = None) -> AdministrativeArea:
        """
        解析 GeoJSON 特征数据并转换为数据库模型对象
        
        Args:
            feature: GeoJSON 特征对象
            parent_adcode: 父级行政区划编码
            parent_name: 父级区域名称
            
        Returns:
            AdministrativeArea 对象
            
        Raises:
            ValueError: 当特征数据缺少必要属性时
        """
        # 获取特征的属性和几何数据
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')
        
        # 提取关键属性
        adcode = properties.get('adcode')
        name = properties.get('name')
        level = properties.get('level')
        center = properties.get('center')
        children_num = properties.get('childrenNum', 0)
        
        # 验证必要属性是否存在
        if not adcode or not name:
            raise ValueError("Feature missing required properties: adcode or name")
        
        # 创建行政区域对象
        area = AdministrativeArea(
            adcode=adcode,
            name=name,
            level=level,
            parent_adcode=parent_adcode,
            parent_name=parent_name,
            center=json.dumps(center) if center else None,
            children_num=children_num,
            raw_data=json.dumps(feature, ensure_ascii=False)
        )
        
        # 如果存在几何数据，转换为 PostGIS 格式
        if geometry:
            shapely_geom = shape(geometry)
            area.geometry = from_shape(shapely_geom, srid=4326)
        
        return area
    
    def save_area(self, session: Session, area: AdministrativeArea):
        """
        保存行政区域数据到数据库（更新或插入）
        
        Args:
            session: 数据库会话
            area: 行政区域对象
        """
        # 查找是否已存在相同 adcode 的记录
        existing = session.query(AdministrativeArea).filter(
            AdministrativeArea.adcode == area.adcode
        ).first()
        
        if existing:
            # 如果存在则更新现有记录
            existing.name = area.name
            existing.level = area.level
            existing.parent_adcode = area.parent_adcode
            existing.parent_name = area.parent_name
            existing.center = area.center
            existing.geometry = area.geometry
            existing.children_num = area.children_num
            existing.raw_data = area.raw_data
        else:
            # 如果不存在则添加新记录
            session.add(area)
    
    def process_geojson_data(self, data: Dict, parent_adcode: Optional[str] = None,
                            parent_name: Optional[str] = None) -> List[AdministrativeArea]:
        """
        处理 GeoJSON 数据，将其转换为数据库模型对象列表
        
        Args:
            data: 包含 GeoJSON 特征的字典
            parent_adcode: 父级行政区划编码
            parent_name: 父级区域名称
            
        Returns:
            AdministrativeArea 对象列表
        """
        areas = []
        
        # 如果数据包含特征列表，则逐一解析
        if 'features' in data:
            for feature in data['features']:
                try:
                    area = self.parse_geojson_feature(feature, parent_adcode, parent_name)
                    areas.append(area)
                except Exception as e:
                    print(f"解析特征失败: {e}")
                    continue
        
        return areas
    
    def save_to_database(self, areas: List[AdministrativeArea]):
        """
        批量保存行政区域数据到数据库
        
        Args:
            areas: 行政区域对象列表
        """
        session = self.db_manager.get_session()
        try:
            for area in areas:
                self.save_area(session, area)
            session.commit()
            print(f"成功保存 {len(areas)} 条行政区划数据")
        except Exception as e:
            session.rollback()
            print(f"保存数据失败: {e}")
            raise
        finally:
            session.close()
    
    def process_and_save(self, data: Dict, parent_adcode: Optional[str] = None,
                        parent_name: Optional[str] = None):
        """
        处理并保存数据的便捷方法
        
        Args:
            data: GeoJSON 数据
            parent_adcode: 父级行政区划编码
            parent_name: 父级区域名称
            
        Returns:
            处理后的行政区域对象列表
        """
        areas = self.process_geojson_data(data, parent_adcode, parent_name)
        if areas:
            self.save_to_database(areas)
        return areas
    
    def get_area_by_adcode(self, adcode: str) -> Optional[AdministrativeArea]:
        """
        根据行政区划编码获取区域信息
        
        Args:
            adcode: 行政区划编码
            
        Returns:
            AdministrativeArea 对象，如果不存在则返回 None
        """
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.adcode == adcode
            ).first()
        finally:
            session.close()
    
    def get_areas_by_level(self, level: str) -> List[AdministrativeArea]:
        """
        根据行政级别获取区域列表
        
        Args:
            level: 行政级别（country, province, city, district）
            
        Returns:
            AdministrativeArea 对象列表
        """
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.level == level
            ).all()
        finally:
            session.close()
    
    def get_children_areas(self, parent_adcode: str) -> List[AdministrativeArea]:
        """
        获取指定父级区域的所有子区域
        
        Args:
            parent_adcode: 父级行政区划编码
            
        Returns:
            子区域对象列表
        """
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.parent_adcode == parent_adcode
            ).all()
        finally:
            session.close()