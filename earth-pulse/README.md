# EARTH PULSE

**Global Seismic Intelligence Dashboard · 全球地震活动监测与时空演化分析平台**

EARTH PULSE 是基于 USGS/Kaggle 1965–2016 年历史显著地震记录的 Streamlit 科学看板。所有指标和图形来自本地 CSV；它不是实时监测系统，也不提供预测。

## 功能

- **Global Overview**：可旋转、缩放和悬浮查看的 WebGL 3D 地球（可切换 2D 地图），震级与深度分布、年度频次和动态指标。
- **Spatiotemporal Explorer**：单年或累计模式的年份控制器，联动 3D 地球、指标和图表。
- **Regional Analysis**：五个近似经纬度区域的事件分析和双区域指标对比。
- **Event Explorer**：事件 ID、时间、震级和深度搜索；可选记录详情、±30 天及 300 km 的邻近记录和 CSV 导出。邻近不等于余震。
- **Global Control Center**：跨页面保留的筛选条件，点击 Apply Filters 后统一作用于所有页面。

## 项目结构

```text
earth-pulse/
├── app.py                  # 启动入口，跳转至总览
├── pages/                  # 四个交互页面
├── components/             # 筛选、侧栏、指标、图表、地图
├── utils/                  # 数据载入、清洗、统计、常量
├── assets/style.css        # 统一深色主题
├── assets/ne_110m_land.geojson # Natural Earth 低精度陆地轮廓
├── data/database.csv       # 本地历史记录
├── requirements.txt
└── README.md
```

## 数据

数据源：[Kaggle Earthquake Database](https://www.kaggle.com/datasets/usgs/earthquake-database)。下载并解压，将 `database.csv` 放在 `earth-pulse/data/database.csv`。当前工作区已包含这个文件。缺少文件时，页面会显示下载说明，不会生成模拟数据。

程序要求至少有 `Date`、`Time`、`Latitude`、`Longitude`、`Magnitude`、`Depth`、`ID` 列。加载时合并日期和时间，校验坐标、震级和深度，仅保留 `Type=Earthquake`，按 `ID` 去重，并添加分析列。原始列仍保留。源文件修改后，Streamlit 缓存会自动失效。

## 安装与运行

需要 Python 3.11+，macOS 可直接使用。进入应用目录后运行：

```bash
cd earth-pulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

当前工作区已有外层 uv 虚拟环境及配置，也可以在仓库根目录运行：

```bash
uv sync
cd earth-pulse
../.venv/bin/streamlit run app.py
```

## 技术栈

Python、Streamlit、Pandas、NumPy、Plotly WebGL、Pillow、Pydeck（预留地图扩展）。3D 地球的陆地轮廓来自 [Natural Earth 1:110m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson)，该项目将数据作为 public domain 发布。地理文件已随项目存储，浏览器无需从地图服务下载底图。

3D 视图需要浏览器启用 WebGL；如果设备禁用了 WebGL，可切换页面上的 **2D Map**。地球拖动旋转、滚轮缩放、悬浮查看事件，不需要 Three.js、地图服务密钥或额外的前端构建工具。

## MVP 限制与下一步

- 区域是经纬度矩形近似，不代表构造分区边界；跨国际日期变更线的阿拉斯加区域已特殊处理。
- 年份控制器采用滑块，没有自动播放；3D 地球使用 Plotly WebGL，没有地震脉冲动画或点选联动。
- 数据是历史显著事件样本，不能用于推断所有地震的绝对频率趋势。

下一阶段优先增加连续时间播放、地图点选事件联动和脉冲动画。若需要更复杂的粒子特效，可通过 `components/maps.py` 的 `render_earthquake_globe()` 接口替换为 Three.js 组件。
