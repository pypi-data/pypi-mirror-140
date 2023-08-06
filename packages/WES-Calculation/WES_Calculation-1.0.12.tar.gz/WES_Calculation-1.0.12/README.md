<!--
 * @Author: BDFD
 * @Date: 2021-10-27 18:39:19
 * @LastEditTime: 2022-03-02 13:53:41
 * @LastEditors: BDFD
 * @Description: In User Settings Edit
 * @FilePath: \5.2-PyPi-WES_Calculation\README.md
-->

# Package Name

Package function description

## Installation

`pip install WES-Calculation`

## Function and Requirements

`import WES_Calculation as wes`

### Gumbel Function Usage

> Gumbel Model Necessary Input Parameter

`wes.gumbel(datao, unitx, unitt, i1, i2)`

- datao: 样本数据<br>

```
    >Input Type: list type
    >Demo Input: '1.55, 1.4, 1.35, 1.26, 1.2, 1.16, 1.1, 1.05, 1.01, 0.97, 0.88, 0.86, 0.82, 0.8, 0.75'
```

- unitx: 物理量单位<br>

```
    > Input Type: string type
    > Demo Input: 'Inch','inch'
```

- unitt: 样本数据的时间间隔<br>

```
  > Input Type: string type
  > Demo Input: 'Year','year'
```

- i1: 概率分析的类型 <br>

```
  > Input Type: Int type
  > Explaination:
  >   1 for 极大值
  >   2 for 极小值(Only Two Valid Input)
  > Demo Input: 1
```

<!-- - i2 概率空间是否截尾 <br>

  > Input Type: Int type
  > Explaination: 1 for 否, 2 for 是(Only Two Valid Input)
  > Demo Input: 1 -->

- i2: 经验估计频率模型 <br>

```
  > Input Type: Int type
  > Explaination:
  >   1 for Weibull
  >   2 for 中值
  >   3 for Gringorton(Only Three Valid Input)
  > Demo Input: 3
```

- Output <br>

```
  > Result: list type
  > Explaination:
  >   plot_url: result graph for input
  >   data: result data for table value
  > Demo Output:
  >   result = wes.gumbel(datao, unitx, unitt, i1, i2)
  >   plot_url = result[0]
  >   data = result[0]
```

## License

copyright @ 2021 BDFD

This repository is licensed under the MIT license. See LICENSE for details.

### References

https://github.com/bdfd/5.2-PyPi-WES_Calculation
