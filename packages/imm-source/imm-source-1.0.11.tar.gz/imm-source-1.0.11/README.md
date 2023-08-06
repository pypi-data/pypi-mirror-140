### V1.0.9
- Excel：去除了info-sheet 变量改变成大写开头。
### V1.0.6
- Excel: 改写了 __add__. 原来只能2个excel相加，现在可以任意excel相加了。 

### V1.0.5 
- makeExcel: 更新。 原来输入sheets/tables的时候，如果是None或[]都是一样处理。导致如果是[]的时候也像None一样处理，于是产生了不需要的sheets/tables。现在只对None处理，如果是None才产生所有的;
如果是[]，则不产生对应的sheets/tables 
    sheets=sheets if sheets is not None else self.sheets.values()
    tables=tables if tables is not None else self.tables.values()

### V1.0.4
- Excel + ： 行和列都相加，并且能合并相同的行 （相同行定义是该行前3列数据一样）改回原来的。

### V1.0.3 
- Excel + ： 只是把行append到原来的excel中。 准备考虑放弃。

### V1.0.2 
- Excel + ： 行和列都相加，并且能合并相同的行 （相同行定义是该行前3列数据一样）


