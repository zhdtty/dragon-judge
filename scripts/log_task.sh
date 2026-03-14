#!/bin/bash
#
# log_task.sh - 任务后自动记录脚本
# 用法: ./log_task.sh "任务描述" "结果类型" "耗时分钟"
#
# 示例:
#   ./log_task.sh "完成Dragon Judge核心算法" "success" "120"
#   ./log_task.sh "修复数据抓取Bug" "partial" "45"
#

set -e

# 配置
WORKSPACE_ROOT="${HOME}/.openclaw/workspace-001"
MEMORY_DIR="${WORKSPACE_ROOT}/memory"
EVOLUTION_DIR="${MEMORY_DIR}/evolution"
TASKS_DIR="${EVOLUTION_DIR}/tasks"

# 确保目录存在
mkdir -p "${TASKS_DIR}"

# 获取参数
TASK_DESC="${1:-未命名任务}"
OUTCOME="${2:-success}"  # success, partial, failure, cancelled
DURATION="${3:-0}"
AGENT="${AGENT_NAME:-代码检查}"

# 生成任务ID
TASK_ID=$(echo "${TASK_DESC}-$(date +%s)" | md5sum | cut -c1-8)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TODAY=$(date '+%Y-%m-%d')

# 结果类型映射
case "${OUTCOME}" in
    success|✅)
        OUTCOME_EMOJI="✅"
        OUTCOME_TEXT="成功"
        ;;
    partial|🟡)
        OUTCOME_EMOJI="🟡"
        OUTCOME_TEXT="部分成功"
        ;;
    failure|❌)
        OUTCOME_EMOJI="❌"
        OUTCOME_TEXT="失败"
        ;;
    cancelled|⚪)
        OUTCOME_EMOJI="⚪"
        OUTCOME_TEXT="取消"
        ;;
    *)
        OUTCOME_EMOJI="✅"
        OUTCOME_TEXT="成功"
        ;;
esac

# 创建任务记录文件
TASK_FILE="${TASKS_DIR}/task_${TASK_ID}_${TODAY}.json"

cat > "${TASK_FILE}" << EOF
{
  "task_id": "${TASK_ID}",
  "timestamp": "${TIMESTAMP}",
  "agent": "${AGENT}",
  "description": "${TASK_DESC}",
  "outcome": "${OUTCOME}",
  "outcome_text": "${OUTCOME_TEXT}",
  "duration_minutes": ${DURATION},
  "tools_used": [],
  "skills_applied": [],
  "problems": [],
  "solutions": [],
  "lessons": [],
  "code_snippets": []
}
EOF

# 同时追加到今日记忆
DAILY_MEMORY="${MEMORY_DIR}/${TODAY}.md"

if [ ! -f "${DAILY_MEMORY}" ]; then
    echo "# ${TODAY} 工作记录" > "${DAILY_MEMORY}"
    echo "" >> "${DAILY_MEMORY}"
fi

cat >> "${DAILY_MEMORY}" << EOF

## ${TIMESTAMP} - ${AGENT}

**任务**: ${TASK_DESC}
**结果**: ${OUTCOME_EMOJI} ${OUTCOME_TEXT}
**耗时**: ${DURATION} 分钟
**任务ID**: ${TASK_ID}

### 执行过程
<!-- 在这里记录详细执行步骤 -->

### 遇到的问题
- 

### 解决方案
- 

### 经验教训
- 

---
EOF

echo "✅ 任务已记录"
echo "📄 任务文件: ${TASK_FILE}"
echo "📝 记忆文件: ${DAILY_MEMORY}"
echo ""
echo "提示: 请编辑记忆文件补充详细信息"
