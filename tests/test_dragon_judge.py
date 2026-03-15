"""
Dragon Judge 核心测试
测试 Dragon Judge 情绪评分系统的各项功能
"""
import pytest
from src.scoring.dragon_judge import (
    DragonJudge,
    MarketCycle,
    LeadingStock,
    MarketData,
    InvalidDataError,
    ValidationError,
    ConfigurationError,
)


class TestMarketCycle:
    """测试 MarketCycle 枚举"""
    
    def test_cycle_names(self):
        """测试周期名称"""
        assert MarketCycle.ICE_POINT.cn_name == "冰点"
        assert MarketCycle.CLIMAX.cn_name == "高潮"
        assert MarketCycle.ICE_POINT.en_name == "ice_point"
    
    def test_cycle_from_value(self):
        """测试从值获取周期"""
        assert MarketCycle.from_value("冰点") == MarketCycle.ICE_POINT
        assert MarketCycle.from_value("climax") == MarketCycle.CLIMAX
        assert MarketCycle.from_value(MarketCycle.START) == MarketCycle.START
    
    def test_cycle_from_value_invalid(self):
        """测试无效周期值"""
        from src.scoring.dragon_judge import InvalidCycleError
        with pytest.raises(InvalidCycleError):
            MarketCycle.from_value("invalid")
    
    def test_display_name(self):
        """测试显示名称"""
        assert "冰点" in MarketCycle.ICE_POINT.display_name


class TestLeadingStock:
    """测试 LeadingStock 数据类"""
    
    def test_create_valid(self):
        """测试创建有效对象"""
        stock = LeadingStock(code="000001", name="平安银行", limit_up_days=3)
        assert stock.code == "000001"
        assert stock.name == "平安银行"
        assert stock.limit_up_days == 3
    
    def test_create_invalid_code(self):
        """测试无效代码"""
        with pytest.raises(ValidationError):
            LeadingStock(code="", name="测试", limit_up_days=1)
    
    def test_create_invalid_days(self):
        """测试无效连板天数"""
        with pytest.raises(ValidationError):
            LeadingStock(code="000001", name="测试", limit_up_days=-1)
    
    def test_to_dict(self):
        """测试转换为字典"""
        stock = LeadingStock(code="000001", name="平安银行", limit_up_days=3, score=85.5)
        data = stock.to_dict()
        assert data["code"] == "000001"
        assert data["score"] == 85.5
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {"code": "000001", "name": "平安银行", "limit_up_days": 3}
        stock = LeadingStock.from_dict(data)
        assert stock.code == "000001"
        assert stock.limit_up_days == 3


class TestMarketData:
    """测试 MarketData 数据类"""
    
    def test_create_valid(self):
        """测试创建有效对象"""
        data = MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            total_stocks=5000
        )
        assert data.limit_up_count == 50
        assert data.limit_down_count == 5
    
    def test_invalid_limit_up(self):
        """测试无效涨停数"""
        with pytest.raises(ValidationError):
            MarketData(date="2024-01-01", limit_up_count=-1, limit_down_count=5)
    
    def test_invalid_total_stocks(self):
        """测试无效总股票数"""
        with pytest.raises(ValidationError):
            MarketData(date="2024-01-01", limit_up_count=50, limit_down_count=5, total_stocks=0)
    
    def test_default_date(self):
        """测试默认日期"""
        data = MarketData(limit_up_count=50, limit_down_count=5)
        assert data.date is not None


class TestDragonJudgeInitialization:
    """测试 DragonJudge 初始化"""
    
    def test_default_initialization(self):
        """测试默认初始化"""
        dj = DragonJudge()
        assert dj is not None
        assert hasattr(dj, 'calculate_sentiment')
        assert hasattr(dj, 'detect_cycle')
        assert hasattr(dj, 'select_leaders')
    
    def test_custom_weights(self):
        """测试自定义权重"""
        config = {
            'weights': {
                'height': 0.50,
                'competition': 0.25,
                'sector': 0.15,
                'sentiment': 0.05,
                'quality': 0.05,
            }
        }
        dj = DragonJudge(config=config)
        assert dj.weights['height'] == 0.50
    
    def test_invalid_weights_sum(self):
        """测试无效权重总和（警告但不报错）"""
        config = {'weights': {'height': 0.5, 'competition': 0.5, 'sector': 0.5, 'sentiment': 0, 'quality': 0}}
        dj = DragonJudge(config=config)
        # 应该正常工作，但会记录警告
    
    def test_missing_weight_key(self):
        """测试缺少权重键"""
        config = {'weights': {'height': 0.5}}
        with pytest.raises(ConfigurationError):
            DragonJudge(config=config)
    
    def test_invalid_threshold_order(self):
        """测试无效阈值顺序"""
        config = {'thresholds': {'ice_point': 50, 'start': 30}}
        with pytest.raises(ConfigurationError):
            DragonJudge(config=config)


