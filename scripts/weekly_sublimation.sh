#!/bin/bash
#
# weekly_sublimation.sh - 每周升华脚本
# 每周日23:00自动运行，深度分析并升华知识
#
# crontab设置:
#   0 23 * * 0 cd /path/to/workspace && ./scripts/weekly_sublimation.sh
#

set -e

# 配置
WORKSPACE_ROOT="${HOME}/.openclaw/workspace-001"
MEMORY_DIR="${WORKSPACE_ROOT}/memory"
EVOLUTION_DIR="${MEMORY_DIR}/evolution"
TASKS_DIR="${EVOLUTION_DIR}/tasks"
SNIPPETS_DIR="${EVOLUTION_DIR}/snippets"
WEEKLY_DIR="${EVOLUTION_DIR}/weekly"

# 确保目录存在
mkdir -p "${WEEKLY_DIR}" "${SNIPPETS_DIR}"

# 获取日期范围
TODAY=$(date '+%Y-%m-%d')
WEEK_START=$(date -d 'last sunday' '+%Y-%m-%d' 2>/dev/null || date -v-sun '+%Y-%m-%d')
WEEK_END=$(date '+%Y-%m-%d')
WEEK_NUM=$(date '+%V')

echo "🚀 启动每周升华流程 - 第${WEEK_NUM}周"
echo "================================"
echo "时间范围: ${WEEK_START} 至 ${WEEK_END}"

# Phase 1: 汇总本周数据
echo ""
echo "📊 Phase 1: 汇总本周数据"

WEEK_TASKS=$(find "${TASKS_DIR}" -name "task_*.json" -newermt "${WEEK_START} 00:00" ! -newermt "${WEEK_END} 23:59" 2>/dev/null | wc -l)
WEEK_SUCCESS=$(find "${TASKS_DIR}" -name "task_*.json" -newermt "${WEEK_START} 00:00" ! -newermt "${WEEK_END} 23:59" -exec grep -l '"outcome": "success"' {} \; 2>/dev/null | wc -l)

echo "  - 本周任务: ${WEEK_TASKS}"
echo "  - 成功: ${WEEK_SUCCESS}"
echo "  - 成功率: $(if [ ${WEEK_TASKS} -gt 0 ]; then echo $(( WEEK_SUCCESS * 100 / WEEK_TASKS )); else echo "0"; fi)%"

# Phase 2: 识别高频工具
echo ""
echo "🔧 Phase 2: 识别高频工具"

TOOL_STATS=$(find "${TASKS_DIR}" -name "task_*.json" -newermt "${WEEK_START} 00:00" ! -newermt "${WEEK_END} 23:59" -exec cat {} \; 2>/dev/null | grep -o '"tools_used": \[[^]]*\]' | tr ',' '\n' | grep -o '"[^"]*"' | sort | uniq -c | sort -rn | head -10)

echo "  本周使用最多的工具:"
echo "${TOOL_STATS}" | while read count tool; do
    if [ -n "${tool}" ]; then
        echo "    - ${tool}: ${count} 次"
    fi
done

# Phase 3: 提取可复用知识
echo ""
echo "💎 Phase 3: 提取可复用知识"

SNIPPET_COUNT=0

# 从本周任务中提取代码片段和解决方案
for task_file in $(find "${TASKS_DIR}" -name "task_*.json" -newermt "${WEEK_START} 00:00" ! -newermt "${WEEK_END} 23:59" 2>/dev/null); do
    # 提取解决方案作为知识片段
    SOLUTIONS=$(grep '"solutions"' "${task_file}" | grep -o '"[^"]*"' | grep -v 'solutions' | head -5)
    
    if [ -n "${SOLUTIONS}" ]; then
        TASK_ID=$(basename "${task_file}" .json | cut -d'_' -f2)
        SNIPPET_FILE="${SNIPPETS_DIR}/snippet_${TASK_ID}.md"
        
        cat > "${SNIPPET_FILE}" << EOF
# 知识片段 - ${TASK_ID}

