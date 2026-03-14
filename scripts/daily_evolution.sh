#!/bin/bash
#
# daily_evolution.sh - 每日进化脚本
# 每天23:00自动运行，整理当日记忆
#
# crontab设置:
#   0 23 * * * cd /path/to/workspace && ./scripts/daily_evolution.sh
#

set -e

# 配置
WORKSPACE_ROOT="${HOME}/.openclaw/workspace-001"
MEMORY_DIR="${WORKSPACE_ROOT}/memory"
EVOLUTION_DIR="${MEMORY_DIR}/evolution"
TASKS_DIR="${EVOLUTION_DIR}/tasks"
SNIPPETS_DIR="${EVOLUTION_DIR}/snippets"
REPORTS_DIR="${EVOLUTION_DIR}/reports"

# 确保目录存在
mkdir -p "${SNIPPETS_DIR}" "${REPORTS_DIR}"

# 获取日期
TODAY=$(date '+%Y-%m-%d')
YESTERDAY=$(date -d 'yesterday' '+%Y-%m-%d' 2>/dev/null || date -v-1d '+%Y-%m-%d')
DAILY_MEMORY="${MEMORY_DIR}/${TODAY}.md"

echo "🚀 启动每日进化流程 - ${TODAY}"
echo "================================"

# 检查今日记忆是否存在
if [ ! -f "${DAILY_MEMORY}" ]; then
    echo "⚠️ 今日记忆文件不存在: ${DAILY_MEMORY}"
    echo "📝 创建空白记忆文件"
    echo "# ${TODAY} 工作记录" > "${DAILY_MEMORY}"
    echo "" >> "${DAILY_MEMORY}"
fi

# 统计今日任务
echo ""
echo "📊 Phase 1: 统计今日任务"

TASK_COUNT=$(find "${TASKS_DIR}" -name "task_*_${TODAY}.json" 2>/dev/null | wc -l)
SUCCESS_COUNT=$(find "${TASKS_DIR}" -name "task_*_${TODAY}.json" -exec grep -l '"outcome": "success"' {} \; 2>/dev/null | wc -l)
FAILURE_COUNT=$(find "${TASKS_DIR}" -name "task_*_${TODAY}.json" -exec grep -l '"outcome": "failure"' {} \; 2>/dev/null | wc -l)

echo "  - 总任务: ${TASK_COUNT}"
echo "  - 成功: ${SUCCESS_COUNT}"
echo "  - 失败: ${FAILURE_COUNT}"

# 生成日报
echo ""
echo "📋 Phase 2: 生成进化日报"

REPORT_FILE="${REPORTS_DIR}/daily_${TODAY}.md"

cat > "${REPORT_FILE}" << EOF
# 📊 进化日报 - ${TODAY}

## 今日概览
- **日期**: ${TODAY}
- **总任务**: ${TASK_COUNT}
- **成功**: ${SUCCESS_COUNT}
- **失败**: ${FAILURE_COUNT}
- **成功率**: $(if [ ${TASK_COUNT} -gt 0 ]; then echo $(( SUCCESS_COUNT * 100 / TASK_COUNT )); else echo "0"; fi)%

## 任务列表
EOF

# 添加任务详情
for task_file in "${TASKS_DIR}"/task_*_${TODAY}.json; do
    if [ -f "${task_file}" ]; then
        DESC=$(grep '"description"' "${task_file}" | cut -d'"' -f4)
        AGENT=$(grep '"agent"' "${task_file}" | cut -d'"' -f4)
        OUTCOME=$(grep '"outcome_text"' "${task_file}" | cut -d'"' -f4)
        echo "- [${AGENT}] ${DESC} - ${OUTCOME}" >> "${REPORT_FILE}"
    fi
done

# 添加教训总结
cat >> "${REPORT_FILE}" << EOF

## 经验教训
<!-- 自动提取或手动填写 -->

## 明日计划
- [ ] 
- [ ] 
- [ ] 

---
*自动生成于 ${TODAY} 23:00*
EOF

echo "  ✅ 日报已生成: ${REPORT_FILE}"

# 更新MEMORY.md
echo ""
echo "🧠 Phase 3: 更新长期记忆"

MEMORY_FILE="${WORKSPACE_ROOT}/MEMORY.md"

if [ ! -f "${MEMORY_FILE}" ]; then
    echo "# 长期记忆" > "${MEMORY_FILE}"
fi

# 提取今日重要教训（简化版）
cat >> "${MEMORY_FILE}" << EOF

## ${TODAY}

**今日完成**: ${TASK_COUNT} 个任务

### 关键事件
<!-- 请手动补充今日重要决策和事件 -->

### 学到的教训
<!-- 请手动补充重要教训 -->
EOF

echo "  ✅ 已更新 MEMORY.md"

# 清理旧任务文件（保留30天）
echo ""
echo "🧹 Phase 4: 清理旧文件"

DELETED_COUNT=$(find "${TASKS_DIR}" -name "task_*.json" -mtime +30 2>/dev/null | wc -l)
find "${TASKS_DIR}" -name "task_*.json" -mtime +30 -delete 2>/dev/null || true

echo "  ✅ 清理了 ${DELETED_COUNT} 个30天前的任务文件"

# 完成
echo ""
echo "================================"
echo "✅ 每日进化完成！"
echo "📄 日报: ${REPORT_FILE}"
echo "🧠 记忆: ${MEMORY_FILE}"
echo ""
echo "提示: 请检查并补充MEMORY.md中的关键事件和教训"
