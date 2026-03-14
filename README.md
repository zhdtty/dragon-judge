# Dragon Judge 🐉

A股情绪龙头助手 - AI驱动的市场情绪分析与龙头选股系统

## 🎯 项目简介

Dragon Judge 是一个基于情绪周期理论的A股量化分析系统，专注于：
- 市场情绪评分（0-100分）
- 龙头候选识别
- 涨停梯队分析
- 主线板块追踪

## ✅ 当前状态（MVP v1.0）

**简化版MVP已可用！** 本地运行，无需Docker。

### 已实现功能
- ✅ Dragon Judge核心算法（情绪评分、周期判断）
- ✅ 5维龙头评分系统
- ✅ 报告生成（JSON + Markdown）
- ✅ 记忆自动进化系统

### 延后功能
- ⏳ Telegram Bot（Sprint 2）
- ⏳ Docker部署（Sprint 3）
- ⏳ Web前端（Sprint 3）

---

## 🚀 快速开始（本地运行）

### 1. 克隆仓库
```bash
git clone https://github.com/zhdtty/dragon-judge.git
cd dragon-judge
```

### 2. 运行（无需安装依赖）
```bash
python3 main.py
```

### 3. 查看报告
```bash
cat output/report_2026-03-14.md
```

---

## 📊 运行示例

```bash
$ python3 main.py

🚀 Dragon Judge MVP v1.0
==================================================
📊 正在获取市场数据...
✅ 数据获取完成
   涨停家数: 45
   跌停家数: 8
   龙头股: 3 只

🐉 正在运行Dragon Judge分析...
✅ 分析完成
   情绪分数: 51.5/100
   市场周期: 高潮
   龙头股: 3 只

📝 正在生成报告...
✅ 报告已保存
   JSON: output/report_2026-03-14.json
   Markdown: output/report_2026-03-14.md

==================================================
📊 Dragon Judge 情绪分析报告
==================================================

📅 日期: 2026-03-14
🌡️  情绪分数: 51.48/100
📈 市场周期: 高潮

🐉 龙头股:
   1. 平安银行 (000001) - 3板 - 评分54.0
   2. 万科A (000002) - 2板 - 评分46.0
   3. 贵州茅台 (600519) - 1板 - 评分38.0

🎯 策略建议:
   高潮减仓，只留核心龙头
```

---

## 🏗️ 项目结构

```
dragon-judge/
├── main.py                 # 简化版MVP主程序 ⭐
├── src/                    # 核心代码
│   └── scoring/
│       └── dragon_judge.py # Dragon Judge算法
├── scripts/                # 工具脚本
│   ├── log_task.sh         # 任务记录
│   ├── daily_evolution.sh  # 每日进化
│   ├── weekly_sublimation.sh # 每周升华
│   ├── auto_evolution.py   # 自动进化系统
│   └── evolution.py        # 进化助手v2.0
├── tests/                  # 测试用例
├── docs/                   # 文档
│   ├── algorithm-v1.md     # 算法文档
│   └── memory-auto-evolution.md # 进化系统文档
├── config/                 # 配置文件
└── output/                 # 输出报告
```

---

## 🎯 使用场景

### 场景1：每日开盘前分析
```bash
python3 main.py
# 查看 output/report_YYYY-MM-DD.md 获取情绪评分和策略建议
```

### 场景2：记录任务（记忆进化）
```bash
./scripts/log_task.sh "完成的任务描述" "success" "60"
```

### 场景3：每日进化整理
```bash
./scripts/daily_evolution.sh
```

---

## 👥 团队分工

| 角色 | 负责人 | 职责 | 状态 |
|------|--------|------|------|
| 产品/策略 | @交易策略 | Dragon Judge算法、情绪评分 | ✅ 算法文档已提交 |
| 数据采集 | @数据采集 | Tushare数据接口、数据Pipeline | 🔄 进行中 |
| 架构/开发 | @代码检查 | 系统架构、main.py整合 | ✅ MVP已可用 |
| 基础设施 | @工程助理 | 部署文档 | 🔄 进行中 |

---

## 📅 开发计划

### Sprint 1 (3/14) - MVP ✅
- [x] Dragon Judge核心算法
- [x] 简化版main.py
- [x] 报告生成
- [x] 记忆进化系统

### Sprint 2 (3/15-3/16) - 数据对接
- [ ] 集成真实数据抓取（akshare/Tushare）
- [ ] 定时任务（9:25自动运行）
- [ ] Telegram Bot推送

### Sprint 3 (3/17-3/20) - 优化部署
- [ ] Docker部署
- [ ] Web前端
- [ ] 性能优化

---

## 📝 更新日志

### v1.0 MVP (2026-03-14)
- ✅ Dragon Judge核心算法
- ✅ 情绪评分系统（0-100分）
- ✅ 市场周期判断（冰点→启动→发酵→高潮→退潮）
- ✅ 5维龙头评分
- ✅ 自动报告生成
- ✅ 记忆自动进化系统（3个脚本）

---

## 📄 许可证

MIT License - 由海东团队打造 🦞
