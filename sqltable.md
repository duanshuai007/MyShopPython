

#### 1.仓库表
用来保存入库和出库的所有记录，该表只保存整体的库存数量以及售卖数量，卖出的金额等信息。

|商品编号|商品名称|商品拼音名|入库总数量|售卖总数量| 总成本 | 总售卖金额| 
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|u32ProductID | c32ProductName | c32PinyinName | u32Inventory | u32Sold | fCost | fIncome |


#### 2.流水表
按照月份每个月生成一个表，该表记录详细的售卖信息，包括年月日时分卖出多少数量的什么货物，共售卖多少钱等信息。

| 消息id | 时间 | 商品编号 | 售出数量 | 售出金额 | 
|:-:|:-:|:-:|:-:|:-:|
|u32ID | time | u32ProductID	|	u32Sold | fIncome |

按照月份每月生成一个入库记录表，用来记录详细的入库货物信息，包括年月日时分入了多少数量的什么货物，成本多少钱等信息

| 消息id | 时间 | 商品编号 | 入库数量| 进货成本 |
|:-:|:-:|:-:|:-:|:-:|
|u32ID |time	|u32ProductID	 | u32Inventory | fCost|
 
 
#### 3.每日统计

根据当日的销售情况生成一个图表，以柱状图的方式来显示每种货物的售卖情况。


#### 4.每月统计

每月统计分成几种方式显示：

1.根据每日销售金额生成曲线图。

2.根据销售