class TestDragonJudgeSentiment:
    """测试情绪分数计算"""
    
    @pytest.fixture
    def sample_data(self):
        """样本数据"""
        return MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            total_stocks=5000,
            leading_stocks=[
                {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
                {'code': '000002', 'name': '万科A', 'limit_up_days': 2},
            ]
        )
    
    def test_sentiment_calculation(self, sample_data):
        """测试情绪分数计算"""
        dj = DragonJudge()
        score = dj.calculate_sentiment(sample_data)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
    
    def test_sentiment_range(self, sample_data):
        """测试情绪分数范围"""
        dj = DragonJudge()
        score = dj.calculate_sentiment(sample_data)
        assert 0 <= score <= 100
    
    def test_sentiment_with_high_boards(self, sample_data):
        """测试有连板时的情绪分数"""
        dj = DragonJudge()
        score = dj.calculate_sentiment(sample_data)
        # 有连板应该加分
        assert score > 50


class TestDragonJudgeCycle:
    """测试市场周期判断"""
    
    @pytest.fixture
    def base_data(self):
        return {
            'date': '2024-01-01',
            'limit_up_count': 50,
            'limit_down_count': 5,
            'total_stocks': 5000,
            'leading_stocks': []
        }
    
    def test_detect_ice_point(self, base_data):
        """测试冰点检测"""
        dj = DragonJudge()
        base_data['limit_up_count'] = 10
        base_data['limit_down_count'] = 50
        cycle = dj.detect_cycle(base_data)
        assert cycle == MarketCycle.ICE_POINT
    
    def test_detect_climax(self, base_data):
        """测试高潮检测"""
        dj = DragonJudge()
        base_data['limit_up_count'] = 200
        base_data['limit_down_count'] = 0
        cycle = dj.detect_cycle(base_data)
        assert cycle == MarketCycle.CLIMAX


class TestDragonJudgeLeaders:
    """测试龙头选股"""
    
    @pytest.fixture
    def sample_market_data(self):
        """样本市场数据"""
        return MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            total_stocks=5000,
            leading_stocks=[
                {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
                {'code': '000002', 'name': '万科A', 'limit_up_days': 2},
                {'code': '600519', 'name': '贵州茅台', 'limit_up_days': 1},
            ]
        )
    
    def test_select_leaders(self, sample_market_data):
        """测试龙头选股"""
        dj = DragonJudge()
        leaders = dj.select_leaders(sample_market_data)
        
        assert isinstance(leaders, list)
        assert len(leaders) > 0
        if leaders:
            assert isinstance(leaders[0], LeadingStock)
            assert hasattr(leaders[0], 'code')
            assert hasattr(leaders[0], 'score')
    
    def test_leaders_sorted_by_score(self, sample_market_data):
        """测试龙头股按分数排序"""
        dj = DragonJudge()
        leaders = dj.select_leaders(sample_market_data)
        
        if len(leaders) > 1:
            assert leaders[0].score >= leaders[1].score
    
    def test_select_leaders_top_n(self, sample_market_data):
        """测试限制返回数量"""
        dj = DragonJudge()
        leaders = dj.select_leaders(sample_market_data, top_n=2)
        assert len(leaders) <= 2
    
    def test_empty_leading_stocks(self):
        """测试空龙头股列表"""
        dj = DragonJudge()
        data = MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            leading_stocks=[]
        )
        leaders = dj.select_leaders(data)
        assert leaders == []


