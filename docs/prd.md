# Nadi Leaf PRD

## 1. 产品定义

`Nadi Leaf` 是一个运行在 Codex 内的纳迪叶风格 skill。它以结构化吠陀盘面为底座，输出：

- 身份核验问题
- 可选 Kandam 分章节报告
- 专题报告
- 时间窗口
- remedy 候选
- 证据标签与能力边界说明

它不是“真实叶片已经找到”的产品，也不把指纹图片包装成真实纳迪认证。

## 2. 产品目标

### 核心目标

1. 先把出生资料稳定转成统一吠陀盘面。
2. 再把盘面转成可追问、可分章节、可分专题的纳迪风格阅读。
3. 所有用户可见结论必须可追溯到规则、解释映射或明确的语料缺口。

### 非目标

1. 不做真实 palm leaf 检索。
2. 不做手印找叶。
3. 不做叶片 OCR 与 verse 对齐。
4. 不对外宣称“95% 命理预测准确率已验证”。

## 3. 用户与场景

### 目标用户

1. 想要纳迪叶式阅读，但不接受纯神秘话术的个人用户。
2. 想在 Codex 内直接调用技能进行专业解读的重度用户。
3. 想把吠陀占星与纳迪主题做成严肃产品的开发者。

### 核心场景

1. 用户输入出生资料，选择 `1-16` 任意章节，得到分章阅读。
2. 用户只选 `事业版 / 财富版 / 灵性版` 专题，得到聚焦报告。
3. 用户上传指纹图片，系统只做图片质量评估和边界提示，不假装找到了叶片。
4. 产品内部可运行多引擎交叉验证，暴露盘面差异与配置风险。

## 4. 功能范围

### V1 必做

1. 输入归一化
2. 输入质量判断
3. `PyJHora` 底层盘面适配
4. `chart.json` 稳定输出
5. 16 个公开常见 Kandam
6. 3 个专题包
7. 身份核验问题
8. 时间窗口
9. remedy 候选
10. 证据标签
11. CLI / script demo
12. 探索性指纹纹型 CV
13. 多引擎交叉验证
14. 内部质量评分

### V2 扩展

1. 专题与章节交叉引用
2. 更完整的样例库
3. 更细的窗口粒度
4. ayanamsa / node model 对齐开关
5. 指纹分类样例集与人工复核闭环
6. 第 16 章加入 transit 与回看校准

### V3 研究增强

1. 文献引用体系
2. 专家评审闭环
3. 真实语料可行性评估
4. 真实 case 回测与评分自动化

## 5. 用户输入与输出

### 输入

- 阳历出生日期
- 出生时间
- 出生地点
- 时区 / UTC offset
- 请求章节
- 请求专题
- 可选指纹图片

### 输出

- `chart_summary`
- `requested_chapters`
- `requested_theme_packs`
- `identity_checks`
- `kandam_reading`
- `theme_sections`
- `timing_windows`
- `remedy_candidates`
- `missing_capabilities`

## 6. 系统设计

### 主链路

`Input -> Chart Adapter -> Structured Chart -> Reading Engine -> Evidence Tagger -> Renderer`

### 技术栈

- Python 3.11+
- `PyJHora` 作为当前默认吠陀引擎
- `jyotishganit` 作为当前第二引擎
- 本地 adapter pattern 隔离上游依赖问题
- Codex skill 作为唯一产品承载形态

### 当前工程结论

1. `PyJHora` 的低层 `rasi_chart / divisional_chart / vimsottari` 可稳定用于 MVP。
2. `PyJHora` 的高层 `Horoscope` 依赖额外 Swiss Ephemeris 文件，当前不作为默认路径。
3. `jyotishganit` 已可作为第二引擎跑通，但当前与 `PyJHora` 存在 ayanamsa / dasha 差异。
4. 产品层必须自己锁依赖，不能信任上游 wheel 的依赖声明完整性。

## 7. 质量标准

### 质量定义

这里的“95 分”先定义为 `产品质量分`，不是“玄学预测准确率 95%”。

质量分由五项组成，每项 20 分：

1. 盘面正确性
2. 章节完整度
3. 解释一致性
4. 时间窗口可用性
5. 边界与证据纪律

### 版本目标

1. V1 目标：内部质量分 `80+`
2. V2 目标：内部质量分 `95+`
3. V3 目标：在真实样本与专家评审引入后，争取可对外声明的准确度成熟度 `95+`

## 8. 验证策略

1. 单元测试验证 `chart adapter`、`cross validator`、`evaluation` 与 `reading engine` 的稳定输出。
2. 用固定出生样本做回归快照，避免输出结构漂移。
3. 用第二引擎做 `lagna / moon / nakshatra / dasha` 交叉验证。
4. 后续引入人工标注集，评估章节相关性与解释一致性。
5. 引入专家复核前，不宣称最终准确率。

## 9. 风险

### 9.1 开源引擎依赖脏

- 风险：`PyJHora` wheel 的依赖声明不完整。
- 应对：在本项目 `pyproject.toml` 显式锁定运行依赖。

### 9.2 高层星历文件缺失

- 风险：Swiss Ephemeris 数据不完整时，高层 API 会失败。
- 应对：V1 先走低层 chart/dasha 路径。

### 9.3 多引擎结论不一致

- 风险：两个引擎给出不同 dasha 或节点度数，用户误以为系统已经足够权威。
- 应对：强制输出 cross validation 与 configuration notes，不隐藏 major diff。

### 9.4 用户误解成真实纳迪叶

- 风险：把纳迪风格解释误当真实叶片。
- 应对：输出层强制保留边界声明和 `missing_capabilities`。

### 9.5 法律与开源协议风险

- 风险：`PyJHora` 为 AGPL，商业闭源分发需要重新评估许可路径。
- 应对：V2 前完成 license review，必要时替换底层引擎。
