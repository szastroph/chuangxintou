import pandas as pd

# 读取Excel文件
file_path = '工作簿1.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 检查数据列名
print("原始数据列名:", df.columns)
print("\n原始数据前几行:")
print(df.head())

# 将数据透视：项目名为列名，姓名为行名，工资为值
pivot_df = df.pivot(index='姓名', columns='项目名', values='工资')

# 填充缺失值为0（如果有的话）
pivot_df = pivot_df.fillna(0)

# 保存到新的Excel文件
output_file = '整理后的工资表.xlsx'
pivot_df.to_excel(output_file)

print(f"\n数据已成功保存到 {output_file}")
print("\n整理后的数据:")
print(pivot_df)
