---
name: nadi-leaf
description: "纳迪叶 / Nadi Jyotisha 解读技能。根据阳历出生日期、准确出生时间、出生地点与问题，先生成结构化吠陀盘面，再输出 Nadi-style 身份核验问题、Kandam 分章节解读、时间窗口与证据标注。触发词: 纳迪叶, Nadi, Naadi, Nadi leaf, Nadi Jyotisha, Agastya Nadi, Bhrigu Nadi, Kandam, 吠陀占星, Vedic astrology, Jyotish."
---

# Nadi Leaf Skill

这是一个以“诚实可落地”为原则的纳迪叶 / 吠陀占星 skill 工作区。当前产品形态只针对 `Codex skill`，不先扩到 API 或咨询师后台。目标不是假装已经拥有真实叶片数据库，而是先把产品拆成可开发、可验证、可持续迭代的三层：

- 吠陀占星计算层
- 纳迪风格解释层
- 真实叶片匹配层

## 使用时机

- 用户要做纳迪叶 / Nadi Jyotisha 相关解读
- 用户要把吠陀盘面转成 Kandam 式阅读
- 用户要做纳迪主题产品、skill、API 或知识库
- 用户要判断现有开源基础够不够支撑一个产品级实现

## 必要输入

- 阳历出生日期
- 尽量精确到分钟的出生时间
- 出生地点，或至少时区 / UTC offset
- 当前最关心的问题或阅读焦点
- 可选：指纹图片，仅用于探索性分类或质量判断

如果缺出生时间或地点，必须显式说明精度下降，尤其影响 Lagna、宫位、Dasha 与事件时间窗。

## 工作原则

1. 先算盘，再解读。没有结构化盘面时，不直接输出完整纳迪式结论。
2. 不伪造“真实 palm leaf 已找到”。只有在具备可追溯语料、索引和校验链路时，才允许宣称真实叶片匹配。
3. 每条关键结论都要落到证据标签之一：
   - `classical_rule`
   - `interpretive_mapping`
   - `requires_corpus`
4. 真实纳迪流程中的“手印 -> 叶束 -> 核验问答 -> 找叶片”与普通吠陀排盘不同，不能混用术语来掩盖能力边界。
5. 指纹图片当前只能做：
   - 清晰度检查
   - 基础纹型分类（如 loop / whorl / arch）
   - 作为未来叶束分类模块的预留输入
   不能直接做“真实纳迪叶认证”。
6. 对外输出优先给：
   - 身份核验问题
   - Kandam 重点
   - 时间窗口
   - Remedy 候选
   - 能力边界说明

## 当前工作区结构

- `SKILL.md`
- `agents/openai.yaml`
- `docs/product-plan.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/contracts/`
- `references/open-source-foundations.md`
- `references/kandam-map.md`
- `references/evidence-policy.md`
- `references/fingerprint-boundary.md`
- `references/theme-packs.md`
- `nadi_leaf/models.py`
- `tests/test_models.py`

## 开发策略

### 第一阶段：复用开源底座

- 计算引擎候选优先看 `references/open-source-foundations.md`
- 当前最优本地 Python 候选是 `PyJHora`
- API / MCP 形态可参考 `jyotish-api` 与 `jyotish-mcp`
- Nadi 主题知识库可参考 `ndastro-api` 与 `BhriguWelt`

### 第二阶段：自建解释层

- 把结构化盘面映射成 Kandam 阅读
- 默认支持公开常见的 16 个 Kandam：
  - 1 身份总纲
  - 2 财富、家庭、教育、表达
  - 3 兄弟姐妹、胆识、技能
  - 4 家宅母缘
  - 5 子女、创造力、传承
  - 6 疾病、债务、敌对、诉讼
  - 7 婚姻关系
  - 8 寿元、风险、危机、转化
  - 9 父缘、福德、导师、远行
  - 10 事业职业
  - 11 收益、机会、社群、二次关系
  - 12 迁移、开销、灵性、解脱
  - 13 Santhi Pariharam / 前世业力与补救
  - 14 Deekshai / mantra、护持与纪律
  - 15 Aushadha / 长期健康倾向
  - 16 Dasa Bukthi / 大运分运预测
- 对 1、4、7、10、12 仍提供更长篇叙述，因为它们是高频核验章节
- 同时提供 3 个专题包：
  - 事业版
  - 财富版
  - 灵性版
- 每条输出都带证据标签
- 第 8、15 章必须显式保留安全边界：不预测死亡日期，不输出诊断、药方或剂量
- 第 13、14 章涉及真实叶片、前世叙事、mantra、护符时，必须标注 `requires_corpus`

### 第三阶段：真实叶片层

只有在拿到以下能力后，才进入这一层：

- 手印分类体系
- 叶束索引数据
- 手稿 OCR / transcript
- verse 对齐
- 翻译与人工校勘

## 输出要求

- `chart_summary`
- `requested_chapters`
- `identity_checks`
- `kandam_reading`
- `theme_sections`
- `timing_windows`
- `remedy_candidates`
- `evidence_notes`
- `missing_capabilities`

## 读取顺序

1. 先读 `docs/product-plan.md`
2. 再读 `docs/architecture.md`
3. 然后根据任务只加载相关 reference：
   - 开源基础选型：`references/open-source-foundations.md`
   - 16 Kandam 设计：`references/kandam-map.md`
   - 输出与声明边界：`references/evidence-policy.md`
   - 指纹能力边界：`references/fingerprint-boundary.md`
   - 专题包设计：`references/theme-packs.md`
