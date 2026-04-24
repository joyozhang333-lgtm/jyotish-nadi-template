# 多引擎交叉验证

## 目标

让 `Nadi Leaf` 不只依赖单一底层引擎，而是把关键盘面字段做显式对比：

- `lagna`
- `moon sign`
- `nakshatra`
- `dasha`
- 九星宫位和度数

## 当前实现

- 主引擎：`PyJHora`
- 第二引擎：`jyotishganit`
- 入口：
  - `nadi_leaf/jyotishganit_adapter.py`
  - `nadi_leaf/cross_validator.py`

输出结构：

- `matches`
- `minor_diffs`
- `major_diffs`
- `configuration_notes`
- `validation_score`

## 当前真实发现

1. `PyJHora` 若直接沿用上游默认值，会走 `TRUE_PUSHYA`。
2. 当前产品已经把主引擎默认改成 `LAHIRI`。
3. `jyotishganit` 当前 ayanamsa 是 `True Chitra Paksha`。
4. 在当前 benchmark 样例下：
   - `lagna / moon / nakshatra / mahadasha / antardasha` 已对齐
   - 大多数行星度数差异已缩到 `0.02` 度量级
   - 剩余主要差异集中在 `Rahu / Ketu` 度数

## 当前工程结论

- 交叉验证已经可运行。
- `LAHIRI` 和 `KP` 目前是最稳的主引擎配置。
- 当前 benchmark 上交叉验证分已达到 `94/100`。
- 还不能说“所有引擎完全对齐”，因为节点模型差异仍在。

## 下一步

1. 继续研究节点使用 `mean node` 还是 `true node`。
2. 扩大 calibration 样例，不只看单一出生盘。
3. 把最优 ayanamsa 配置基线固定到 case 集评测。
