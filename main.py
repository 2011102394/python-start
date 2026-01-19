import time
from data_fetcher import DataVFetcher
from models import DatabaseManager
from data_processor import DataProcessor
from config import Config


def main():
    if not Config.validate():
        return
    
    print("开始获取行政区划数据...")
    print(f"数据库连接: {Config.DATABASE_URL}")
    print(f"起始区域: {Config.START_ADCODE}")
    print(f"最大层级: {Config.MAX_LEVEL}")
    
    db_manager = DatabaseManager(Config.DATABASE_URL)
    fetcher = DataVFetcher()
    processor = DataProcessor(db_manager)
    
    try:
        print("\n创建数据库表...")
        db_manager.create_tables()
        
        print(f"\n开始从 {Config.START_ADCODE} 获取数据...")
        all_data = fetcher.drill_down(
            Config.START_ADCODE, 
            max_level=Config.MAX_LEVEL
        )
        
        print(f"\n共获取到 {len(all_data)} 个区域的数据")
        
        total_saved = 0
        for idx, data in enumerate(all_data, 1):
            print(f"\n处理第 {idx}/{len(all_data)} 个区域...")
            
            try:
                areas = processor.process_geojson_data(data)
                processor.save_to_database(areas)
                total_saved += len(areas)
                
                if idx < len(all_data):
                    time.sleep(Config.DELAY_SECONDS)
                    
            except Exception as e:
                print(f"处理数据时出错: {e}")
                continue
        
        print(f"\n完成! 共保存 {total_saved} 条行政区划数据到数据库")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")
        raise
    finally:
        fetcher.close()
        db_manager.close()


if __name__ == "__main__":
    main()
