# 产品开发规划

## 当前定位

`Nadi Leaf` 是一个运行在 Codex 内的纳迪叶风格解读 skill。当前产品主线已经明确：

1. 只做 `Codex skill`
2. 默认支持 `16 个 Kandam + 3 个专题包`
3. 底层默认接 `PyJHora (LAHIRI)`
4. 所有输出都带 `evidence_tag`
5. 明确停在“解释层产品”，不伪装成真实叶片系统

## 当前已完成

### 工程面

- skill 工作区骨架
- 统一数据模型
- `PyJHora` 最小运行链路验证
- `chart adapter` 初版
- `PyJHora` 主引擎校准到 `LAHIRI`
- `jyotishganit adapter` 初版
- `cross validator` 初版
- `primary engine calibration` 初版
- `reading engine` 已扩展到 16 Kandam
- `quality scorer` 初版
- CLI demo 入口
- 评测脚本入口
- 单元测试骨架与交叉验证测试
- 完整 16 章 Markdown 导出预设
- 用户反馈贴合度评分

### 文档面

- 架构设计
- 输入输出契约
- Kandam 映射
- 专题包设计
- 指纹边界文档
- PRD
- 质量评分框架

## 需要优先看的文档

1. [PRD](prd.md)
2. [质量评分框架](quality-scorecard.md)
3. [架构设计](architecture.md)
4. [Roadmap](roadmap.md)
5. [命理准确度评分标准](accuracy-standard.md)

## 当前版本结论

### V1 范围

- 输入归一化
- 输入质量判断
- 结构化盘面
- 16 个公开常见 Kandam
- 事业 / 财富 / 灵性专题
- 身份核验问题
- 时间窗口
- remedy 候选
- 指纹探索性分型
- 证据与边界输出
- 可选多引擎交叉验证
- 可选主引擎校准
- 可选内部质量评分

### V1 边界

- 不做真实叶片匹配
- 不做手印找叶
- 不宣称 95% 命理预测准确率
- 当前只能先追求“工程质量分”和“解释一致性”
- 当前 `98/100` 只代表固定 benchmark 样例上的内部产品质量分
- 它不代表“命理准确率 98%”
- 当前新增 `accuracy_profile` 后，可以把“盘面计算准确度”和“实证验证成熟度”分开看
- 当前新增 `feedback_alignment` 后，可以把用户标注的 `准 / 半准 / 不准` 转成个人校准分
- 第 8 章不输出死亡日期或灾难定论
- 第 15 章不输出诊断、药方、剂量或替代医疗建议
- 第 13/14 章的前世叙事、mantra、护符和仪轨必须等真实语料或传承文本复核

## 当前 blocker

1. `PyJHora` 改到 `LAHIRI` 之后，`dasha` 已和第二引擎对齐，但 `Rahu/Ketu` 度数仍有 node model 差异。
2. 真实语料评测目前还是 `sample case + rubric`，还没有大样本。
3. 指纹分型已有第一版 CV，但缺少标注数据和人工复核集。
4. 目前还没有公开、可信、可直接训练的 thumb-index 叶束数据集。

## 下一步

1. 继续研究 node model 对齐，缩窄 `Rahu/Ketu` 度数偏差。
2. 建 `20-50` 个真实 case 样例库，把 `98/100` 从单样例 benchmark 扩到小样本 benchmark。
3. 继续补强第 2/3/5/6/8/9/11/13/14/15/16 章的叙事深度。
4. 为第 16 章加入 transit、年度/季度事件窗口和真实反馈回看。
