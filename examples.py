from data_fetcher import DataVFetcher
from models import DatabaseManager
from data_processor import DataProcessor


def example_fetch_single_area():
    print("示例1: 获取单个区域数据")
    fetcher = DataVFetcher()
    
    data = fetcher.fetch_national_data()
    if data:
        print(f"获取到全国数据，包含 {len(data.get('features', []))} 个特征")
        print(f"第一个区域: {data['features'][0]['properties']}")
    
    fetcher.close()


def example_fetch_province():
    print("\n示例2: 获取特定省份数据")
    fetcher = DataVFetcher()
    
    data = fetcher.fetch_province_data("110000")
    if data:
        print(f"获取到北京市数据")
        for feature in data.get('features', []):
            props = feature['properties']
            print(f"  - {props['name']} (adcode: {props['adcode']})")
    
    fetcher.close()


def example_drill_down():
    print("\n示例3: 逐级下钻获取数据")
    fetcher = DataVFetcher()
    
    results = fetcher.drill_down("100000", max_level=2)
    print(f"共获取到 {len(results)} 个区域的数据")
    
    fetcher.close()


def example_save_to_database():
    print("\n示例4: 保存数据到数据库")
    
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/geo_data"
    
    db_manager = DatabaseManager(DATABASE_URL)
    fetcher = DataVFetcher()
    processor = DataProcessor(db_manager)
    
    try:
        db_manager.create_tables()
        
        data = fetcher.fetch_province_data("110000")
        if data:
            areas = processor.process_geojson_data(data)
            processor.save_to_database(areas)
            
            saved_areas = processor.get_areas_by_level("district")
            print(f"数据库中现在有 {len(saved_areas)} 个区县级区域")
    
    finally:
        fetcher.close()
        db_manager.close()


if __name__ == "__main__":
    example_fetch_single_area()
    example_fetch_province()
    example_drill_down()
    # example_save_to_database()  # 需要数据库连接