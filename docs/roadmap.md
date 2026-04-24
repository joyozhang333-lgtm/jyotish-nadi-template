# Roadmap

## M0 已完成

- 新建工作区 `nadi-leaf`
- 建立 skill 骨架
- 建立产品规划与架构文档
- 固定初始数据契约

## M1 底层接入

- 选定默认计算引擎
- 写 `Chart Adapter`
- 输出最小 `chart.json`
- 为示例出生数据跑通一版结果
- 加入可选指纹输入位

## M2 阅读 MVP

- 实现身份核验问题生成
- 实现 16 个 Kandam 映射
- 实现章节选择输入
- 实现事业 / 财富 / 灵性专题
- 实现 evidence tags
- 实现统一 CLI / JSON renderer

## M3 演示版本

- 提供脚本入口
- 准备 3 组样例
- 写测试覆盖核心数据结构与输出稳定性
- 提供指纹探索性分类说明

## M3.5 研究增强基础版

- 接入第二引擎 `jyotishganit`
- 实现 `cross validation`
- 实现质量评分框架
- 落地真实语料评测 contract 与 sample case

## M4 扩展

- 已扩到 16 Kandam
- 增加多 runtime 适配
- 加入更细粒度的 timing windows
- 引入更强的专题模板与引用体系
- 加入 ayanamsa / node model 对齐开关

## M5 真实语料评估

- 调研是否能获得可用手稿 / OCR / 指纹索引
- 如果没有，明确停在“解释层产品”
- 若进入真实语料层，先做 license review 与数据校验流程
