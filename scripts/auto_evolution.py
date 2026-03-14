#!/usr/bin/env python3
"""
记忆自动进化系统 (Memory Auto-Evolution System)

自动从任务中学习，持续改进 Agent 的能力和工作方式
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re

# 配置路径
WORKSPACE_ROOT = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
EVOLUTION_DIR = MEMORY_DIR / "evolution"

class TaskOutcome(Enum):
    """任务结果类型"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CANCELLED = "cancelled"

@dataclass
class TaskLog:
    """任务日志"""
    task_id: str
    description: str
    agent: str
    start_time: datetime
    end_time: datetime
    outcome: TaskOutcome
    steps: List[str]
    issues: List[str]
    solutions: List[str]
    lessons: List[str]
    tools_used: List[str]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'outcome': self.outcome.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskLog':
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        data['outcome'] = TaskOutcome(data['outcome'])
        return cls(**data)

class MemoryEvolutionSystem:
    """记忆自动进化系统"""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace = workspace_root or WORKSPACE_ROOT
        self.memory_dir = self.workspace / "memory"
        self.evolution_dir = self.memory_dir / "evolution"
        
        # 确保目录存在
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        (self.evolution_dir / "task_logs").mkdir(exist_ok=True)
        (self.evolution_dir / "lessons").mkdir(exist_ok=True)
        (self.evolution_dir / "patterns").mkdir(exist_ok=True)
    
    def log_task(self, task_log: TaskLog) -> None:
        """记录任务日志"""
        log_file = self.evolution_dir / "task_logs" / f"{task_log.task_id}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(task_log.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"✅ 任务日志已记录: {task_log.task_id}")
        
        # 自动提取教训
        self._extract_lessons(task_log)
    
    def _extract_lessons(self, task_log: TaskLog) -> None:
        """从任务中提取教训"""
        lessons = []
        
        # 基于结果提取教训
        if task_log.outcome == TaskOutcome.SUCCESS:
            lessons.append(f"✅ 成功经验: {task_log.description}")
            if task_log.solutions:
                lessons.append(f"   解决方案: {', '.join(task_log.solutions)}")
        
        elif task_log.outcome == TaskOutcome.FAILURE:
            lessons.append(f"❌ 失败教训: {task_log.description}")
            if task_log.issues:
                lessons.append(f"   问题原因: {', '.join(task_log.issues)}")
            if task_log.solutions:
                lessons.append(f"   解决方法: {', '.join(task_log.solutions)}")
        
        # 记录自定义教训
        for lesson in task_log.lessons:
            lessons.append(f"💡 {lesson}")
        
        # 保存教训
        if lessons:
            lesson_file = self.evolution_dir / "lessons" / f"{task_log.task_id}.md"
            with open(lesson_file, 'w', encoding='utf-8') as f:
                f.write(f"# 任务教训: {task_log.description}\n\n")
                f.write(f"**时间**: {task_log.end_time.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"**Agent**: {task_log.agent}\n")
                f.write(f"**结果**: {task_log.outcome.value}\n\n")
                f.write("## 教训总结\n\n")
                for lesson in lessons:
                    f.write(f"- {lesson}\n")
            
            print(f"💡 已提取 {len(lessons)} 条教训")
    
    def daily_cleanup(self) -> None:
        """每日记忆整理"""
        today = datetime.now()
        daily_file = self.memory_dir / f"{today.strftime('%Y-%m-%d')}.md"
        
        if not daily_file.exists():
            print("⚠️ 今日记忆文件不存在")
            return
        
        print(f"🧹 开始整理今日记忆: {daily_file.name}")
        
        # 读取今日记忆
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取关键信息
        key_events = self._extract_key_events(content)
        
        # 更新长期记忆
        if key_events:
            self._update_long_term_memory(key_events)
        
        print(f"✅ 每日整理完成，提取 {len(key_events)} 个关键事件")
    
    def _extract_key_events(self, content: str) -> List[Dict]:
        """从记忆内容中提取关键事件"""
        events = []
        
        # 简单规则：提取标题和列表项
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            # 检测标题
            if line.startswith('# '):
                current_section = line[2:].strip()
            
            # 检测重要标记
            elif any(marker in line for marker in ['✅', '❌', '🔴', '🚨', '💡', '🎯']):
                events.append({
                    'section': current_section,
                    'content': line.strip(),
                    'type': 'significant'
                })
            
            # 检测决策记录
            elif '决策' in line or '决定' in line:
                events.append({
                    'section': current_section,
                    'content': line.strip(),
                    'type': 'decision'
                })
        
        return events
    
    def _update_long_term_memory(self, events: List[Dict]) -> None:
        """更新长期记忆文件"""
        memory_file = self.workspace / "MEMORY.md"
        
        # 读取现有内容
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                existing = f.read()
        else:
            existing = "# 长期记忆\n\n"
        
        # 添加新事件
        new_content = f"\n## {datetime.now().strftime('%Y-%m-%d')} 更新\n\n"
        for event in events:
            if event['type'] == 'significant':
                new_content += f"- {event['content']}\n"
        
        # 写入文件
        with open(memory_file, 'a', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"📝 已更新长期记忆: {len(events)} 个事件")
    
    def analyze_patterns(self, days: int = 7) -> Dict:
        """分析近期任务模式"""
        task_logs_dir = self.evolution_dir / "task_logs"
        
        if not task_logs_dir.exists():
            return {}
        
        # 读取近期日志
        logs = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in task_logs_dir.glob("*.json"):
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                log_time = datetime.fromisoformat(data['end_time'])
                if log_time > cutoff:
                    logs.append(TaskLog.from_dict(data))
        
        # 统计分析
        analysis = {
            'total_tasks': len(logs),
            'success_rate': 0,
            'common_issues': {},
            'common_tools': {},
            'avg_duration': 0
        }
        
        if logs:
            success_count = sum(1 for log in logs if log.outcome == TaskOutcome.SUCCESS)
            analysis['success_rate'] = success_count / len(logs)
            
            # 统计常见问题
            for log in logs:
                for issue in log.issues:
                    analysis['common_issues'][issue] = analysis['common_issues'].get(issue, 0) + 1
                for tool in log.tools_used:
                    analysis['common_tools'][tool] = analysis['common_tools'].get(tool, 0) + 1
            
            # 平均耗时
            durations = [(log.end_time - log.start_time).total_seconds() / 60 for log in logs]
            analysis['avg_duration'] = sum(durations) / len(durations)
        
        return analysis
    
    def generate_report(self) -> str:
        """生成进化报告"""
        analysis = self.analyze_patterns(days=7)
        
        report = f"""# 记忆自动进化报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 本周统计

- **总任务数**: {analysis.get('total_tasks', 0)}
- **成功率**: {analysis.get('success_rate', 0) * 100:.1f}%
- **平均耗时**: {analysis.get('avg_duration', 0):.1f} 分钟

## 🔍 常见问题

"""
        
        # 添加常见问题
        common_issues = analysis.get('common_issues', {})
        if common_issues:
            sorted_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            for issue, count in sorted_issues:
                report += f"- {issue}: {count} 次\n"
        else:
            report += "- 暂无足够数据\n"
        
        report += "\n## 🛠️ 常用工具\n\n"
        
        # 添加常用工具
        common_tools = analysis.get('common_tools', {})
        if common_tools:
            sorted_tools = sorted(common_tools.items(), key=lambda x: x[1], reverse=True)[:5]
            for tool, count in sorted_tools:
                report += f"- {tool}: {count} 次\n"
        else:
            report += "- 暂无足够数据\n"
        
        return report

def main():
    """主函数"""
    system = MemoryEvolutionSystem()
    
    import argparse
    parser = argparse.ArgumentParser(description='记忆自动进化系统')
    parser.add_argument('--daily-cleanup', action='store_true', help='执行每日整理')
    parser.add_argument('--analyze-patterns', action='store_true', help='分析任务模式')
    parser.add_argument('--report', action='store_true', help='生成进化报告')
    parser.add_argument('--setup-cron', action='store_true', help='设置定时任务')
    
    args = parser.parse_args()
    
    if args.daily_cleanup:
        system.daily_cleanup()
    
    elif args.analyze_patterns:
        analysis = system.analyze_patterns()
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    elif args.report:
        report = system.generate_report()
        print(report)
    
    elif args.setup_cron:
        print("设置定时任务...")
        print("建议添加到 crontab:")
        print("0 23 * * * python3 auto_evolution.py --daily-cleanup")
        print("0 0 * * 0 python3 auto_evolution.py --analyze-patterns")
    
    else:
        # 默认执行每日整理
        system.daily_cleanup()

if __name__ == "__main__":
    main()
