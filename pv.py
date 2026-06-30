import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import warnings
from matplotlib.gridspec import GridSpec

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置当前目录
current_dir = os.getcwd()
folder_path = current_dir

print(f"当前工作目录: {current_dir}")

# 读取Excel文件
excel_file = os.path.join(current_dir, '创新投雪球管理.xlsx')

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

# 确保日期列是datetime类型
df_history['date'] = pd.to_datetime(df_history['date'])

# 计算每天的涨跌
# df_history['涨跌'] = df_history['估值总和'].diff()

def maximum_drawdown(prices):
    """
    计算最大回撤及其区间。

    :param prices: 股票价格序列（列表或NumPy数组）
    :return: 最大回撤值和最大回撤区间（开始索引和结束索引）
    """
    # 转换为 NumPy 数组
    prices = np.array(prices)
    
    # 示例使用
    cumulative_sum = prices.cumsum()  # 计算积分

    data =np.array( cumulative_sum)
    # max_dd, (start, end) = maximum_drawdown(prices)

    index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
    # print(index_j)                      ###maximum loss
    index_i = np.argmax(data[:index_j])  # 开始位置
    # print(index_i)                       ##maximum gain
    d = data[index_j] - data[index_i]  # 最大回撤
    return(d, index_i, index_j)

def plot_dividend(df):


    df.rename(columns={'估值': '估值总和', '日期':"date"}, inplace=True)
    df['PV_DIFF'] = df['估值'].diff()
    df.loc[0, 'PV_DIFF'] = 0
    print(df.head())


    times_str = []
    tt = df['date']
    for t in tt:
        times_str.append(t.strftime('%Y%m%d'))
    # 查找特定日期
    target_date = '20251231'  # 要寻找的日期
    if target_date in times_str:
        index = times_str.index(target_date)
        found_date = df['date'].iloc[index]
        print(f"找到日期: {found_date}")
    else:
        print("未找到日期 2025-12-31")

    fig = plt.figure(figsize=( 10, 6 ))
    gs = GridSpec(nrows=1, ncols=1)#, width_ratios=[3, 1, 1, 0], height_ratios=[1, 1])

    # 第一个子图：绘制 qdt 列的散点图

    ax1 = fig.add_subplot(gs[0, 0])  # 第一行，占据前 3 列ax3 = fig.add_subplot(2,1)
    colors = ['red' if value > 0 else 'green' for value in  df['PV_DIFF']]
    line1 = ax1.bar(times_str, df['PV_DIFF'], label = '每日盈亏', color = colors)
    ax1.plot(times_str, df['PV'] * 0, 'k--')

    data =np.array( df['PV'])
    # print('近一个月累积收益：' , data[-1])

    # ax1.plot(times_str,  df['PV'], 'b', label='累计估值')
    line2 = ax1.plot(times_str[:index+1],  df['PV'][:index+1], 'b',alpha = 0.6, label='累计估值2025')
    line3 = ax1.plot(times_str[index:],  df['PV'][index:], 'b',alpha = 1, label='累计估值2026')

    down, index_i, index_j = maximum_drawdown(df['PV_DIFF'])
    ax1.plot([index_i, index_j], [data[index_i], data[index_j]], 'o', color="k", markersize=8)
    itv = int(len(df)/10)
    if len(df)>63:
        pass
    else:
        itv =1
    # 设置每 60 个数据点一个 xtick
    ax1.set_xticks(times_str[::itv])
    ax1.set_xticklabels(times_str[::itv], rotation=45)
    ax1.grid(True)
    # yticks = ax1.get_yticks()
    # ax1.set_yticklabels([f'{val/1e7:.2f}千万' for val in yticks])
    ax1.legend(loc='upper left')
    # lines = [line1, line2, line3]  # 将两条线的 Handles 组合在一起
    # labels = [line1.get_label(), line2.get_label(), line3.get_label()]  # 获取每条线的标签
    close   = 1
    if close:
        # 创建共享 X 轴的右侧 Y 轴
        ax2 = ax1.twinx()  # 创建一个共享 X 轴的新轴
        line4 = ax2.plot(times_str, df['500收盘价'], 'k--',alpha = 0.2, label='中证500收盘')
        line5 = ax2.plot(times_str, df['1000收盘价'], color='k',alpha = 0.3, label='中证1000收盘')
        ax2.set_ylabel('收盘点位')
        ax2.legend(loc='lower right')
        # lines = [line1, line2, line3, line4, line5]  # 将两条线的 Handles 组合在一起
        # labels = [line1.get_label(), line2.get_label(), line3.get_label(),line4.get_label(), line5.get_label()]  # 获取每条线的标签
    # 设置背景色和边框
    plt.gca().patch.set_facecolor('#ffffff')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_linewidth(1)
    plt.gca().spines['left'].set_linewidth(1)

    plt.tight_layout()
    print(folder_path, os.path.join(folder_path, 'IMAGES\\dividend_plot.png'))
    plt.savefig(os.path.join(folder_path, 'IMAGES\\dividend_plot.png'), dpi=300)
plot_dividend(df_history)
