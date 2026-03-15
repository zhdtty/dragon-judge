# Dragon Judge 代码优化说明

## 优化概述

本次优化将 Dragon Judge 从 v1.0 MVP 版本升级到 v2.0 生产级版本，主要改进了以下方面：

---

## 1. dragon_judge.py 核心算法优化

### 1.1 完整类型注解

**改动点：**
- 所有函数参数和返回值添加类型注解
- 使用 `Union`, `Optional`, `List`, `Dict`, `Any` 等类型
- 复杂类型使用自定义类型别名

```python
# 示例
def validate_market_data(
    self, 
    market_data: Union[Dict[str, Any], MarketData]
) -> MarketData:
    ...
```

### 1.2 完善错误处理

**新增自定义异常类：**
- `DragonJudgeError` - 基础异常类
- `InvalidDataError` - 数据无效异常
- `ValidationError` - 数据验证异常
- `InvalidCycleError` - 无效周期异常
- `ConfigurationError` - 配置错误异常

**特点：**
- 所有异常继承自基类，便于统一捕获
- 异常包含错误代码 (code) 和错误信息 (message)

### 1.3 优化五维评分算法

**改进点：**

1. **高度分优化**
   - 使用非线性增长公式：`min((天数/满分天数)^1.5 * 100, 100)`
   - 连板越多，分数增长越快，但5板封顶

2. **竞争分优化**
   - 考虑同身位股票数量
   - 每个竞争对手扣除固定分数（可配置）
   - 分数下限为0

3. **板块分优化**
   - 添加板块数据支持
   - 考虑跟风股数量和板块涨停数
   - 支持板块效应加权

4. **情绪分优化**
   - 与市场整体情绪挂钩
   - 情绪>70时加分

5. **质量分优化**
   - 添加换手率评估
   - 添加量比评估
   - 连板质量加分

### 1.4 数据验证逻辑

**新增 `MarketData` 数据类：**
- 自动验证数据类型和范围
- 提供默认值处理
- 支持 `to_dict()` 转换

**新增 `LeadingStock` 数据类扩展：**
- 添加扩展字段：sector, market_cap, turnover_rate, volume_ratio
- `__post_init__` 验证必填字段
- `from_dict()` 工厂方法

**验证规则：**
- 股票代码和名称不能为空
- 连板天数必须为非负整数
- 涨停/跌停数必须为非负整数
- 总股票数必须为正整数

---

## 2. main.py 主程序优化

### 2.1 配置加载功能

**新增 `AppConfig` 数据类：**
- 支持 YAML/JSON 配置文件
- 环境变量 `DRAGON_JUDGE_CONFIG` 支持
- 配置优先级：命令行 > 环境变量 > 配置文件 > 默认值

**配置项：**
```python
- output_dir: 输出目录
- data_source: 数据源 (mock/tushare/akshare)
- weights: 评分权重
- thresholds: 周期阈值
- report_format: 报告格式
- max_leaders: 显示龙头股数量
- log_level: 日志级别
- log_file: 日志文件路径
```

### 2.2 完善命令行参数处理

**使用 argparse 实现完整参数解析：**

```bash
# 运行模式
--fetch          # 仅抓取数据
--analyze        # 仅分析数据
--report         # 仅生成报告

# 配置选项
--config, -c     # 配置文件路径
--output, -o     # 输出目录
--source, -s     # 数据源

# 报告选项
--format, -f     # 报告格式
--max-leaders    # 显示龙头股数量

# 日志选项
--verbose, -v    # 详细日志
--log-level      # 日志级别
--log-file       # 日志文件
```

### 2.3 添加日志系统

**日志特性：**
- 支持控制台和文件双输出
- 可配置日志级别 (DEBUG/INFO/WARNING/ERROR)
- 文件日志包含时间戳、模块名、日志级别
- 控制台日志简洁，只显示核心信息

**使用方式：**
```bash
python main.py --verbose              # 调试模式
python main.py --log-level DEBUG      # 设置日志级别
python main.py --log-file app.log     # 输出到文件
```

### 2.4 优化报告生成

**新增 `ReportGenerator` 类：**
- 支持 Markdown/JSON 双格式输出
- 生成带有 emoji 的易读报告
- 输出文件自动命名（基于日期）
- 控制台彩色输出

**报告内容：**
- 情绪分数和市场周期
- 龙头股排行表格
- 策略建议
- 风险等级

---

## 3. requirements.txt 依赖管理

