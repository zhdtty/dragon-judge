#!/usr/bin/env python3
"""
Dragon Judge - A股情绪龙头分析系统主程序

整合数据抓取、情绪分析、报告生成全流程

用法:
    python main.py                    # 运行完整流程
    python main.py --fetch            # 仅抓取数据
    python main.py --analyze          # 仅分析数据
    python main.py --report           # 仅生成报告
    python main.py --config config.yaml  # 使用指定配置文件
    python main.py --verbose          # 显示详细日志

环境变量:
    DRAGON_JUDGE_CONFIG: 配置文件路径
    DRAGON_JUDGE_LOG_LEVEL: 日志级别 (DEBUG/INFO/WARNING/ERROR)
"""

import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scoring.dragon_judge import (
    DragonJudge, 
    MarketData,
    LeadingStock,
    MarketCycle,
    DragonJudgeError
)


# ==================== 配置管理 ====================

@dataclass
class AppConfig:
    """应用程序配置"""
    # 数据配置
    output_dir: str = "output"
    data_source: str = "mock"  # mock, tushare, akshare
    
    # 评分配置
    weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None
    
    # 报告配置
    report_format: str = "markdown"  # markdown, json, both
    max_leaders: int = 10
    include_details: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """从字典创建配置"""
        return cls(
            output_dir=data.get('output_dir', 'output'),
            data_source=data.get('data_source', 'mock'),
            weights=data.get('weights'),
            thresholds=data.get('thresholds'),
            report_format=data.get('report_format', 'markdown'),
            max_leaders=data.get('max_leaders', 10),
            include_details=data.get('include_details', False),
            log_level=data.get('log_level', 'INFO'),
            log_file=data.get('log_file'),
        )
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "AppConfig":
        """从 YAML 文件加载配置"""
        import yaml
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_json(cls, filepath: str) -> "AppConfig":
        """从 JSON 文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'output_dir': self.output_dir,
            'data_source': self.data_source,
            'weights': self.weights,
            'thresholds': self.thresholds,
            'report_format': self.report_format,
            'max_leaders': self.max_leaders,
            'include_details': self.include_details,
            'log_level': self.log_level,
            'log_file': self.log_file,
        }


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    加载应用程序配置
    
    优先级:
    1. 指定的配置文件路径
    2. 环境变量 DRAGON_JUDGE_CONFIG
    3. 默认配置文件 (config/config.yaml)
    4. 使用默认配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        AppConfig 配置对象
    """
    import os
    
    # 确定配置文件路径
    if config_path:
        filepath = Path(config_path)
    elif os.getenv('DRAGON_JUDGE_CONFIG'):
        filepath = Path(os.getenv('DRAGON_JUDGE_CONFIG'))
    else:
        # 尝试默认配置
        default_paths = [
            Path('config/config.yaml'),
            Path('config/config.yml'),
            Path('config/config.json'),
            Path('config/config.example.yaml'),
        ]
        for p in default_paths:
            if p.exists():
                filepath = p
                break
        else:
            logging.warning("未找到配置文件，使用默认配置")
            return AppConfig()
    
    if not filepath.exists():
        logging.warning(f"配置文件不存在: {filepath}，使用默认配置")
        return AppConfig()
    
    # 根据文件扩展名选择加载方式
    suffix = filepath.suffix.lower()
    try:
        if suffix in ['.yaml', '.yml']:
            return AppConfig.from_yaml(str(filepath))
        elif suffix == '.json':
            return AppConfig.from_json(str(filepath))
        else:
            logging.warning(f"不支持的配置文件格式: {suffix}，使用默认配置")
            return AppConfig()
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        return AppConfig()


# ==================== 日志配置 ====================

def setup_logging(
    level: str = "INFO", 
    log_file: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        verbose: 是否显示详细日志
        
    Returns:
        配置好的 Logger 实例
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    if verbose:
        log_level = logging.DEBUG
    
    # 日志格式
    console_format = "%(message)s"
    file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置根日志器
    handlers: List[logging.Handler] = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(console_format))
    handlers.append(console_handler)
    
    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(file_format))
        handlers.append(file_handler)
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )
    
    logger = logging.getLogger('dragon_judge')
    logger.debug(f"日志级别设置为: {logging.getLevelName(log_level)}")
    
    return logger


# ==================== 数据获取 ====================

