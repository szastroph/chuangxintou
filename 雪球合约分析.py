import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置当前目录
current_dir = os.getcwd()
print(f"当前工作目录: {current_dir}")

# 读取Excel文件
excel_file = os.path.join(current_dir, '创新投雪球管理.xlsx')

# 读取合约状态sheet
df_contracts = pd.read_excel(excel_file, sheet_name='合约状态')
print("合约状态数据:")
print(df_contracts.head())
print(f"\n合约状态数据形状: {df_contracts.shape}")

# 读取历史行情sheet
# 第1行是列名，从第4行开始读取数据（header=1，因为pandas从0开始计数）
df_history = pd.read_excel(excel_file, sheet_name='历史行情', header=1)
print("原始历史行情数据:")
print(df_history.head())
print(f"\n原始历史行情数据形状: {df_history.shape}")

# 删除前两行（第2行和第3行是没用的）
df_history = df_history.iloc[2:].reset_index(drop=True)
print("\n删除前两行后的历史行情数据:")
print(df_history.head())
print(f"\n删除前两行后的历史行情数据形状: {df_history.shape}")

# 给第0列添加"date"列名
df_history.columns = ['date'] + list(df_history.columns[1:])
print("\n添加date列名后的历史行情数据:")
print(df_history.head())

# 给第9列添加"估值总和"列名
if len(df_history.columns) > 9:
    df_history.columns = list(df_history.columns[:9]) + ['估值总和'] + list(df_history.columns[10:])
    print("\n添加估值总和列名后的历史行情数据:")
    print(df_history.head())

# 删除最后两行
df_history = df_history.iloc[:-2]
print("\n删除最后两行后的历史行情数据:")
print(df_history.head())
print(f"\n删除最后两行后的历史行情数据形状: {df_history.shape}")

# 检查列名
print("合约状态列名:")
print(df_contracts.columns.tolist())

print("\n历史行情列名:")
print(df_history.columns.tolist())

# 提取合约信息
contract_info = df_contracts[['挂钩标的', '敲入点位', '名义本金']].copy()
print("合约信息:")
print(contract_info.head())
print(f"\n合约信息形状: {contract_info.shape}")

# 获取历史行情最后一天的收盘价
# 第一列是日期，第二到第五列是各标的收盘价，第9列是估值总和
last_day_data = df_history.iloc[-1]
date = last_day_data['date']  # 日期
last_day_prices = {}
valuation_sum = last_day_data['估值总和']  # 估值总和

# 提取各标的收盘价（第二列到第五列）
for i in range(1, 5):
    if i < len(df_history.columns):
        last_day_prices[df_history.columns[i]] = last_day_data.iloc[i]

print(f"日期: {date}")
print("最后一天的收盘价:")
print(last_day_prices)
print(f"估值总和: {valuation_sum}")

# 按标的分组
underlying_assets = contract_info['挂钩标的'].unique()
print(f"共有 {len(underlying_assets)} 个标的:")
print(underlying_assets)

# 为每个标的创建图表
for asset in underlying_assets:
    # 获取该标的的所有合约
    asset_contracts = contract_info[contract_info['挂钩标的'] == asset]

    # 获取该标的当前价格
    current_price = last_day_prices.get(asset, None)

    if current_price is None:
        print(f"警告: 找不到标的 {asset} 的当前价格")
        continue

    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))

    # 绘制当前价格线
    ax.axhline(y=current_price, color='blue', linestyle='-', linewidth=2, label=f'当前价格: {current_price:.2f}')

    # 为每个合约绘制敲入点位
    for idx, (_, contract) in enumerate(asset_contracts.iterrows()):
        knock_in = contract['敲入点位']
        nominal = contract['名义本金']

        # 计算距离敲入的百分比
        distance_to_knock_in = (current_price - knock_in) / current_price * 100

        # 为每笔合约生成不同的颜色
        # 使用颜色循环，确保每笔合约有独特的颜色
        colors = plt.cm.tab20(np.linspace(0, 1, len(asset_contracts)))
        color = colors[idx]

        # 根据距离敲入的远近设置透明度
        # 距离越近，透明度越高（越不透明）
        if distance_to_knock_in < 0:
            alpha = 1.0  # 已敲入，完全不透明
        elif distance_to_knock_in < 5:
            alpha = 0.9  # 距离敲入很近，高透明度
        elif distance_to_knock_in < 10:
            alpha = 0.7  # 距离敲入较近，中等透明度
        else:
            alpha = 0.5  # 距离敲入较远，低透明度

        # 点的大小根据名义本金调整
        size = nominal / 1000000 * 20  # 每100万对应20个点的大小

        # 绘制敲入点位
        ax.scatter(x=0, y=knock_in, s=size, color=color, alpha=alpha,
                   label=f'敲入点位: {knock_in:.2f}, 距离: {distance_to_knock_in:.2f}%, 名义本金: {nominal/10000:.1f}万')

    # 设置图表标题和标签
    ax.set_title(f'{asset} - 合约敲入点位分析', fontsize=16)
    ax.set_ylabel('价格', fontsize=12)

    # 隐藏x轴
    ax.set_xticks([])

    # 添加图例
    ax.legend(loc='best')

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)

    # 显示图表
    plt.tight_layout()
    plt.show()

# 汇总分析结果
summary_data = []
for asset in underlying_assets:
    asset_contracts = contract_info[contract_info['挂钩标的'] == asset]
    current_price = last_day_prices.get(asset, None)

    if current_price is None:
        continue

    for _, contract in asset_contracts.iterrows():
        knock_in = contract['敲入点位']
        nominal = contract['名义本金']
        distance_to_knock_in = (current_price - knock_in) / current_price * 100

        summary_data.append({
            '标的': asset,
            '当前价格': current_price,
            '敲入点位': knock_in,
            '距离敲入(%)': distance_to_knock_in,
            '名义本金(万)': nominal/10000
        })

summary_df = pd.DataFrame(summary_data)
print("合约敲入点位分析汇总:")
print(summary_df)
