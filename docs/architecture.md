# 架构设计

## 目标架构

```text
User Input
  -> Input Normalizer
  -> Fingerprint Classifier (optional)
  -> Chart Adapter
  -> Cross Validator (optional)
  -> Structured Chart
  -> Identity Check Generator
  -> Kandam Mapper
  -> Theme Pack Builder
  -> Timing Window Engine
  -> Evidence Tagger
  -> Quality Scorer / Corpus Eval Harness
  -> Renderer / Skill Output
```

## 模块划分

### 1. Input Normalizer

职责：

- 归一化日期、时间、地点、时区
- 标记输入质量
- 为后续计算给出统一输入对象

### 2. Chart Adapter

职责：

- 屏蔽具体开源引擎差异
- 输出统一 `chart.json`
- 当前默认主引擎是 `PyJHora (LAHIRI)`
- V1 默认走 `rasi_chart + divisional_chart + vimsottari` 的低层稳定路径
- 暂不依赖 `Horoscope` 高层封装，因为它要求额外 Swiss Ephemeris 数据文件
- 当前已接入第二引擎 `jyotishganit`
- 第二引擎只作为 `cross validation` 使用，不会悄悄覆盖默认主引擎输出
- `jyotishganit` 的 dasha `current/upcoming` 字段不直接信任，必须基于完整 period tree 按 `reference_date` 重算
- `PyJHora` 每次调用前都会显式初始化 Swiss Ephemeris 和 ayanamsa，避免全局状态污染

### 2.5 Fingerprint Classifier

职责：

- 检查指纹图片是否可读
- 输出基础纹型分类
- 未来为叶束分类预留输入

当前实现：

- 基于 `orientation field + Poincare singularity` 的第一版 CV 管线
- 支持 `loop / whorl / arch / manual_review_required`
- 输出 `confidence / detected_cores / detected_deltas / image_quality`

当前边界：

- 可以做探索性图像分析
- 不可以做真实纳迪叶匹配认证

### 2.8 Cross Validator

职责：

- 运行 `PyJHora` 与 `jyotishganit` 两套引擎
- 对比 `lagna / moon / nakshatra / dasha / planets`
- 把差异分成 `matches / minor_diffs / major_diffs`
- 输出 `configuration_notes`

当前已发现的真实差异：

- `PyJHora` 默认 ayanamsa 是 `TRUE_PUSHYA`
- `jyotishganit` 当前固定为 `True Chitra Paksha`
- 这会直接影响节点度数和 dasha 结果

### 2.9 Quality Scorer / Corpus Eval Harness

职责：

- 基于结构完整度、证据标签、边界纪律和交叉验证结果给内部质量分
- 为将来的真实样本和专家复核预留评分接口
- 明确区分 `产品质量分` 与未经验证的“命理准确率”

### 3. Identity Check Generator

职责：

- 生成纳迪式身份核验问题
- 输出可验证项，不抢先给满结论

例子：

- 父母结构
- 兄弟姐妹数量与关系
- 婚姻状态或重要关系节点
- 职业路径中的转折
- 外地 / 国外迁移倾向

### 4. Kandam Mapper

职责：

- 把结构化盘面映射到 Kandam
- 默认支持公开常见的 1-16 Kandam
- 对 1 / 4 / 7 / 10 / 12 保留长篇叙述
- 对 8 / 13 / 14 / 15 加强证据与安全边界

### 4.5 Theme Pack Builder

职责：

- 基于 Kandam 与盘面组合专题报告
- 第一批专题：
  - 事业版
  - 财富版
  - 灵性版

原则：

- 专题不是脱离盘面的新体系
- 专题是 Kandam 与盘面信号的重组视图

### 5. Timing Window Engine

职责：

- 用 dasha / bhukti / transit / house emphasis 给时间窗
- 不强装成“叶片原文给出的绝对日期”

### 6. Evidence Tagger

职责：

- 给每条结论打标签
- 降低越界叙述风险

## 初始代码组织

- `nadi_leaf/models.py`
  - 核心数据结构
- `nadi_leaf/chart_adapter.py`
  - `PyJHora` 适配器与稳定 chart 输出
- `nadi_leaf/jyotishganit_adapter.py`
  - 第二引擎适配器与统一摘要输出
- `nadi_leaf/cross_validator.py`
  - 多引擎交叉验证
- `nadi_leaf/reading_engine.py`
  - 16 个 Kandam + 3 个专题包的解释层
- `nadi_leaf/fingerprint.py`
  - 探索性指纹分型 CV
- `nadi_leaf/evaluation.py`
  - 质量评分与评测框架
- `nadi_leaf/cli.py`
  - demo / CLI 入口
- `scripts/evaluate_reading.py`
  - 端到端评测入口
- `evaluations/`
  - 样例 case 与 rubric
- `docs/contracts/`
  - JSON 契约
- `references/`
  - 开源基础与知识设计

## 默认技术路线

- 语言：Python
- 适配层：本地 adapter pattern
- skill 层：LLM-friendly markdown + structured object
- 依赖策略：在本工程显式锁 `PyJHora` 相关运行依赖，不信任上游 wheel 的依赖声明完整性
- 第二引擎策略：`jyotishganit` 目前用于对照，不直接替代默认主引擎

## 当前工程注意事项

1. `PyJHora` PyPI 包的运行依赖声明不完整，必须由本项目补锁。
2. `rasi_chart` 默认会带上额外点位，解释层若只做九星体系，必须显式过滤。
3. `PyJHora` import 会打印路径噪音；若要输出纯 JSON，需要在集成层压掉 stdout。
4. `PyJHora` 上游默认 ayanamsa 为 `TRUE_PUSHYA`，当前产品已显式改为 `LAHIRI`。
5. `jyotishganit` 内建的 dasha `current/upcoming` 直接依赖运行时 `datetime.now()`，不能直接拿来做严肃对比。
6. `PyJHora` 显式切换某些 `TRUE_*` ayanamsa 模式时，若未先初始化 Swiss Ephemeris，可能直接报错；当前产品默认走稳定的 `LAHIRI`。

## 为什么先不做真实叶片层

因为真实叶片层依赖的不是一个“更强模型”，而是数据资产：

- 指纹分类
- 叶束索引
- 手稿语料
- OCR / 译文
- 人工校验流程

没有这些，做出来的也只是“纳迪风格解释器”，不是“真实纳迪叶匹配系统”。