class TestDragonJudgeReport:
    """测试报告生成"""
    
    @pytest.fixture
    def sample_data(self):
        return MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            total_stocks=5000,
            leading_stocks=[
                {'code': '000001', 'name': '平安银行', 'limit_up_days': 3},
            ]
        )
    
    def test_generate_report(self, sample_data):
        """测试生成报告"""
        dj = DragonJudge()
        report = dj.generate_report(sample_data)
        
        assert 'date' in report
        assert 'sentiment_score' in report
        assert 'market_cycle' in report
        assert 'leading_stocks' in report
        assert 'strategy' in report
    
    def test_report_structure(self, sample_data):
        """测试报告结构"""
        dj = DragonJudge()
        report = dj.generate_report(sample_data, include_details=True)
        
        assert isinstance(report['sentiment_score'], (int, float))
        assert isinstance(report['leading_stocks'], list)
        assert 'market_summary' in report


class TestDragonJudgeErrors:
    """测试错误处理"""
    
    def test_invalid_data_error(self):
        """测试无效数据错误"""
        dj = DragonJudge()
        with pytest.raises(InvalidDataError):
            dj.validate_market_data({'invalid': 'data'})
    
    def test_negative_values_error(self):
        """测试负值错误"""
        dj = DragonJudge()
        with pytest.raises(InvalidDataError):
            dj.validate_market_data({
                'date': '2024-01-01',
                'limit_up_count': -10,
                'limit_down_count': 5,
            })


class TestFiveDimensions:
    """测试五维评分系统"""
    
    def test_height_score_calculation(self):
        """测试高度分计算"""
        dj = DragonJudge()
        stock = LeadingStock(code="000001", name="测试", limit_up_days=5)
        data = MarketData(date="2024-01-01", limit_up_count=50, limit_down_count=5)
        
        dj._calculate_five_dimensions(stock, data)
        assert stock.height_score == 100.0
    
    def test_competition_score(self):
        """测试竞争分"""
        dj = DragonJudge()
        stock = LeadingStock(code="000001", name="测试", limit_up_days=3)
        data = MarketData(
            date="2024-01-01",
            limit_up_count=50,
            limit_down_count=5,
            leading_stocks=[
                {'code': '000001', 'name': '测试1', 'limit_up_days': 3},
                {'code': '000002', 'name': '测试2', 'limit_up_days': 3},
                {'code': '000003', 'name': '测试3', 'limit_up_days': 3},
            ]
        )
        
        dj._calculate_five_dimensions(stock, data)
        # 有3个同身位，竞争分应该低于100
        assert stock.competition_score < 100


class TestStrategy:
    """测试策略生成"""
    
    def test_strategy_for_each_cycle(self):
        """测试各周期的策略"""
        dj = DragonJudge()
        
        strategies = {
            MarketCycle.ICE_POINT: "空仓观望",
            MarketCycle.START: "轻仓试错",
            MarketCycle.FERMENTATION: "半仓参与",
            MarketCycle.CLIMAX: "高潮减仓",
            MarketCycle.DIVERGENCE: "全面撤退",
        }
        
        for cycle, keyword in strategies.items():
            strategy = dj._generate_strategy(50, cycle)
            assert keyword in strategy
    
    def test_extreme_sentiment_warning(self):
        """测试极端情绪警告"""
        dj = DragonJudge()
        
        high_strategy = dj._generate_strategy(95, MarketCycle.CLIMAX)
        assert "⚠️" in high_strategy or "过热" in high_strategy
        
        low_strategy = dj._generate_strategy(5, MarketCycle.ICE_POINT)
        assert "💡" in low_strategy or "冰点" in low_strategy


class TestRiskLevel:
    """测试风险等级计算"""
    
    def test_risk_levels(self):
        """测试各周期风险等级"""
        dj = DragonJudge()
        
        risk_mapping = {
            MarketCycle.ICE_POINT: "低风险",
            MarketCycle.START: "中低风险",
            MarketCycle.FERMENTATION: "中等风险",
            MarketCycle.CLIMAX: "高风险",
            MarketCycle.DIVERGENCE: "极高风险",
        }
        
        for cycle, expected_level in risk_mapping.items():
            risk = dj._calculate_risk_level(50, cycle)
            assert risk['level'] == expected_level
