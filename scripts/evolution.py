#!/usr/bin/env python3
"""
Dragon Judge 进化助手 (Evolution Assistant)

Phase 2: 自动化记忆进化系统
- 分析任务记录
- 自动生成复盘
- 提取知识片段
- 更新记忆文件

作者: 小码哥 🦞
版本: 2.0
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import argparse

# 配置
WORKSPACE_ROOT = Path.home() / ".openclaw/workspace-001"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
SKILLS_DIR = Path.home() / ".openclaw/workspace/skills"
DOCS_DIR = WORKSPACE_ROOT / "docs"

class TaskType(Enum):
    """任务类型"""
    CODE = "代码开发"
    ANALYSIS = "数据分析"
    WRITING = "文档编写"
    DEBUG = "Bug修复"
    RESEARCH = "调研研究"
    COMMUNICATION = "沟通协调"
    OTHER = "其他"

class TaskOutcome(Enum):
    """任务结果"""
    SUCCESS = "✅ 成功"
    PARTIAL = "🟡 部分成功"
    FAILURE = "❌ 失败"
    CANCELLED = "⚪ 取消"

@dataclass
class TaskRecord:
    """任务记录"""
    task_id: str
    timestamp: datetime
    agent: str
    task_type: TaskType
    description: str
    outcome: TaskOutcome
    duration_minutes: int
    tools_used: List[str] = field(default_factory=list)
    skills_applied: List[str] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    problems_encountered: List[str] = field(default_factory=list)
    solutions_found: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    reusable_snippets: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'task_type': self.task_type.value,
            'outcome': self.outcome.value
        }

@dataclass
class KnowledgeSnippet:
    """知识片段"""
    snippet_id: str
    category: str  # 'code', 'pattern', 'lesson', 'tool_usage'
    content: str
    source_task: str
    created_at: datetime
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'created_at': self.created_at.isoformat()
        }

class EvolutionAssistant:
    """进化助手核心类"""
    
    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE_ROOT
        self.memory_dir = self.workspace / "memory"
        self.evolution_dir = self.memory_dir / "evolution"
        self.snippets_dir = self.evolution_dir / "snippets"
        self.tasks_dir = self.evolution_dir / "tasks"
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        for dir_path in [self.evolution_dir, self.snippets_dir, self.tasks_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def analyze_today_tasks(self) -> List[TaskRecord]:
        """分析今日任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_memory = self.memory_dir / f"{today}.md"
        
        if not daily_memory.exists():
            print(f"⚠️ 今日记忆文件不存在: {daily_memory}")
            return []
        
        print(f"📖 读取今日记忆: {daily_memory.name}")
        
        with open(daily_memory, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析任务记录
        tasks = self._parse_tasks_from_memory(content)
        
        print(f"✅ 解析到 {len(tasks)} 个任务")
        return tasks
    
    def _parse_tasks_from_memory(self, content: str) -> List[TaskRecord]:
        """从记忆内容中解析任务"""
        tasks = []
        
        # 按任务块分割（通过标题或分隔符）
        # 支持多种格式：## 任务、### 任务、--- 分隔等
        task_blocks = re.split(r'\n##+ |\n---+|\n\*\*\*+', content)
        
        for block in task_blocks:
            if not block.strip():
                continue
            
            task = self._extract_task_info(block)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _extract_task_info(self, block: str) -> Optional[TaskRecord]:
        """从文本块提取任务信息"""
        # 生成任务ID
        task_id = hashlib.md5(block.encode()).hexdigest()[:8]
        
        # 检测任务类型
        task_type = self._detect_task_type(block)
        
        # 检测结果
        outcome = self._detect_outcome(block)
        
        # 提取描述（第一行或标题）
        lines = block.strip().split('\n')
        description = lines[0][:100] if lines else "未命名任务"
        
        # 提取工具使用
        tools = self._extract_tools(block)
        
        # 提取技能应用
        skills = self._extract_skills(block)
        
        # 提取问题
        problems = self._extract_patterns(block, r'(?:问题|错误|bug|失败|阻塞)[：:]?\s*(.+)', '问题')
        
        # 提取解决方案
        solutions = self._extract_patterns(block, r'(?:解决|方案|修复|搞定)[：:]?\s*(.+)', '方案')
        
        # 提取教训
        lessons = self._extract_patterns(block, r'(?:教训|学到|注意|切记)[：:]?\s*(.+)', '教训')
        
        # 提取可复用代码片段
        snippets = self._extract_code_snippets(block, task_id)
        
        return TaskRecord(
            task_id=task_id,
            timestamp=datetime.now(),
            agent="代码检查",  # 当前Agent
            task_type=task_type,
            description=description,
            outcome=outcome,
            duration_minutes=0,  # 可从文本中提取
            tools_used=tools,
            skills_applied=skills,
            problems_encountered=problems,
            solutions_found=solutions,
            lessons_learned=lessons,
            reusable_snippets=snippets
        )
    
    def _detect_task_type(self, text: str) -> TaskType:
        """检测任务类型"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['开发', '编写', '实现', '代码', 'commit', 'push']):
            return TaskType.CODE
        elif any(kw in text_lower for kw in ['分析', '统计', '计算', '数据']):
            return TaskType.ANALYSIS
        elif any(kw in text_lower for kw in ['文档', 'readme', 'md', '说明']):
            return TaskType.WRITING
        elif any(kw in text_lower for kw in ['修复', 'bug', '错误', 'debug']):
            return TaskType.DEBUG
        elif any(kw in text_lower for kw in ['调研', '研究', '调查', '分析']):
            return TaskType.RESEARCH
        elif any(kw in text_lower for kw in ['沟通', '协调', '讨论', '会议']):
            return TaskType.COMMUNICATION
        
        return TaskType.OTHER
    
    def _detect_outcome(self, text: str) -> TaskOutcome:
        """检测任务结果"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['✅', '完成', '搞定', 'success', 'done']):
            return TaskOutcome.SUCCESS
        elif any(kw in text_lower for kw in ['❌', '失败', '取消', '放弃', 'fail']):
            return TaskOutcome.FAILURE
        elif any(kw in text_lower for kw in ['🟡', '部分', '延期', '延迟', 'partial']):
            return TaskOutcome.PARTIAL
        
        return TaskOutcome.SUCCESS  # 默认成功
    
    def _extract_tools(self, text: str) -> List[str]:
        """提取使用的工具"""
        tools = []
        tool_patterns = [
            r'(?:使用|用|通过)\s+([A-Za-z_]+)',
            r'`([^`]+)`',
            r'gh\s+\w+',
            r'git\s+\w+',
            r'python\s+\w+',
            r'pytest',
            r'flake8',
            r'black'
        ]
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tools.extend(matches)
        
        return list(set(tools))[:10]  # 去重，最多10个
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取应用的技能"""
        skills = []
        
        # 从SKILL.md文件名提取
        if SKILLS_DIR.exists():
            for skill_file in SKILLS_DIR.glob("*/SKILL.md"):
                skill_name = skill_file.parent.name
                if skill_name.lower() in text.lower():
                    skills.append(skill_name)
        
        return skills
    
    def _extract_patterns(self, text: str, pattern: str, prefix: str) -> List[str]:
        """提取特定模式的内容"""
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        return [f"{prefix}: {m.strip()}" for m in matches[:5]]  # 最多5个
    
    def _extract_code_snippets(self, text: str, task_id: str) -> List[Dict]:
        """提取可复用的代码片段"""
        snippets = []
        
        # 提取代码块
        code_blocks = re.findall(r'```(?:python|bash|json)?\n(.*?)```', text, re.DOTALL)
        
        for i, code in enumerate(code_blocks):
            if len(code.strip()) > 50:  # 只保存有意义的片段
                snippet = {
                    'id': f"{task_id}_{i}",
                    'language': self._detect_language(code),
                    'code': code.strip()[:500],  # 限制长度
                    'description': self._generate_snippet_description(code)
                }
                snippets.append(snippet)
        
        return snippets
    
    def _detect_language(self, code: str) -> str:
        """检测代码语言"""
        if 'def ' in code or 'import ' in code:
            return 'python'
        elif 'function' in code or 'const ' in code:
            return 'javascript'
        elif 'git ' in code or 'pip ' in code:
            return 'bash'
        return 'text'
    
    def _generate_snippet_description(self, code: str) -> str:
        """生成代码片段描述"""
        lines = code.strip().split('\n')
        
        # 找注释或函数名
        for line in lines[:3]:
            if line.strip().startswith('#') or line.strip().startswith('//'):
                return line.strip('#/ ')
            if 'def ' in line or 'class ' in line:
                return line.strip()
        
        return "代码片段"
    
    def generate_review_template(self, task: TaskRecord) -> str:
        """生成复盘模板"""
        template = f"""# 任务复盘: {task.description}

## 基本信息
- **任务ID**: {task.task_id}
- **时间**: {task.timestamp.strftime('%Y-%m-%d %H:%M')}
- **Agent**: {task.agent}
- **类型**: {task.task_type.value}
- **结果**: {task.outcome.value}
- **耗时**: {task.duration_minutes} 分钟

## 使用的工具
{self._format_list(task.tools_used)}

## 应用的技能
{self._format_list(task.skills_applied)}

## 遇到的问题
{self._format_list(task.problems_encountered)}

## 解决方案
{self._format_list(task.solutions_found)}

## 经验教训
{self._format_list(task.lessons_learned)}

## 可复用片段
{self._format_snippets(task.reusable_snippets)}

## 改进建议
- [ ] 
- [ ] 
- [ ] 

---
*自动生成的复盘模板，由 Evolution Assistant 创建*
"""
        return template
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return "- 无"
        return '\n'.join([f"- {item}" for item in items])
    
    def _format_snippets(self, snippets: List[Dict]) -> str:
        """格式化代码片段"""
        if not snippets:
            return "- 无"
        
        result = []
        for s in snippets:
            result.append(f"### {s['description']}")
            result.append(f"```\n{s['code'][:200]}...\n```")
        return '\n\n'.join(result)
    
    def save_review(self, task: TaskRecord) -> Path:
        """保存复盘文档"""
        template = self.generate_review_template(task)
        
        review_file = self.tasks_dir / f"review_{task.task_id}_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(review_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"📝 复盘已保存: {review_file.name}")
        return review_file
    
    def extract_knowledge_snippets(self, tasks: List[TaskRecord]) -> List[KnowledgeSnippet]:
        """提取知识片段"""
        snippets = []
        
        for task in tasks:
            # 从教训中提取
            for lesson in task.lessons_learned:
                snippet = KnowledgeSnippet(
                    snippet_id=hashlib.md5(lesson.encode()).hexdigest()[:8],
                    category='lesson',
                    content=lesson,
                    source_task=task.task_id,
                    created_at=datetime.now(),
                    tags=[task.task_type.value, 'lesson']
                )
                snippets.append(snippet)
            
            # 从解决方案中提取
            for solution in task.solutions_found:
                snippet = KnowledgeSnippet(
                    snippet_id=hashlib.md5(solution.encode()).hexdigest()[:8],
                    category='pattern',
                    content=solution,
                    source_task=task.task_id,
                    created_at=datetime.now(),
                    tags=[task.task_type.value, 'solution']
                )
                snippets.append(snippet)
            
            # 从代码片段中提取
            for code_snippet in task.reusable_snippets:
                snippet = KnowledgeSnippet(
                    snippet_id=code_snippet['id'],
                    category='code',
                    content=code_snippet['code'],
                    source_task=task.task_id,
                    created_at=datetime.now(),
                    tags=[code_snippet['language'], 'code']
                )
                snippets.append(snippet)
        
        return snippets
    
    def save_snippets(self, snippets: List[KnowledgeSnippet]):
        """保存知识片段"""
        for snippet in snippets:
            snippet_file = self.snippets_dir / f"{snippet.snippet_id}.json"
            
            with open(snippet_file, 'w', encoding='utf-8') as f:
                json.dump(snippet.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"💎 已保存 {len(snippets)} 个知识片段")
    
    def update_skill_md(self, snippets: List[KnowledgeSnippet]):
        """更新SKILL.md（可选）"""
        # 按技能分类
        skill_updates = {}
        
        for snippet in snippets:
            for tag in snippet.tags:
                if tag not in skill_updates:
                    skill_updates[tag] = []
                skill_updates[tag].append(snippet)
        
        # 这里可以自动更新具体的SKILL.md文件
        # 暂时只打印建议
        print("\n📝 建议更新的技能文档:")
        for skill, items in skill_updates.items():
            print(f"  - {skill}: 添加 {len(items)} 条知识")
    
    def update_memory_md(self, tasks: List[TaskRecord]):
        """更新MEMORY.md"""
        memory_file = self.workspace / "MEMORY.md"
        
        # 读取现有内容
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# 长期记忆\n\n"
        
        # 生成新的记忆条目
        today = datetime.now().strftime('%Y-%m-%d')
        new_entry = f"\n## {today} 自动更新\n\n"
        new_entry += f"**今日完成任务**: {len(tasks)} 个\n\n"
        
        # 提取重要教训
        all_lessons = []
        for task in tasks:
            all_lessons.extend(task.lessons_learned)
        
        if all_lessons:
            new_entry += "### 重要教训\n\n"
            for lesson in all_lessons[:5]:  # 最多5条
                new_entry += f"- {lesson}\n"
            new_entry += "\n"
        
        # 追加到文件
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(new_entry)
        
        print(f"🧠 已更新 MEMORY.md")
    
    def generate_daily_report(self, tasks: List[TaskRecord]) -> str:
        """生成每日进化报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        report = f"""# 📊 进化日报 ({today})

## 今日概览
- **完成任务**: {len(tasks)} 个
- **成功**: {sum(1 for t in tasks if t.outcome == TaskOutcome.SUCCESS)} 个
- **部分成功**: {sum(1 for t in tasks if t.outcome == TaskOutcome.PARTIAL)} 个
- **失败**: {sum(1 for t in tasks if t.outcome == TaskOutcome.FAILURE)} 个

## 任务类型分布
"""
        
        # 统计任务类型
        type_counts = {}
        for task in tasks:
            type_counts[task.task_type.value] = type_counts.get(task.task_type.value, 0) + 1
        
        for task_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"- {task_type}: {count} 个\n"
        
        report += "\n## 使用的工具\n"
        all_tools = []
        for task in tasks:
            all_tools.extend(task.tools_used)
        
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- {tool}: {count} 次\n"
        
        report += "\n## 重要教训\n"
        all_lessons = []
        for task in tasks:
            all_lessons.extend(task.lessons_learned)
        
        if all_lessons:
            for lesson in all_lessons[:10]:
                report += f"- {lesson}\n"
        else:
            report += "- 暂无\n"
        
        report += """

## 明日改进建议
- [ ] 继续完善自动进化系统
- [ ] 提取更多可复用知识
- [ ] 优化任务分析准确度

---
*由 Evolution Assistant 自动生成*
"""
        
        return report
    
    def run_full_evolution(self):
        """运行完整的进化流程"""
        print("🚀 启动进化助手 v2.0\n")
        print("=" * 50)
        
        # 1. 分析今日任务
        print("\n📖 Phase 1: 分析今日任务")
        tasks = self.analyze_today_tasks()
        
        if not tasks:
            print("⚠️ 未找到今日任务，退出")
            return
        
        # 2. 生成复盘
        print("\n📝 Phase 2: 生成任务复盘")
        for task in tasks:
            self.save_review(task)
        
        # 3. 提取知识片段
        print("\n💎 Phase 3: 提取知识片段")
        snippets = self.extract_knowledge_snippets(tasks)
        self.save_snippets(snippets)
        
        # 4. 更新记忆文件
        print("\n🧠 Phase 4: 更新记忆文件")
        self.update_memory_md(tasks)
        self.update_skill_md(snippets)
        
        # 5. 生成日报
        print("\n📊 Phase 5: 生成进化日报")
        report = self.generate_daily_report(tasks)
        
        report_file = self.evolution_dir / f"report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 进化完成！")
        print(f"📄 日报已保存: {report_file.name}")
        print(f"💡 共提取 {len(snippets)} 个知识片段")
        print(f"📝 生成 {len(tasks)} 个复盘文档")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Dragon Judge 进化助手')
    parser.add_argument('--analyze', action='store_true', help='分析今日任务')
    parser.add_argument('--review', action='store_true', help='生成复盘')
    parser.add_argument('--extract', action='store_true', help='提取知识')
    parser.add_argument('--update', action='store_true', help='更新记忆文件')
    parser.add_argument('--full', action='store_true', help='运行完整进化流程')
    parser.add_argument('--report', action='store_true', help='生成日报')
    
    args = parser.parse_args()
    
    assistant = EvolutionAssistant()
    
    if args.full or (not any([args.analyze, args.review, args.extract, args.update, args.report])):
        # 默认运行完整流程
        assistant.run_full_evolution()
    elif args.analyze:
        tasks = assistant.analyze_today_tasks()
        print(f"\n找到 {len(tasks)} 个任务")
        for task in tasks:
            print(f"- [{task.task_type.value}] {task.description[:50]}")
    elif args.report:
        tasks = assistant.analyze_today_tasks()
        report = assistant.generate_daily_report(tasks)
        print(report)

if __name__ == "__main__":
    main()
