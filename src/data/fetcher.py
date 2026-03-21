#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股全市场行情数据采集脚本
支持：日线/周线/月线行情数据
数据源：AKShare (东方财富)
作者：数据采集 Agent
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse


class AShareDataCollector:
    """A股数据采集器"""
    
    def __init__(self, output_dir="./a股数据"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def get_stock_list(self):
        """获取A股所有股票列表"""
        print("📊 正在获取A股股票列表...")
        try:
            df = ak.stock_info_a_code_name()
            df['code'] = df['code'].astype(str).str.zfill(6)
            print(f"✅ 获取到 {len(df)} 只股票")
            return df
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None
    
    def get_stock_history(self, code, name, start_date, end_date, period="daily"):
        """获取单只股票历史行情"""
        try:
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period=period,
                start_date=start_date, 
                end_date=end_date
            )
            if not df.empty:
                df['股票名称'] = name
                df['股票代码'] = code
            return df
        except Exception as e:
            return None
    
    def collect_all(self, days=30, batch_size=100, delay=0.2, max_workers=1):
        """
        采集全市场数据
        
        参数:
            days: 采集最近多少天的数据
            batch_size: 每批次采集数量 (测试用)
            delay: 请求间隔(秒)，避免被封
            max_workers: 并发数 (建议=1，避免被封)
        """
        # 获取股票列表
        stock_list = self.get_stock_list()
        if stock_list is None:
            return
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days+5)  # 多取几天确保覆盖交易日
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        print(f"\n📅 采集区间: {start_str} 至 {end_str}")
        print(f"⏱️  预计耗时: 约 {len(stock_list) * delay / 60:.1f} 分钟")
        print("-" * 60)
        
        all_data = []
        failed_stocks = []
        success_count = 0
        
        # 用于测试，可限制数量
        if batch_size > 0:
            stock_list = stock_list.head(batch_size)
            print(f"🧪 测试模式: 仅采集前 {batch_size} 只股票")
        
        total = len(stock_list)
        
        for i, row in stock_list.iterrows():
            code = row['code']
            name = row['name']
            
            df = self.get_stock_history(code, name, start_str, end_str)
            
            if df is not None and not df.empty:
                all_data.append(df)
                success_count += 1
                
                if success_count % 50 == 0:
                    progress = (i + 1) / total * 100
                    print(f"✅ {success_count}/{total} ({progress:.1f}%) - {code} {name}")
            else:
                failed_stocks.append((code, name))
            
            time.sleep(delay)
        
        print("-" * 60)
        
        # 合并并保存数据
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 调整列顺序
            col_order = ['日期', '股票代码', '股票名称', '开盘', '收盘', '最高', '最低', 
                        '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            combined_df = combined_df[[c for c in col_order if c in combined_df.columns]]
            
            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f'{self.output_dir}/a股日线行情_{success_count}只_{start_str}_{end_str}.csv'
            combined_df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            # 统计信息
            self._print_statistics(combined_df, success_count, failed_stocks, filename)
            
            return combined_df
        else:
            print("❌ 未能获取任何数据")
            return None
    
    def _print_statistics(self, df, success_count, failed_stocks, filename):
        """打印统计信息"""
        print(f"\n💾 数据已保存: {filename}")
        print(f"\n📊 采集统计:")
        print(f"   ✅ 成功: {success_count} 只股票")
        print(f"   ❌ 失败: {len(failed_stocks)} 只")
        print(f"   📈 总记录: {len(df)} 条")
        print(f"   📅 交易日期: {df['日期'].nunique()} 天")
        print(f"   📊 日期范围: {df['日期'].min()} 至 {df['日期'].max()}")
        
        # 最新交易日统计
        latest_date = df['日期'].max()
        latest = df[df['日期'] == latest_date]
        
        print(f"\n📈 最新交易日 ({latest_date}) 统计:")
        up = len(latest[latest['涨跌幅'] > 0])
        down = len(latest[latest['涨跌幅'] < 0])
        flat = len(latest[latest['涨跌幅'] == 0])
        
        print(f"   上涨: {up} 只")
        print(f"   下跌: {down} 只")
        print(f"   平盘: {flat} 只")
        
        if up > 0:
            print(f"   平均涨幅: {latest[latest['涨跌幅'] > 0]['涨跌幅'].mean():.2f}%")
        if down > 0:
            print(f"   平均跌幅: {latest[latest['涨跌幅'] < 0]['涨跌幅'].mean():.2f}%")
        
        # 涨跌幅排行
        print(f"\n🚀 涨幅前10:")
        top10 = latest.nlargest(10, '涨跌幅')[['股票代码', '股票名称', '收盘', '涨跌幅']]
        print(top10.to_string(index=False))
        
        print(f"\n📉 跌幅前10:")
        bottom10 = latest.nsmallest(10, '涨跌幅')[['股票代码', '股票名称', '收盘', '涨跌幅']]
        print(bottom10.to_string(index=False))
        
        # 成交额排行
        print(f"\n💰 成交额前10:")
        vol10 = latest.nlargest(10, '成交额')[['股票代码', '股票名称', '成交额', '涨跌幅']]
        print(vol10.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description='A股行情数据采集工具')
    parser.add_argument('-d', '--days', type=int, default=30, help='采集最近N天数据 (默认30)')
    parser.add_argument('-b', '--batch', type=int, default=0, help='测试模式:仅采集前N只 (默认0=全部)')
    parser.add_argument('--delay', type=float, default=0.2, help='请求间隔秒数 (默认0.2)')
    parser.add_argument('-o', '--output', type=str, default='./a股数据', help='输出目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 A股全市场行情数据采集")
    print("=" * 60)
    
    collector = AShareDataCollector(output_dir=args.output)
    collector.collect_all(
        days=args.days,
        batch_size=args.batch,
        delay=args.delay
    )
    
    print("\n" + "=" * 60)
    print("✅ 采集完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
