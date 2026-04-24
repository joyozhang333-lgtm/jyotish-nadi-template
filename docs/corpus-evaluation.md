# 真实语料评测框架

## 当前状态

现在还没有足够的真实纳迪叶手稿、OCR 语料、叶束索引和标注集，所以当前不能声称“真实语料评测已经完成”。

这轮已经完成的是：

- 评分模块：`nadi_leaf/evaluation.py`
- 评测脚本：`scripts/evaluate_reading.py`
- 样例 case：`evaluations/cases/sample-case.json`
- rubric：`evaluations/rubrics/reading-rubric.json`
- benchmark 结果：固定样例当前可跑到 `98/100`
- 新增：`score_accuracy_profile(...)`，专门把“可对外声称的命理准确度分”单独拆出来

## 这套框架在评什么

1. 盘面正确性
2. 章节完整度
3. 解释一致性
4. 边界纪律
5. 证据与评测准备度

同时现在还会单独评：

1. 盘面计算准确度
2. 解读可追溯性
3. 实证验证成熟度

## 现在为什么还不能把“95+”理解成全面完成

因为下面这些关键资产还缺：

- 专家复核样本
- 多个真实用户 case 的长期回看
- 纳迪相关原始语料或稳定译文
- 指纹分类标注集

也就是说，现在可以把 `95+` 用在内部产品质量 benchmark 上，但还不能把它直接翻译成“真实命理准确率 95+”。

## 下一步数据建设

1. 沉淀 `20-50` 个固定出生样例。
2. 每个样例加入人工核验字段：
   - 家庭结构
   - 关系状态
   - 事业轨迹
   - 迁移历史
   - 灵性 / 修行线索
3. 让专家或高质量用户对章节命中度做回看打分。
4. 把这些分数接回 `evaluation.py`。

## case 元数据要求

后续每个 case 应尽量带上：

- `benchmark_case_count`
- `expert_review_count`
- `longitudinal_follow_up_count`

这样 `score_accuracy_profile(...)` 才能真实反映产品离“可对外声称 95+”还有多远。
