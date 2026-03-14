#!/usr/bin/env python3
"""
Dragon Judge - 简化版MVP主程序
整合数据抓取、情绪分析、报告生成

用法:
    python main.py              # 运行完整流程
    python main.py --fetch      # 仅抓取数据
    python main.py --analyze    # 仅分析数据
    python main.py --report     # 仅生成报告
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scoring.dragon_judge import DragonJudge


def fetch_data():
    """抓取数据（简化版，使用模拟数据）"""
    print("📊 正在获取市场数据...")
    
    # TODO: 集成真实数据抓取
    # 当前使用模拟数据验证流程
    data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'limit_up_count': 45,
        'limit_down_count': 8,
        'total_stocks': 5000,
        'leading_stocks': [
            {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
            {'code': '000002', 'name': '万科A', 'limit_up_days': 2},
            {'code': '600519', 'name': '贵州茅台', 'limit_up_days': 1},
        ]
    }
    
    print(f"✅ 数据获取完成")
    print(f"   涨停家数: {data['limit_up_count']}")
    print(f"   跌停家数: {data['limit_down_count']}")
    print(f"   龙头股: {len(data['leading_stocks'])} 只")
    
    return data


def analyze_data(data):
    """分析数据"""
    print("\n🐉 正在运行Dragon Judge分析...")
    
    dj = DragonJudge()
    
    sentiment = dj.calculate_sentiment(data)
    cycle = dj.detect_cycle(data)
    leaders = dj.select_leaders(data)
    
    print(f"✅ 分析完成")
    print(f"   情绪分数: {sentiment:.1f}/100")
    print(f"   市场周期: {cycle}")
    print(f"   龙头股: {len(leaders)} 只")
    
    return {
        'sentiment': sentiment,
        'cycle': cycle,
        'leaders': leaders
    }


def generate_report(data, analysis):
    """生成报告"""
    print("\n📝 正在生成报告...")
    
    report = {
        'date': data['date'],
        'sentiment_score': round(analysis['sentiment'], 2),
        'market_cycle': analysis['cycle'],
        'leading_stocks': [
            {
                'code': l.code,
                'name': l.name,
                'limit_up_days': l.limit_up_days,
                'score': round(l.score, 2)
            }
            for l in analysis['leaders'][:5]
        ],
        'strategy': generate_strategy(analysis['sentiment'], analysis['cycle'])
    }
    
    return report


def generate_strategy(sentiment, cycle):
    """生成策略建议"""
    if cycle == '冰点':
        return "空仓观望，等待冰点转折信号"
    elif cycle == '启动':
        return "轻仓试错，关注首板机会"
    elif cycle == '发酵':
        return "半仓参与，聚焦主线龙头"
    elif cycle == '高潮':
        return "高潮减仓，只留核心龙头"
    else:
        return "全面撤退，规避退潮风险"


def save_report(report, output_dir='output'):
    """保存报告"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # JSON格式
    json_file = Path(output_dir) / f"report_{report['date']}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Markdown格式（易读）
    md_file = Path(output_dir) / f"report_{report['date']}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Dragon Judge 情绪分析报告\n\n")
        f.write(f"**日期**: {report['date']}\n\n")
        f.write(f"## 📊 市场情绪\n\n")
        f.write(f"- **情绪分数**: {report['sentiment_score']}/100\n")
        f.write(f"- **市场周期**: {report['market_cycle']}\n\n")
        f.write(f"## 🐉 龙头股\n\n")
        for stock in report['leading_stocks']:
            f.write(f"- **{stock['name']}** ({stock['code']}): ")
            f.write(f"{stock['limit_up_days']}板, 评分{stock['score']}\n")
        f.write(f"\n## 🎯 策略建议\n\n")
        f.write(f"{report['strategy']}\n\n")
        f.write(f"---\n*Dragon Judge MVP v1.0*\n")
    
    print(f"✅ 报告已保存")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    
    return md_file


def print_report(report):
    """打印报告到控制台"""
    print("\n" + "="*50)
    print("📊 Dragon Judge 情绪分析报告")
    print("="*50)
    print(f"\n📅 日期: {report['date']}")
    print(f"🌡️  情绪分数: {report['sentiment_score']}/100")
    print(f"📈 市场周期: {report['market_cycle']}")
    print(f"\n🐉 龙头股:")
    for i, stock in enumerate(report['leading_stocks'], 1):
        print(f"   {i}. {stock['name']} ({stock['code']}) - ", end='')
        print(f"{stock['limit_up_days']}板 - 评分{stock['score']}")
    print(f"\n🎯 策略建议:")
    print(f"   {report['strategy']}")
    print("\n" + "="*50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Dragon Judge MVP')
    parser.add_argument('--fetch', action='store_true', help='仅抓取数据')
    parser.add_argument('--analyze', action='store_true', help='仅分析数据')
    parser.add_argument('--report', action='store_true', help='仅生成报告')
    parser.add_argument('--output', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    print("🚀 Dragon Judge MVP v1.0")
    print("="*50)
    
    # 阶段1: 抓取数据
    data = fetch_data()
    if args.fetch:
        print("\n✅ 数据抓取完成")
        return
    
    # 阶段2: 分析数据
    analysis = analyze_data(data)
    if args.analyze:
        print("\n✅ 数据分析完成")
        return
    
    # 阶段3: 生成报告
    report = generate_report(data, analysis)
    save_report(report, args.output)
    print_report(report)
    
    print("\n✅ 全流程运行完成！")


if __name__ == "__main__":
    main()
