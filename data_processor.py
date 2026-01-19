import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from shapely.geometry import shape, mapping
from geoalchemy2.shape import from_shape
from models import DatabaseManager, AdministrativeArea


class DataProcessor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def parse_geojson_feature(self, feature: Dict, parent_adcode: Optional[str] = None, 
                             parent_name: Optional[str] = None) -> AdministrativeArea:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')
        
        adcode = properties.get('adcode')
        name = properties.get('name')
        level = properties.get('level')
        center = properties.get('center')
        children_num = properties.get('childrenNum', 0)
        
        if not adcode or not name:
            raise ValueError("Feature missing required properties: adcode or name")
        
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
        
        if geometry:
            shapely_geom = shape(geometry)
            area.geometry = from_shape(shapely_geom, srid=4326)
        
        return area
    
    def save_area(self, session: Session, area: AdministrativeArea):
        existing = session.query(AdministrativeArea).filter(
            AdministrativeArea.adcode == area.adcode
        ).first()
        
        if existing:
            existing.name = area.name
            existing.level = area.level
            existing.parent_adcode = area.parent_adcode
            existing.parent_name = area.parent_name
            existing.center = area.center
            existing.geometry = area.geometry
            existing.children_num = area.children_num
            existing.raw_data = area.raw_data
        else:
            session.add(area)
    
    def process_geojson_data(self, data: Dict, parent_adcode: Optional[str] = None,
                            parent_name: Optional[str] = None) -> List[AdministrArea]:
        areas = []
        
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
        areas = self.process_geojson_data(data, parent_adcode, parent_name)
        if areas:
            self.save_to_database(areas)
        return areas
    
    def get_area_by_adcode(self, adcode: str) -> Optional[AdministrativeArea]:
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.adcode == adcode
            ).first()
        finally:
            session.close()
    
    def get_areas_by_level(self, level: str) -> List[AdministrativeArea]:
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.level == level
            ).all()
        finally:
            session.close()
    
    def get_children_areas(self, parent_adcode: str) -> List[AdministrativeArea]:
        session = self.db_manager.get_session()
        try:
            return session.query(AdministrativeArea).filter(
                AdministrativeArea.parent_adcode == parent_adcode
            ).all()
        finally:
            session.close()