### 优化内容：

1. **结构化分类**
   - 核心依赖
   - 数据库
   - 定时任务
   - 推送服务
   - 开发依赖
   - 类型检查

2. **版本约束**
   - 使用 `>=` 指定最低版本
   - 确保兼容性

3. **新增依赖**
   - `pytest-asyncio` - 异步测试支持
   - `mypy` - 静态类型检查
   - `types-*` - 类型存根

---

## 4. 项目结构优化

### 优化后的结构：

```
dragon-judge/
├── main.py                  # 主程序入口
├── requirements.txt         # 依赖管理
├── README.md               # 项目说明
├── config/
│   └── config.example.yaml # 配置示例
├── src/
│   ├── __init__.py
│   └── scoring/
│       ├── __init__.py     # 模块导出
│       └── dragon_judge.py # 核心算法
├── tests/
│   ├── conftest.py         # 测试固件
│   └── test_dragon_judge.py # 单元测试
├── scripts/
│   ├── evolution.py
│   └── auto_evolution.py
├── output/                 # 输出目录
└── docs/                   # 文档目录
```

### 模块导出优化：

**src/scoring/__init__.py：**
```python
__all__ = [
    "DragonJudge",
    "MarketCycle",
    "LeadingStock",
    "MarketData",
    "DragonJudgeError",
    ...
]
```

---

## 5. 测试优化

### 测试覆盖：

1. **MarketCycle 测试**
   - 周期名称验证
   - 从值获取周期
   - 无效值处理
   - 显示名称

2. **LeadingStock 测试**
   - 有效/无效创建
   - 字典转换
   - 数据验证

3. **MarketData 测试**
   - 数据验证
   - 默认值处理

4. **DragonJudge 初始化测试**
   - 默认配置
   - 自定义权重
   - 无效配置处理

5. **情绪分数测试**
   - 分数计算
   - 范围验证
   - 连板加分

6. **周期判断测试**
   - 各周期检测
   - 边界条件

7. **龙头选股测试**
   - 选股逻辑
   - 排序验证
   - 空数据处理

8. **报告生成测试**
   - 报告结构
   - 内容验证

9. **错误处理测试**
   - 异常抛出
   - 错误信息

10. **五维评分测试**
    - 各维度计算
    - 综合评分

11. **策略生成测试**
    - 各周期策略
    - 极端情况处理

12. **风险等级测试**
    - 风险计算
    - 警告信息

---

## 6. 新增功能

### 6.1 风险等级评估
```python
risk_level = {
    'level': '高风险',
    'score': 4,
    'color': '🔴',
    'warning': '情绪极度亢奋，随时可能回调'
}
```

### 6.2 周期转换概率
```python
probabilities = dj.get_cycle_transition_probability(
    current_cycle=MarketCycle.CLIMAX,
    sentiment_trend="down"
)
# {'DIVERGENCE': 0.8, 'CLIMAX': 0.2}
```

### 6.3 市场情绪趋势分析
- 基于历史数据的情绪趋势判断
- 支持 up/down/flat 三种趋势

---

## 7. 代码质量提升

### 7.1 文档字符串
- 所有公共方法都有详细的文档字符串
- 包含参数说明、返回值、异常说明
- 算法逻辑有详细注释

### 7.2 命名规范
- 使用有意义的变量名
- 遵循 PEP 8 命名规范
- 类型名使用 PascalCase

### 7.3 模块化设计
- 单一职责原则
- 低耦合高内聚
- 便于单元测试

---

## 修改文件清单

| 文件路径 | 操作 | 说明 |
|----------|------|------|
| src/scoring/dragon_judge.py | 修改 | 核心算法优化 |
| src/scoring/__init__.py | 新增 | 模块导出 |
| src/__init__.py | 新增 | 包初始化 |
| main.py | 修改 | 主程序优化 |
| requirements.txt | 修改 | 依赖管理 |
| tests/test_dragon_judge.py | 修改 | 测试优化 |
| tests/conftest.py | 修改 | 测试固件 |

---

## 运行说明

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行主程序
```bash
# 完整流程
python main.py

# 仅抓取数据
python main.py --fetch

# 使用配置
python main.py --config config.yaml --verbose

# 自定义输出
python main.py --output ./reports --format both
```

### 运行测试
```bash
pytest tests/test_dragon_judge.py -v
```

---

## 版本信息

- **版本**: v2.0.0
- **Python**: 3.9+
- **更新日期**: 2026-03-15
