"""
Dragon Judge 全面测试套件
包含单元测试、边界测试和异常处理测试
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.scoring.dragon_judge import (
    DragonJudge, LeadingStock, MarketData, MarketCycle,
    DragonJudgeError, InvalidDataError, ValidationError,
    InvalidCycleError, ConfigurationError
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def default_judge():
    """返回默认配置的 DragonJudge 实例"""
    return DragonJudge()


@pytest.fixture
def custom_config():
    """返回自定义配置"""
    return {
        'weights': {
            'height': 0.35,
            'competition': 0.35,
            'sector': 0.15,
            'sentiment': 0.10,
            'quality': 0.05
        },
        'thresholds': {
            'ice_point': 15.0,
            'start': 30.0,
            'fermentation': 55.0,
            'climax': 75.0,
            'divergence': 90.0
        }
    }


@pytest.fixture
def sample_market_data():
    """示例市场数据 - 正常情况"""
    return {
        "date": "2026-03-14",
        "limit_up_count": 45,
        "limit_down_count": 8,
        "total_stocks": 5000,
        "leading_stocks": [
            {"code": "000001", "name": "平安银行", "limit_up_days": 3},
            {"code": "000002", "name": "万科A", "limit_up_days": 2},
            {"code": "600519", "name": "贵州茅台", "limit_up_days": 3},
            {"code": "300750", "name": "宁德时代", "limit_up_days": 1},
        ]
    }


@pytest.fixture
def sample_market_data_obj():
    """示例 MarketData 对象"""
    return MarketData(
        date="2026-03-14",
        limit_up_count=45,
        limit_down_count=8,
        total_stocks=5000,
        leading_stocks=[
            {"code": "000001", "name": "平安银行", "limit_up_days": 3},
            {"code": "000002", "name": "万科A", "limit_up_days": 2},
        ]
    )


@pytest.fixture
def empty_market_data():
    """空市场数据"""
    return {
        "limit_up_count": 0,
        "limit_down_count": 0,
        "total_stocks": 5000,
        "leading_stocks": []
    }


@pytest.fixture
def extreme_ice_point_data():
    """极端冰点数据"""
    return {
        "date": "2026-03-14",
        "limit_up_count": 5,
        "limit_down_count": 200,
        "total_stocks": 5000,
        "leading_stocks": [
            {"code": "000001", "name": "平安银行", "limit_up_days": 1},
        ]
    }


@pytest.fixture
def extreme_climax_data():
    """极端高潮数据"""
    return {
        "date": "2026-03-14",
        "limit_up_count": 500,
        "limit_down_count": 0,
        "total_stocks": 5000,
        "leading_stocks": [
            {"code": "000001", "name": "平安银行", "limit_up_days": 10},
            {"code": "000002", "name": "万科A", "limit_up_days": 8},
            {"code": "600519", "name": "贵州茅台", "limit_up_days": 7},
            {"code": "300750", "name": "宁德时代", "limit_up_days": 6},
            {"code": "601398", "name": "工商银行", "limit_up_days": 6},
        ]
    }


@pytest.fixture
def sample_leading_stock():
    """示例龙头股票"""
    return LeadingStock(
        code="000001",
        name="平安银行",
        limit_up_days=3,
        score=0.0,
        height_score=0.0,
        competition_score=0.0,
        sector_score=0.0,
        sentiment_score=0.0,
        quality_score=0.0
    )


# =============================================================================
# MarketCycle 枚举测试
# =============================================================================

class TestMarketCycle:
    """测试 MarketCycle 枚举类"""
    
    def test_enum_values(self):
        """测试枚举值定义"""
        assert MarketCycle.ICE_POINT.cn_name == "冰点"
        assert MarketCycle.ICE_POINT.en_name == "ice_point"
        assert MarketCycle.ICE_POINT.emoji == "❄️"
        assert MarketCycle.START.cn_name == "启动"
        assert MarketCycle.START.en_name == "start"
        assert MarketCycle.START.emoji == "🚀"
        assert MarketCycle.FERMENTATION.cn_name == "发酵"
        assert MarketCycle.FERMENTATION.en_name == "fermentation"
        assert MarketCycle.FERMENTATION.emoji == "🔥"
        assert MarketCycle.CLIMAX.cn_name == "高潮"
        assert MarketCycle.CLIMAX.en_name == "climax"
        assert MarketCycle.CLIMAX.emoji == "🌟"
        assert MarketCycle.DIVERGENCE.cn_name == "分化/退潮"
        assert MarketCycle.DIVERGENCE.en_name == "divergence"
        assert MarketCycle.DIVERGENCE.emoji == "⚠️"
    
    def test_display_name(self):
        """测试显示名称"""
        assert "❄️" in MarketCycle.ICE_POINT.display_name
        assert "冰点" in MarketCycle.ICE_POINT.display_name
    
    def test_from_value_with_cn_name(self):
        """测试从中文名称获取枚举"""
        assert MarketCycle.from_value("冰点") == MarketCycle.ICE_POINT
        assert MarketCycle.from_value("启动") == MarketCycle.START
        assert MarketCycle.from_value("发酵") == MarketCycle.FERMENTATION
        assert MarketCycle.from_value("高潮") == MarketCycle.CLIMAX
        assert MarketCycle.from_value("分化/退潮") == MarketCycle.DIVERGENCE
    
    def test_from_value_with_en_name(self):
        """测试从英文名称获取枚举"""
        assert MarketCycle.from_value("ice_point") == MarketCycle.ICE_POINT
        assert MarketCycle.from_value("start") == MarketCycle.START
        assert MarketCycle.from_value("fermentation") == MarketCycle.FERMENTATION
        assert MarketCycle.from_value("climax") == MarketCycle.CLIMAX
        assert MarketCycle.from_value("divergence") == MarketCycle.DIVERGENCE
    
    def test_from_value_with_enum(self):
        """测试从枚举获取枚举"""
        assert MarketCycle.from_value(MarketCycle.ICE_POINT) == MarketCycle.ICE_POINT
    
    def test_from_value_invalid(self):
        """测试无效值抛出异常"""
        with pytest.raises(InvalidCycleError, match="Unknown market cycle: invalid"):
            MarketCycle.from_value("invalid")
        
        with pytest.raises(InvalidCycleError):
            MarketCycle.from_value("")


# =============================================================================
# LeadingStock 数据类测试
# =============================================================================

class TestLeadingStock:
    """测试 LeadingStock 数据类"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        stock = LeadingStock(code="000001", name="测试股票", limit_up_days=3)
        assert stock.code == "000001"
        assert stock.name == "测试股票"
        assert stock.limit_up_days == 3
        assert stock.score == 0.0
        assert stock.height_score == 0.0
        assert stock.competition_score == 0.0
        assert stock.sector_score == 0.0
        assert stock.sentiment_score == 0.0
        assert stock.quality_score == 0.0
        assert stock.sector is None
        assert stock.market_cap is None
    
    def test_full_initialization(self):
        """测试完整初始化"""
        stock = LeadingStock(
            code="000001",
            name="测试股票",
            limit_up_days=5,
            score=85.5,
            height_score=100.0,
            competition_score=80.0,
            sector_score=60.0,
            sentiment_score=70.0,
            quality_score=90.0,
            sector="金融",
            market_cap=1000.5,
            turnover_rate=5.5,
            volume_ratio=2.0
        )
        assert stock.score == 85.5
        assert stock.height_score == 100.0
        assert stock.sector == "金融"
        assert stock.market_cap == 1000.5
    
    def test_invalid_code(self):
        """测试无效股票代码"""
        with pytest.raises(ValidationError):
            LeadingStock(code="", name="测试", limit_up_days=1)
        with pytest.raises(ValidationError):
            LeadingStock(code=None, name="测试", limit_up_days=1)
    
    def test_invalid_name(self):
        """测试无效股票名称"""
        with pytest.raises(ValidationError):
            LeadingStock(code="000001", name="", limit_up_days=1)
    
    def test_invalid_limit_up_days(self):
        """测试无效连板天数"""
        with pytest.raises(ValidationError):
            LeadingStock(code="000001", name="测试", limit_up_days=-1)
    
    def test_to_dict(self):
        """测试转换为字典"""
        stock = LeadingStock(
            code="000001",
            name="测试股票",
            limit_up_days=3,
            score=75.123456,
            height_score=60.987654
        )
        result = stock.to_dict()
        
        assert result['code'] == "000001"
        assert result['name'] == "测试股票"
        assert result['limit_up_days'] == 3
        assert result['score'] == 75.12
        assert result['height_score'] == 60.99
    
    def test_to_dict_with_details(self):
        """测试转换为字典（含详情）"""
        stock = LeadingStock(
            code="000001",
            name="测试",
            limit_up_days=1,
            sector="科技",
            market_cap=500.0
        )
        result = stock.to_dict(include_details=True)
        assert result['sector'] == "科技"
        assert result['market_cap'] == 500.0
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "code": "000001",
            "name": "测试股票",
            "limit_up_days": 5,
            "sector": "金融"
        }
        stock = LeadingStock.from_dict(data)
        assert stock.code == "000001"
        assert stock.limit_up_days == 5
        assert stock.sector == "金融"