class DataFetcher:
    """数据获取器"""
    
    def __init__(self, source: str = "mock") -> None:
        """
        初始化数据获取器
        
        Args:
            source: 数据源 (mock, tushare, akshare)
        """
        self.source = source
        self.logger = logging.getLogger('dragon_judge.fetcher')
    
    def fetch(self) -> MarketData:
        """
        获取市场数据
        
        Returns:
            MarketData 市场数据对象
        """
        fetchers = {
            'mock': self._fetch_mock,
            'tushare': self._fetch_tushare,
            'akshare': self._fetch_akshare,
        }
        
        fetcher = fetchers.get(self.source, self._fetch_mock)
        return fetcher()
    
    def _fetch_mock(self) -> MarketData:
        """获取模拟数据"""
        self.logger.info("📊 使用模拟数据...")
        
        return MarketData(
            date=datetime.now().strftime('%Y-%m-%d'),
            limit_up_count=45,
            limit_down_count=8,
            total_stocks=5000,
            leading_stocks=[
                {'code': '000001', 'name': '平安银行', 'limit_up_days': 3, 'sector': '金融'},
                {'code': '000002', 'name': '万科A', 'limit_up_days': 2, 'sector': '地产'},
                {'code': '600519', 'name': '贵州茅台', 'limit_up_days': 1, 'sector': '消费'},
                {'code': '300750', 'name': '宁德时代', 'limit_up_days': 4, 'sector': '新能源'},
                {'code': '002594', 'name': '比亚迪', 'limit_up_days': 2, 'sector': '新能源'},
            ],
            sector_data={
                '新能源': {'follower_count': 8, 'limit_up_count': 12},
                '金融': {'follower_count': 3, 'limit_up_count': 5},
                '地产': {'follower_count': 2, 'limit_up_count': 4},
                '消费': {'follower_count': 4, 'limit_up_count': 6},
            }
        )
    
    def _fetch_tushare(self) -> MarketData:
        """从 Tushare 获取数据 (待实现)"""
        self.logger.warning("Tushare 数据源尚未实现，使用模拟数据")
        return self._fetch_mock()
    
    def _fetch_akshare(self) -> MarketData:
        """从 AKShare 获取数据 (待实现)"""
        self.logger.warning("AKShare 数据源尚未实现，使用模拟数据")
        return self._fetch_mock()


# ==================== 报告生成 ====================

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: AppConfig) -> None:
        """
        初始化报告生成器
        
        Args:
            config: 应用配置
        """
        self.config = config
        self.logger = logging.getLogger('dragon_judge.report')
    
    def generate(
        self, 
        data: MarketData, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成报告
        
        Args:
            data: 市场数据
            analysis: 分析结果
            
        Returns:
            报告字典
        """
        report = {
            'date': data.date,
            'sentiment_score': round(analysis['sentiment'], 2),
            'market_cycle': analysis['cycle'].cn_name,
            'market_cycle_display': analysis['cycle'].display_name,
            'leading_stocks': [
                {
                    'code': l.code,
                    'name': l.name,
                    'limit_up_days': l.limit_up_days,
                    'score': round(l.score, 2)
                }
                for l in analysis['leaders'][:self.config.max_leaders]
            ],
            'strategy': self._generate_strategy(analysis['sentiment'], analysis['cycle']),
        }
        
        return report
    
    def _generate_strategy(self, sentiment: float, cycle: MarketCycle) -> str:
        """生成策略建议"""
        strategies = {
            MarketCycle.ICE_POINT: "空仓观望，等待冰点转折信号",
            MarketCycle.START: "轻仓试错，关注首板机会",
            MarketCycle.FERMENTATION: "半仓参与，聚焦主线龙头",
            MarketCycle.CLIMAX: "高潮减仓，只留核心龙头",
            MarketCycle.DIVERGENCE: "全面撤退，规避退潮风险"
        }
        
        strategy = strategies.get(cycle, "观望为主，等待明确信号")
        
        if sentiment > 90:
            strategy += " ⚠️ 情绪过热，注意风险"
        elif sentiment < 10:
            strategy += " 💡 极度冰点，关注反转机会"
        
        return strategy
    
    def save(
        self, 
        report: Dict[str, Any], 
        output_dir: str,
        format_type: str = "markdown"
    ) -> List[Path]:
        """
        保存报告
        
        Args:
            report: 报告字典
            output_dir: 输出目录
            format_type: 格式类型 (markdown, json, both)
            
        Returns:
            保存的文件路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files: List[Path] = []
        date = report['date']
        
        # 保存 JSON
        if format_type in ['json', 'both']:
            json_file = output_path / f"report_{date}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            saved_files.append(json_file)
            self.logger.debug(f"JSON 报告已保存: {json_file}")
        
        # 保存 Markdown
        if format_type in ['markdown', 'both']:
            md_file = output_path / f"report_{date}.md"
            self._save_markdown(report, md_file)
            saved_files.append(md_file)
            self.logger.debug(f"Markdown 报告已保存: {md_file}")
        
        return saved_files
    
    def _save_markdown(self, report: Dict[str, Any], filepath: Path) -> None:
        """保存 Markdown 格式报告"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 🐉 Dragon Judge 情绪分析报告\n\n")
            f.write(f"**日期**: {report['date']}\n\n")
            f.write(f"---\n\n")
            
            # 市场情绪
            f.write(f"## 📊 市场情绪\n\n")
            f.write(f"- **情绪分数**: {report['sentiment_score']}/100\n")
            f.write(f"- **市场周期**: {report['market_cycle_display']}\n\n")
            
            # 龙头股
            f.write(f"## 🐉 龙头股排行\n\n")
            f.write(f"| 排名 | 股票名称 | 代码 | 连板数 | 评分 |\n")
            f.write(f"|------|----------|------|--------|------|\n")
            for i, stock in enumerate(report['leading_stocks'], 1):
                f.write(f"| {i} | {stock['name']} | {stock['code']} | ")
                f.write(f"{stock['limit_up_days']}板 | {stock['score']} |\n")
            f.write(f"\n")
            
            # 策略建议
            f.write(f"## 🎯 策略建议\n\n")
            f.write(f"> {report['strategy']}\n\n")
            
            f.write(f"---\n")
            f.write(f"*Generated by Dragon Judge v2.0*\n")
    
    def print_console(self, report: Dict[str, Any]) -> None:
        """打印报告到控制台"""
        print("\n" + "="*60)
        print("🐉 Dragon Judge 情绪分析报告")
        print("="*60)
        print(f"\n📅 日期: {report['date']}")
        print(f"🌡️  情绪分数: {report['sentiment_score']}/100")
        print(f"📈 市场周期: {report['market_cycle_display']}")
        print(f"\n🐉 龙头股:")
        for i, stock in enumerate(report['leading_stocks'], 1):
            print(f"   {i}. {stock['name']} ({stock['code']}) - ", end='')
            print(f"{stock['limit_up_days']}板 - 评分{stock['score']}")
        print(f"\n🎯 策略建议:")
        print(f"   {report['strategy']}")
        print("\n" + "="*60)


# ==================== 主程序 ====================

def create_argument_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        description='Dragon Judge - A股情绪龙头分析系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py                    # 运行完整流程
    python main.py --fetch            # 仅抓取数据
    python main.py --analyze          # 仅分析数据
    python main.py --config config.yaml --verbose
        """
    )
    
    # 运行模式
    parser.add_argument(
        '--fetch', 
        action='store_true',
        help='仅抓取数据'
    )
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='仅分析数据'
    )
    parser.add_argument(
        '--report', 
        action='store_true',
        help='仅生成报告'
    )
    
    # 配置选项
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='配置文件路径'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='输出目录 (默认: output)'
    )
    parser.add_argument(
        '--source', '-s',
        type=str,
        choices=['mock', 'tushare', 'akshare'],
        help='数据源'
    )
    
    # 报告选项
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['markdown', 'json', 'both'],
        help='报告格式'
    )
    parser.add_argument(
        '--max-leaders',
        type=int,
        default=10,
        help='显示龙头股数量 (默认: 10)'
    )
    
    # 日志选项
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='日志文件路径'
    )
    
    return parser