**来源任务**: $(basename "${task_file}")
**提取时间**: ${TODAY}

## 解决方案
${SOLUTIONS}

## 使用场景
<!-- 补充适用场景 -->

## 注意事项
<!-- 补充使用注意事项 -->
EOF
        SNIPPET_COUNT=$((SNIPPET_COUNT + 1))
    fi
done

echo "  ✅ 提取了 ${SNIPPET_COUNT} 个知识片段"

# Phase 4: 生成升华报告
echo ""
echo "📈 Phase 4: 生成升华报告"

WEEKLY_FILE="${WEEKLY_DIR}/weekly_${WEEK_NUM}_${TODAY}.md"

cat > "${WEEKLY_FILE}" << EOF
# 🚀 每周升华报告 - 第${WEEK_NUM}周

**时间范围**: ${WEEK_START} 至 ${WEEK_END}  
**生成时间**: ${TODAY}

---

## 📊 本周数据概览

| 指标 | 数值 |
|------|------|
| 总任务数 | ${WEEK_TASKS} |
| 成功任务 | ${WEEK_SUCCESS} |
| 成功率 | $(if [ ${WEEK_TASKS} -gt 0 ]; then echo $(( WEEK_SUCCESS * 100 / WEEK_TASKS )); else echo "0"; fi)% |
| 新增知识片段 | ${SNIPPET_COUNT} |

---

## 🔧 工具使用分析

本周使用频率最高的工具:
$(echo "${TOOL_STATS}" | head -5)

---

## 💡 本周重要教训

<!-- 请手动补充本周学到的重要教训 -->

1. 
2. 
3. 

---

## 🎯 模式识别

### 高频任务类型
<!-- 自动统计或手动填写 -->

### 重复出现的问题
<!-- 记录本周多次遇到的问题 -->

### 成功的关键因素
<!-- 总结本周成功任务的共同点 -->

---

## 📚 知识升华

### 新提取的知识片段
- 共提取 ${SNIPPET_COUNT} 个可复用知识片段
- 存储位置: ${SNIPPETS_DIR}/

### 技能改进建议
<!-- 基于本周经验，提出技能改进建议 -->

1. 
2. 
3. 

---

## 🚀 下周计划

### 重点目标
- [ ] 
- [ ] 
- [ ] 

### 待优化事项
- [ ] 
- [ ] 

---

## 📝 长期记忆更新

### 需要更新到 MEMORY.md 的内容
<!-- 列出本周值得长期保存的关键信息 -->

### 需要更新到 SKILL.md 的内容
<!-- 列出本周改进的技能文档 -->

---

*每周升华报告 - 由自动进化系统生成*  
*下次升华: $(date -d 'next sunday' '+%Y-%m-%d' 2>/dev/null || date -v+sun '+%Y-%m-%d')*
EOF

echo "  ✅ 升华报告已生成: ${WEEKLY_FILE}"

# Phase 5: 归档旧数据
echo ""
echo "📦 Phase 5: 归档旧数据"

# 归档90天前的日报
ARCHIVED_COUNT=$(find "${EVOLUTION_DIR}/reports" -name "daily_*.md" -mtime +90 2>/dev/null | wc -l)
mkdir -p "${EVOLUTION_DIR}/archive"
find "${EVOLUTION_DIR}/reports" -name "daily_*.md" -mtime +90 -exec mv {} "${EVOLUTION_DIR}/archive/" \; 2>/dev/null || true

echo "  ✅ 归档了 ${ARCHIVED_COUNT} 个90天前的日报"

# 完成
echo ""
echo "================================"
echo "✅ 每周升华完成！"
echo "📄 报告: ${WEEKLY_FILE}"
echo "💎 知识片段: ${SNIPPETS_DIR}/"
echo ""
echo "🎯 下一步行动:"
echo "  1. 阅读升华报告，补充模式识别内容"
echo "  2. 更新 MEMORY.md 长期记忆"
echo "  3. 更新相关 SKILL.md 技能文档"
echo "  4. 规划下周重点目标"