# =============================================================================
# MarketData 数据类测试
# =============================================================================

class TestMarketData:
    """测试 MarketData 数据类"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        data = MarketData(limit_up_count=10, limit_down_count=5)
        assert data.limit_up_count == 10
        assert data.limit_down_count == 5
        assert data.total_stocks == 5000
        assert data.leading_stocks == []
        assert data.date != ""  # 应自动填充当前日期
    
    def test_full_initialization(self):
        """测试完整初始化"""
        data = MarketData(
            date="2026-03-14",
            limit_up_count=50,
            limit_down_count=10,
            total_stocks=5000,
            leading_stocks=[{"code": "000001", "name": "测试"}],
            sector_data={"科技": {"count": 10}}
        )
        assert data.date == "2026-03-14"
        assert len(data.leading_stocks) == 1
    
    def test_invalid_limit_up_count(self):
        """测试无效涨停数"""
        with pytest.raises(ValidationError):
            MarketData(limit_up_count=-5, limit_down_count=10)
    
    def test_invalid_limit_down_count(self):
        """测试无效跌停数"""
        with pytest.raises(ValidationError):
            MarketData(limit_up_count=10, limit_down_count=-5)
    
    def test_zero_total_stocks(self):
        """测试零总股票数"""
        with pytest.raises(ValidationError):
            MarketData(limit_up_count=10, limit_down_count=5, total_stocks=0)
    
    def test_negative_total_stocks(self):
        """测试负数总股票数"""
        with pytest.raises(ValidationError):
            MarketData(limit_up_count=10, limit_down_count=5, total_stocks=-100)
    
    def test_to_dict(self):
        """测试转换为字典"""
        data = MarketData(
            date="2026-03-14",
            limit_up_count=50,
            limit_down_count=10
        )
        result = data.to_dict()
        assert result['date'] == "2026-03-14"
        assert result['limit_up_count'] == 50


# =============================================================================
# 异常类测试
# =============================================================================

class TestExceptions:
    """测试自定义异常"""
    
    def test_dragon_judge_error(self):
        """测试基础异常"""
        err = DragonJudgeError("测试错误")
        assert err.message == "测试错误"
        assert err.code == "DRAGON_JUDGE_ERROR"
        assert "测试错误" in str(err)
    
    def test_invalid_data_error(self):
        """测试数据异常"""
        err = InvalidDataError("无效数据")
        assert err.code == "INVALID_DATA"
    
    def test_validation_error(self):
        """测试验证异常"""
        err = ValidationError("验证失败")
        assert err.code == "VALIDATION_ERROR"
    
    def test_configuration_error(self):
        """测试配置异常"""
        err = ConfigurationError("配置错误")
        assert err.code == "CONFIG_ERROR"


# =============================================================================
# DragonJudge 初始化测试
# =============================================================================

class TestDragonJudgeInitialization:
    """测试 DragonJudge 初始化"""
    
    def test_default_initialization(self, default_judge):
        """测试默认初始化"""
        assert default_judge is not None
        assert default_judge.config == {}
        assert default_judge.weights == DragonJudge.DEFAULT_WEIGHTS
        assert default_judge.thresholds == DragonJudge.DEFAULT_THRESHOLDS
    
    def test_custom_config_initialization(self, custom_config):
        """测试自定义配置初始化"""
        judge = DragonJudge(custom_config)
        assert judge.weights == custom_config['weights']
        assert judge.thresholds == custom_config['thresholds']
    
    def test_partial_config_initialization(self):
        """测试部分配置初始化"""
        config = {'weights': {'height': 0.5, 'competition': 0.3, 'sector': 0.2, 'sentiment': 0.0, 'quality': 0.0}}
        judge = DragonJudge(config)
        assert judge.weights == config['weights']
        assert judge.thresholds == DragonJudge.DEFAULT_THRESHOLDS
    
    def test_invalid_weights_warning(self, caplog):
        """测试权重总和不等于1时的警告"""
        config = {'weights': {'height': 0.5, 'competition': 0.5, 'sector': 0.5, 'sentiment': 0.0, 'quality': 0.0}}
        with caplog.at_level("WARNING"):
            judge = DragonJudge(config)
        assert "权重总和为" in caplog.text
    
    def test_missing_weight_config(self):
        """测试缺少权重配置"""
        config = {'weights': {'height': 0.5}}  # 缺少其他权重
        with pytest.raises(ConfigurationError, match="缺少权重配置"):
            DragonJudge(config)
    
    def test_invalid_weight_type(self):
        """测试无效权重类型"""
        config = {'weights': {'height': 'invalid', 'competition': 0.3, 'sector': 0.2, 'sentiment': 0.0, 'quality': 0.0}}
        with pytest.raises(ConfigurationError, match="必须是数字"):
            DragonJudge(config)
    
    def test_weight_out_of_range(self):
        """测试权重超出范围"""
        config = {'weights': {'height': 1.5, 'competition': 0.3, 'sector': 0.2, 'sentiment': 0.0, 'quality': 0.0}}
        with pytest.raises(ConfigurationError, match="必须在 0-1 之间"):
            DragonJudge(config)


# =============================================================================
# DragonJudge 数据验证测试
# =============================================================================

class TestDragonJudgeValidation:
    """测试 DragonJudge 数据验证"""
    
    def test_valid_dict_data(self, default_judge, sample_market_data):
        """测试有效字典数据"""
        result = default_judge.validate_market_data(sample_market_data)
        assert isinstance(result, MarketData)
        assert result.limit_up_count == 45
    
    def test_valid_marketdata_object(self, default_judge, sample_market_data_obj):
        """测试有效 MarketData 对象"""
        result = default_judge.validate_market_data(sample_market_data_obj)
        assert isinstance(result, MarketData)
        assert result is sample_market_data_obj  # 应返回原对象
    
    def test_missing_limit_up_count(self, default_judge):
        """测试缺少 limit_up_count"""
        data = {"limit_down_count": 10}
        with pytest.raises(InvalidDataError, match="缺少必要字段: limit_up_count"):
            default_judge.validate_market_data(data)
    
    def test_missing_limit_down_count(self, default_judge):
        """测试缺少 limit_down_count"""
        data = {"limit_up_count": 10}
        with pytest.raises(InvalidDataError, match="缺少必要字段: limit_down_count"):
            default_judge.validate_market_data(data)
    
    def test_negative_limit_up_count(self, default_judge):
        """测试负数涨停数"""
        data = {"limit_up_count": -5, "limit_down_count": 10}
        with pytest.raises(InvalidDataError, match="不能为负数"):
            default_judge.validate_market_data(data)
    
    def test_string_limit_up_count(self, default_judge):
        """测试字符串类型的涨停数"""
        data = {"limit_up_count": "100", "limit_down_count": 10}
        with pytest.raises(InvalidDataError, match="必须是数字类型"):
            default_judge.validate_market_data(data)


# =============================================================================
# DragonJudge 情绪计算测试
# =============================================================================

class TestDragonJudgeSentimentCalculation:
    """测试 DragonJudge 情绪计算"""
    
    def test_normal_sentiment(self, default_judge, sample_market_data):
        """测试正常情绪计算"""
        score = default_judge.calculate_sentiment(sample_market_data)
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_empty_market_sentiment(self, default_judge, empty_market_data):
        """测试空市场情绪"""
        score = default_judge.calculate_sentiment(empty_market_data)
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_sentiment_range_limit_low(self, default_judge):
        """测试情绪分数下限"""
        data = {
            "limit_up_count": 0,
            "limit_down_count": 1000,
            "total_stocks": 1000,
            "leading_stocks": []
        }
        score = default_judge.calculate_sentiment(data)
        assert score == 0.0
    
    def test_sentiment_range_limit_high(self, default_judge):
        """测试情绪分数上限"""
        data = {
            "limit_up_count": 1000,
            "limit_down_count": 0,
            "total_stocks": 1000,
            "leading_stocks": [
                {"code": "000001", "name": "股票1", "limit_up_days": 10},
            ]
        }
        score = default_judge.calculate_sentiment(data)
        assert score == 100.0


# =============================================================================
# DragonJudge 市场周期检测测试
# =============================================================================

class TestDragonJudgeCycleDetection:
    """测试 DragonJudge 市场周期检测"""
    
    def test_detect_ice_point(self, default_judge):
        """测试检测冰点"""
        data = {"limit_up_count": 10, "limit_down_count": 200, "total_stocks": 5000, "leading_stocks": []}
        cycle = default_judge.detect_cycle(data)
        assert cycle == MarketCycle.ICE_POINT
    
    def test_detect_start(self, default_judge):
        """测试检测启动期"""
        data = {"limit_up_count": 30, "limit_down_count": 50, "total_stocks": 5000, "leading_stocks": []}
        cycle = default_judge.detect_cycle(data)
        assert cycle == MarketCycle.START
    
    def test_detect_fermentation(self, default_judge):
        """测试检测发酵期"""
        data = {"limit_up_count": 60, "limit_down_count": 20, "total_stocks": 5000, "leading_stocks": []}
        cycle = default_judge.detect_cycle(data)
        assert cycle == MarketCycle.FERMENTATION
    
    def test_detect_climax(self, default_judge):
        """测试检测高潮期"""
        data = {"limit_up_count": 150, "limit_down_count": 5, "total_stocks": 5000, "leading_stocks": []}
        cycle = default_judge.detect_cycle(data)
        assert cycle == MarketCycle.CLIMAX
    
    def test_detect_divergence(self, default_judge):
        """测试检测分化期（情绪>=85）"""
        data = {"limit_up_count": 500, "limit_down_count": 0, "total_stocks": 5000, "leading_stocks": [
            {"code": "000001", "name": "股票1", "limit_up_days": 10},
            {"code": "000002", "name": "股票2", "limit_up_days": 8},
        ]}
        cycle = default_judge.detect_cycle(data)
        assert cycle == MarketCycle.DIVERGENCE


# =============================================================================
# DragonJudge 龙头选股测试
# =============================================================================

class TestDragonJudgeLeaderSelection:
    """测试 DragonJudge 龙头选股"""
    
    def test_select_leaders_normal(self, default_judge, sample_market_data):
        """测试正常选股"""
        leaders = default_judge.select_leaders(sample_market_data)
        assert isinstance(leaders, list)
        assert len(leaders) > 0
        assert all(isinstance(l, LeadingStock) for l in leaders)
    
    def test_select_leaders_empty(self, default_judge, empty_market_data):
        """测试空数据选股"""
        leaders = default_judge.select_leaders(empty_market_data)
        assert leaders == []
    
    def test_select_leaders_sorted(self, default_judge, sample_market_data):
        """测试选股结果排序"""
        leaders = default_judge.select_leaders(sample_market_data)
        if len(leaders) > 1:
            scores = [l.score for l in leaders]
            assert scores == sorted(scores, reverse=True)
    
    def test_select_leaders_with_top_n(self, default_judge, sample_market_data):
        """测试限制返回数量"""
        leaders = default_judge.select_leaders(sample_market_data, top_n=2)
        assert len(leaders) <= 2
    
    def test_select_leaders_invalid_stock_data(self, default_judge, caplog):
        """测试无效股票数据处理"""
        data = {
            "limit_up_count": 10,
            "limit_down_count": 5,
            "total_stocks": 5000,
            "leading_stocks": [
                "invalid_data",
                {"code": "", "name": "", "limit_up_days": 1},
                {"code": "000001", "name": "有效股票", "limit_up_days": 2},
            ]
        }
        with caplog.at_level("WARNING"):
            leaders = default_judge.select_leaders(data)
        
        assert len(leaders) >= 1
        assert any("无效的股票数据格式" in msg for msg in caplog.messages)


# =============================================================================
# DragonJudge 报告生成测试
# =============================================================================

class TestDragonJudgeReportGeneration:
    """测试 DragonJudge 报告生成"""
    
    def test_generate_report_normal(self, default_judge, sample_market_data):
        """测试正常报告生成"""
        report = default_judge.generate_report(sample_market_data)
        
        assert 'date' in report
        assert 'sentiment_score' in report
        assert 'market_cycle' in report
        assert 'market_cycle_en' in report
        assert 'market_cycle_display' in report
        assert 'leading_stocks' in report
        assert 'strategy' in report
        assert 'market_summary' in report
        assert 'risk_level' in report
        assert 'generated_at' in report
    
    def test_report_with_details(self, default_judge, sample_market_data):
        """测试生成详细报告"""
        report = default_judge.generate_report(sample_market_data, include_details=True)
        assert 'leading_stocks' in report
    
    def test_report_cycle_names(self, default_judge, sample_market_data):
        """测试报告中周期名称"""
        report = default_judge.generate_report(sample_market_data)
        assert report['market_cycle'] in [c.cn_name for c in MarketCycle]
        assert report['market_cycle_en'] in [c.en_name for c in MarketCycle]


# =============================================================================
# DragonJudge 策略生成测试
# =============================================================================

class TestDragonJudgeStrategy:
    """测试 DragonJudge 策略生成"""
    
    def test_strategy_ice_point(self, default_judge):
        """测试冰点策略"""
        strategy = default_judge._generate_strategy(15, MarketCycle.ICE_POINT)
        assert "空仓观望" in strategy
    
    def test_strategy_start(self, default_judge):
        """测试启动期策略"""
        strategy = default_judge._generate_strategy(30, MarketCycle.START)
        assert "轻仓试错" in strategy
    
    def test_strategy_fermentation(self, default_judge):
        """测试发酵期策略"""
        strategy = default_judge._generate_strategy(45, MarketCycle.FERMENTATION)
        assert "半仓参与" in strategy
    
    def test_strategy_climax(self, default_judge):
        """测试高潮期策略"""
        strategy = default_judge._generate_strategy(75, MarketCycle.CLIMAX)
        assert "高潮减仓" in strategy
    
    def test_strategy_divergence(self, default_judge):
        """测试分化期策略"""
        strategy = default_judge._generate_strategy(90, MarketCycle.DIVERGENCE)
        assert "全面撤退" in strategy
    
    def test_strategy_extreme_high_sentiment(self, default_judge):
        """测试极端高情绪策略"""
        strategy = default_judge._generate_strategy(95, MarketCycle.CLIMAX)
        assert "情绪过热" in strategy
        assert "⚠️" in strategy
    
    def test_strategy_extreme_low_sentiment(self, default_judge):
        """测试极端低情绪策略"""
        strategy = default_judge._generate_strategy(5, MarketCycle.ICE_POINT)
        assert "极度冰点" in strategy
        assert "💡" in strategy


# =============================================================================
# DragonJudge 风险等级测试
# =============================================================================

class TestDragonJudgeRiskLevel:
    """测试 DragonJudge 风险等级"""
    
    def test_risk_level_ice_point(self, default_judge):
        """测试冰点风险等级"""
        risk = default_judge._calculate_risk_level(15, MarketCycle.ICE_POINT)
        assert risk['level'] == "低风险"
        assert risk['score'] == 1
    
    def test_risk_level_climax(self, default_judge):
        """测试高潮风险等级"""
        risk = default_judge._calculate_risk_level(75, MarketCycle.CLIMAX)
        assert risk['level'] == "高风险"
        assert risk['score'] == 4
    
    def test_risk_level_extreme(self, default_judge):
        """测试极端情绪风险警告"""
        risk = default_judge._calculate_risk_level(96, MarketCycle.CLIMAX)
        assert 'warning' in risk


# =============================================================================
# DragonJudge 周期转换概率测试
# =============================================================================

class TestDragonJudgeCycleTransition:
    """测试 DragonJudge 周期转换概率"""
    
    def test_transition_from_ice_point_up(self, default_judge):
        """测试冰点向上转换"""
        probs = default_judge.get_cycle_transition_probability(MarketCycle.ICE_POINT, "up")
        assert MarketCycle.START in probs
        assert sum(probs.values()) == 1.0
    
    def test_transition_from_climax_down(self, default_judge):
        """测试高潮向下转换"""
        probs = default_judge.get_cycle_transition_probability(MarketCycle.CLIMAX, "down")
        assert MarketCycle.DIVERGENCE in probs
        assert sum(probs.values()) == 1.0


# =============================================================================
# 边界条件测试
# =============================================================================

class TestDragonJudgeBoundaryConditions:
    """测试 DragonJudge 边界条件"""
    
    def test_zero_limit_up_and_down(self, default_judge):
        """测试零涨停跌停"""
        data = {
            "limit_up_count": 0,
            "limit_down_count": 0,
            "total_stocks": 5000,
            "leading_stocks": []
        }
        score = default_judge.calculate_sentiment(data)
        assert score == 50.0
    
    def test_all_limit_up(self, default_judge):
        """测试全部涨停"""
        data = {
            "limit_up_count": 5000,
            "limit_down_count": 0,
            "total_stocks": 5000,
            "leading_stocks": []
        }
        score = default_judge.calculate_sentiment(data)
        assert score == 100.0
    
    def test_all_limit_down(self, default_judge):
        """测试全部跌停"""
        data = {
            "limit_up_count": 0,
            "limit_down_count": 5000,
            "total_stocks": 5000,
            "leading_stocks": []
        }
        score = default_judge.calculate_sentiment(data)
        assert score == 0.0
    
    def test_single_stock_market(self, default_judge):
        """测试单股票市场"""
        data = {
            "limit_up_count": 1,
            "limit_down_count": 0,
            "total_stocks": 1,
            "leading_stocks": [{"code": "000001", "name": "唯一股票", "limit_up_days": 1}]
        }
        score = default_judge.calculate_sentiment(data)
        assert score > 50
    
    def test_very_large_total_stocks(self, default_judge):
        """测试超大市场"""
        data = {
            "limit_up_count": 100,
            "limit_down_count": 50,
            "total_stocks": 100000,
            "leading_stocks": []
        }
        score = default_judge.calculate_sentiment(data)
        assert 0 <= score <= 100


# =============================================================================
# 异常处理测试
# =============================================================================

class TestDragonJudgeExceptions:
    """测试 DragonJudge 异常处理"""
    
    def test_invalid_data_type(self, default_judge):
        """测试无效数据类型"""
        with pytest.raises(InvalidDataError):
            default_judge.validate_market_data("invalid")
    
    def test_calculate_sentiment_with_invalid_data(self, default_judge):
        """测试使用无效数据计算情绪"""
        with pytest.raises(InvalidDataError):
            default_judge.calculate_sentiment({"limit_up_count": -10, "limit_down_count": 5})
    
    def test_detect_cycle_with_invalid_data(self, default_judge):
        """测试使用无效数据检测周期"""
        with pytest.raises(InvalidDataError):
            default_judge.detect_cycle({})
    
    def test_select_leaders_with_invalid_data(self, default_judge):
        """测试使用无效数据选股"""
        with pytest.raises(InvalidDataError):
            default_judge.select_leaders({})
    
    def test_generate_report_with_invalid_data(self, default_judge):
        """测试使用无效数据生成报告"""
        with pytest.raises(InvalidDataError):
            default_judge.generate_report({})


# =============================================================================
# 性能测试
# =============================================================================

class TestDragonJudgePerformance:
    """测试 DragonJudge 性能"""
    
    def test_large_dataset_performance(self, default_judge):
        """测试大数据集处理性能"""
        large_data = {
            "date": "2026-03-14",
            "limit_up_count": 500,
            "limit_down_count": 50,
            "total_stocks": 5000,
            "leading_stocks": [
                {"code": f"{i:06d}", "name": f"股票{i}", "limit_up_days": (i % 10) + 1}
                for i in range(1, 1001)
            ]
        }
        
        start_time = time.time()
        leaders = default_judge.select_leaders(large_data)
        elapsed = time.time() - start_time
        
        assert len(leaders) == 1000
        assert elapsed < 2.0
    
    def test_repeated_calculation_consistency(self, default_judge, sample_market_data):
        """测试重复计算一致性"""
        scores = [
            default_judge.calculate_sentiment(sample_market_data)
            for _ in range(100)
        ]
        assert all(s == scores[0] for s in scores)


# =============================================================================
# 集成测试
# =============================================================================

class TestDragonJudgeIntegration:
    """测试 DragonJudge 集成场景"""
    
    def test_full_workflow(self, default_judge, sample_market_data):
        """测试完整工作流程"""
        data = default_judge.validate_market_data(sample_market_data)
        sentiment = default_judge.calculate_sentiment(data)
        cycle = default_judge.detect_cycle(data)
        leaders = default_judge.select_leaders(data)
        report = default_judge.generate_report(data.to_dict())
        
        assert report['sentiment_score'] == round(sentiment, 2)
        assert report['market_cycle'] == cycle.cn_name
        assert len(report['leading_stocks']) == len(leaders)
    
    def test_workflow_with_empty_leaders(self, default_judge):
        """测试无龙头的工作流程"""
        data = MarketData(
            date="2026-03-14",
            limit_up_count=10,
            limit_down_count=5,
            total_stocks=5000,
            leading_stocks=[]
        )
        
        sentiment = default_judge.calculate_sentiment(data)
        cycle = default_judge.detect_cycle(data)
        leaders = default_judge.select_leaders(data)
        report = default_judge.generate_report(data)
        
        assert sentiment is not None
        assert isinstance(cycle, MarketCycle)
        assert leaders == []
        assert report['leading_stocks'] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
