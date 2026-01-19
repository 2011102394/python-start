uv# 行政区划数据获取和存储工具

从阿里云 DataV GeoAtlas 获取行政区划数据，并存储到 PostGIS 数据库中。

## 功能特性

- 从 DataV GeoAtlas API 获取行政区划数据
- 支持逐级下钻获取（国家 -> 省/直辖市 -> 市 -> 区县）
- 将数据存储到 PostGIS 数据库
- 支持地理空间数据的存储和查询
- 自动处理 GeoJSON 格式数据

## 安装依赖

使用 uv 包管理工具：

```bash
uv sync
```

或使用 pip 安装：

```bash
pip install -e .
```

手动安装依赖：

```bash
uv pip install requests psycopg2-binary geoalchemy2 sqlalchemy shapely
```

## 数据库准备

### 1. 安装 PostgreSQL 和 PostGIS

确保已安装 PostgreSQL 和 PostGIS 扩展。

### 2. 创建数据库

```sql
CREATE DATABASE geo_data;
```

### 3. 启用 PostGIS 扩展

```sql
\c geo_data
CREATE EXTENSION postgis;
```

## 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
DATABASE_URL=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geo_data
DB_USER=postgres
DB_PASSWORD=your_password
START_ADCODE=100000
MAX_LEVEL=3
DELAY_SECONDS=0.2
```

### 配置说明

**方式一：使用 DATABASE_URL（完整连接字符串）**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

**方式二：使用单独配置项（推荐，支持特殊字符密码）**
- `DB_HOST`: 数据库主机地址（默认：localhost）
- `DB_PORT`: 数据库端口（默认：5432）
- `DB_NAME`: 数据库名称（默认：geo_data）
- `DB_USER`: 数据库用户名（默认：postgres）
- `DB_PASSWORD`: 数据库密码（支持包含特殊字符，如 !@#$%）

**其他配置：**
- `START_ADCODE`: 起始区域编码（100000 表示全国）
- `MAX_LEVEL`: 最大下钻层级（0=国家, 1=省, 2=市, 3=区县）
- `DELAY_SECONDS`: 请求间隔时间（秒），避免请求过于频繁

## 使用方法

### 运行主程序

使用 uv 运行：

```bash
uv run python main.py
```

或直接运行：

```bash
python main.py
```

这将：
1. 从指定的起始区域开始获取数据
2. 逐级下钻获取子区域数据
3. 将所有数据保存到 PostGIS 数据库

### 运行示例

使用 uv 运行：

```bash
uv run python examples.py
```

或直接运行：

```bash
python examples.py
```

示例包含：
- 获取单个区域数据
- 获取特定省份数据
- 逐级下钻获取数据
- 保存数据到数据库

## 项目结构

```
python-start/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── data_fetcher.py      # 数据获取模块
├── models.py            # 数据库模型
├── data_processor.py    # 数据处理模块
├── examples.py          # 使用示例
├── pyproject.toml       # 项目配置
├── .env.example         # 环境变量示例
└── README.md            # 项目说明
```

## 数据库表结构

### administrative_areas 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| adcode | String(20) | 行政区划编码（唯一） |
| name | String(100) | 区域名称 |
| level | String(20) | 行政级别（country/province/city/district） |
| parent_adcode | String(20) | 上级区域编码 |
| parent_name | String(100) | 上级区域名称 |
| center | String(100) | 中心点坐标（JSON格式） |
| geometry | Geometry | 地理空间数据（MULTIPOLYGON） |
| children_num | Integer | 子区域数量 |
| raw_data | Text | 原始JSON数据 |

## API 接口说明

DataV GeoAtlas 提供两种 API 格式：

1. 基础数据：`https://geo.datav.aliyun.com/areas_v3/bound/{adcode}.json`
2. 完整数据：`https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json`

完整数据包含子区域信息，支持逐级下钻。

## 常用区域编码

- 100000: 中华人民共和国
- 110000: 北京市
- 310000: 上海市
- 440000: 广东省
- 440300: 深圳市

## 注意事项

1. 请合理设置请求间隔时间，避免对服务器造成过大压力
2. 数据来源于高德开放平台，仅供学习交流使用
3. 数据更新时间为 2021年5月
4. 确保数据库连接配置正确
5. 首次运行会创建数据库表，重复运行会更新已有数据

## 查询示例

### 查询所有省份

```sql
SELECT adcode, name FROM administrative_areas WHERE level = 'province';
```

### 查询某个省份的所有城市

```sql
SELECT adcode, name FROM administrative_areas 
WHERE parent_adcode = '440000';
```

### 查询某个区域的边界

```sql
SELECT name, ST_AsGeoJSON(geometry) as geojson 
FROM administrative_areas 
WHERE adcode = '440300';
```

### 查询包含某个点的区域

```sql
SELECT name, adcode FROM administrative_areas 
WHERE ST_Contains(geometry, ST_SetSRID(ST_MakePoint(114.0579, 22.5431), 4326));
```

## 许可证

本项目仅供学习交流使用。