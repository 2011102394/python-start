"""
主程序入口

执行行政区划数据获取和存储的主要逻辑流程
"""

import time
from data_fetcher import DataVFetcher
from models import DatabaseManager
from data_processor import DataProcessor
from config import Config


def main():
    """
    主程序入口函数
    
    执行完整的数据获取和存储流程：
    1. 验证配置
    2. 创建数据库表
    3. 获取行政区划数据
    4. 逐级下钻处理数据
    5. 保存到数据库
    """
    
    # 验证配置是否有效
    if not Config.validate():
        return
    
    # 获取数据库连接URL
    database_url = Config.get_database_url()
    
    print("开始获取行政区划数据...")
    print(f"数据库连接: {database_url}")
    print(f"起始区域: {Config.START_ADCODE}")
    print(f"最大层级: {Config.MAX_LEVEL}")
    
    # 初始化各个组件
    db_manager = DatabaseManager(database_url)
    fetcher = DataVFetcher()
    processor = DataProcessor(db_manager)
    
    try:
        # 创建数据库表
        print("\n创建数据库表...")
        db_manager.create_tables()
        
        # 开始获取数据
        print(f"\n开始从 {Config.START_ADCODE} 获取数据...")
        all_data = fetcher.drill_down(
            Config.START_ADCODE, 
            max_level=Config.MAX_LEVEL
        )
        
        print(f"\n共获取到 {len(all_data)} 个区域的数据")
        
        # 逐个处理获取到的数据
        total_saved = 0
        for idx, data in enumerate(all_data, 1):
            print(f"\n处理第 {idx}/{len(all_data)} 个区域...")
            
            try:
                # 解析并保存数据
                areas = processor.process_geojson_data(data)
                processor.save_to_database(areas)
                total_saved += len(areas)
                
                # 在处理多个数据之间添加延迟，避免请求过于频繁
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
        # 关闭资源
        fetcher.close()
        db_manager.close()


if __name__ == "__main__":
    main()