def main() -> int:
    """
    主函数
    
    Returns:
        退出码 (0=成功, 1=错误)
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.source:
        config.data_source = args.source
    if args.format:
        config.report_format = args.format
    if args.max_leaders:
        config.max_leaders = args.max_leaders
    if args.log_level:
        config.log_level = args.log_level
    if args.log_file:
        config.log_file = args.log_file
    
    # 设置日志
    logger = setup_logging(
        level=config.log_level,
        log_file=config.log_file,
        verbose=args.verbose
    )
    
    logger.info("🚀 Dragon Judge v2.0 启动")
    logger.info("="*60)
    
    try:
        # 阶段1: 抓取数据
        logger.info("📊 正在获取市场数据...")
        fetcher = DataFetcher(source=config.data_source)
        data = fetcher.fetch()
        
        logger.info(f"✅ 数据获取完成")
        logger.info(f"   涨停家数: {data.limit_up_count}")
        logger.info(f"   跌停家数: {data.limit_down_count}")
        logger.info(f"   龙头股: {len(data.leading_stocks)} 只")
        
        if args.fetch:
            logger.info("✅ 数据抓取完成")
            return 0
        
        # 阶段2: 分析数据
        logger.info("\n🐉 正在运行 Dragon Judge 分析...")
        dj = DragonJudge(config=config.to_dict())
        
        sentiment = dj.calculate_sentiment(data)
        cycle = dj.detect_cycle(data)
        leaders = dj.select_leaders(data, top_n=config.max_leaders)
        
        analysis = {
            'sentiment': sentiment,
            'cycle': cycle,
            'leaders': leaders
        }
        
        logger.info(f"✅ 分析完成")
        logger.info(f"   情绪分数: {sentiment:.1f}/100")
        logger.info(f"   市场周期: {cycle.display_name}")
        logger.info(f"   龙头股: {len(leaders)} 只")
        
        if args.analyze:
            logger.info("✅ 数据分析完成")
            return 0
        
        # 阶段3: 生成报告
        logger.info("\n📝 正在生成报告...")
        report_gen = ReportGenerator(config)
        report = report_gen.generate(data, analysis)
        
        output_dir = args.output or config.output_dir
        saved_files = report_gen.save(report, output_dir, config.report_format)
        report_gen.print_console(report)
        
        logger.info(f"\n✅ 报告已保存:")
        for f in saved_files:
            logger.info(f"   - {f}")
        
        if args.report:
            logger.info("✅ 报告生成完成")
            return 0
        
        logger.info("\n✅ 全流程运行完成！")
        return 0
        
    except DragonJudgeError as e:
        logger.error(f"Dragon Judge 错误: {e.message}")
        return 1
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断")
        return 130
    except Exception as e:
        logger.exception(f"发生未预期的错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
