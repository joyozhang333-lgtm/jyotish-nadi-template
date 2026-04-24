# Jyotish Nadi Template

**Jyotish Nadi Template** is an open-source template for building Vedic astrology / Jyotish reading systems with a Nadi-style chapter structure. It is explicitly **based on Vedic astrology calculations** rather than original Nadi leaf manuscripts. It converts birth data into a structured Vedic chart, maps the chart into 16 common Kandam-style reading chapters, adds timing windows, evidence tags, quality scoring, and clear product boundaries.

> Important: this repository is **not** a collection of original Nadi palm leaf manuscripts, not a digitized Nadi leaf corpus, not an authenticated Agastya Nadi / Bhrigu Nadi text, and not a fingerprint-to-leaf matching system. It is a software template for **Nadi-style interpretation built on Vedic astrology calculations** and can be used as a reference for people who want to understand how Nadi-style readings may relate to Jyotish chart factors.

中文：**Jyotish Nadi Template** 是一个开源的吠陀占星 / Jyotish 解读模板。它明确依据的是**吠陀占星计算体系**，不是纳迪叶原文。它用于把出生资料转成结构化吠陀盘面，并按公开常见的 16 个 Kandam 章节生成纳迪风格报告。它可以作为大家了解 Nadi 叶、Nadi-style reading 和吠陀占星关系的参考，但不能宣称“已经找到某个人的真实纳迪叶”。

## SEO Keywords

Vedic astrology, Jyotish, Nadi astrology, Nadi Jyotisha, Naadi astrology, Agastya Nadi, Bhrigu Nadi, Kandam, palm leaf astrology, Vedic birth chart, Vimshottari Dasha, Dasha Bhukti, Nadi reading template, Nadi leaf reference, learn Nadi astrology, AI astrology, Codex skill, astrology report generator, 吠陀占星, 印度占星, 纳迪叶, 纳迪占星, 纳迪叶参考, 纳迪叶入门, 纳迪风格解读, 16 Kandam, 大运分运, 纳迪叶模板。

## What Is Vedic Astrology / Jyotish?

Vedic astrology, also known as **Jyotish**, is a traditional Indian astrology system that interprets a birth chart through sidereal zodiac signs, houses, planetary lords, Nakshatras, Vargas, and planetary periods such as Vimshottari Dasha. A Jyotish reading usually starts from precise birth data, calculates the Lagna or ascendant, places planets into houses and signs, and then interprets life themes such as character, family, relationships, profession, wealth, health tendencies, spirituality, and timing cycles.

In this project, Vedic astrology is the calculation and evidence foundation. The software first builds a structured Jyotish chart, then maps that chart into a Nadi-style report structure. This means the output is grounded in chart factors such as house lords, planetary placements, Dasha periods, Navamsa, and evidence tags. It should be read as a **Vedic astrology-based Nadi-style template**, not as a recovered palm leaf scripture.

## How This Helps People Understand Nadi Leaves

Nadi astrology is often associated with palm leaf manuscripts, thumb impressions, identity verification, and chapter-based readings called Kandams. Many readers are curious about Nadi leaves but do not have access to authenticated manuscripts, original Tamil/Sanskrit palm leaf text, lineage-based translations, or verified leaf-bundle indexes.

This repository provides a transparent reference layer:

- It shows how a 16 Kandam-style structure can be modeled in software.
- It explains which parts can be derived from ordinary Jyotish chart factors.
- It marks which claims would require real Nadi leaf corpus data.
- It keeps Nadi-style interpretation separate from authentic palm leaf matching.
- It helps developers and researchers prototype a responsible educational tool for learning about Nadi-style readings.

## What This Project Does

- Calculates a structured Vedic astrology chart from birth date, time, location, and timezone.
- Uses `PyJHora` as the primary Jyotish calculation adapter.
- Uses `jyotishganit` as a secondary cross-validation engine.
- Generates Nadi-style readings across 16 common Kandam chapters.
- Supports focused theme packs for career, wealth, and spirituality.
- Adds identity-check questions to help users validate or reject claims.
- Adds timing windows based on Dasha and Bhukti periods.
- Adds `evidence_tag` labels to separate classical rules, interpretive mappings, and corpus-dependent claims.
- Includes a quality scorecard and feedback alignment scoring.
- Includes an exploratory fingerprint classifier boundary, without claiming real leaf matching.

## What This Project Does Not Do

- It does not contain original Nadi palm leaf text.
- It does not contain authenticated Nadi manuscript scans or OCR.
- It does not provide leaf-level ground truth labels.
- It does not perform real thumb impression to leaf-bundle matching.
- It does not prove 95% predictive astrology accuracy.
- It does not diagnose medical conditions, prescribe remedies, or predict death dates.

## 16 Kandam Coverage

The template supports a common public 16-chapter Nadi reading structure:

1. Identity and life overview
2. Wealth, family, education, and speech
3. Siblings, courage, skills, and initiative
4. Mother, home, property, and inner stability
5. Children, creativity, romance, and legacy
6. Disease, debt, enemies, litigation, and obstacles
7. Marriage, spouse, partnership, and relationship patterns
8. Longevity, risk, crisis, and transformation
9. Father, fortune, teachers, dharma, and long journeys
10. Career, profession, status, and public role
11. Gains, opportunities, networks, and social expansion
12. Expenditure, foreign lands, sleep, retreat, spirituality, and moksha themes
13. Santhi Pariharam: karmic patterns and remediation boundaries
14. Deeksha: mantra, discipline, and spiritual protection boundaries
15. Aushadha: health tendency boundaries, not medical diagnosis
16. Dasa Bukthi: Dasha-Bhukti timing windows

## Evidence Tags

Every important claim should be marked with one of these labels:

- `classical_rule`: derived from standard Jyotish chart factors such as houses, lords, planets, Vargas, and Dasha.
- `interpretive_mapping`: an interpretation or product-level synthesis based on chart factors.
- `requires_corpus`: a claim that would require authenticated Nadi leaf text, manuscript data, lineage material, or human verification before being treated as strong evidence.

## 中文介绍

### 项目定位

`Jyotish Nadi Template` 是一个“吠陀占星计算 + 纳迪风格章节报告”的开源模板。它的根基是吠陀占星，不是纳迪叶原文。换句话说，本项目先用 Jyotish 的排盘、宫位、星体、Nakshatra、Dasha、Navamsa 等方法建立盘面证据，再把这些证据组织成接近 Nadi 叶阅读体验的 16 Kandam 报告。

吠陀占星，也常称为 Jyotish，是印度传统占星体系。它通常以准确出生时间和地点为基础，计算上升、星体落宫、月宿、分盘和大运分运，用来观察一个人的性格、家庭、关系、事业、财富、健康倾向、灵性路径和时间周期。和现代心理测评不同，它更强调时间、业力主题、人生阶段和具体生活领域的联动。

Nadi 叶传统中会出现手印、叶束、身份核验、Kandam 分章、补救章节等元素。本项目不能替代真实 Nadi 叶阅读，但可以作为一个公开、可审计、可学习的参考：帮助读者理解 Nadi-style report 可能如何借助吠陀占星盘面来组织内容，也帮助开发者区分“可由 Jyotish 推导的内容”和“必须依赖真实叶片语料的内容”。

它适合用来开发：

- 吠陀占星 AI 解读系统
- 纳迪风格报告生成器
- Codex / agent skill
- Jyotish chart adapter
- 16 Kandam 分章报告模板
- 证据标签化的命理解读产品

### 明确边界

这个项目不是：

- 不是纳迪叶原文
- 不是 Agastya Nadi 或 Bhrigu Nadi 的原始文本
- 不包含真实 palm leaf 手稿扫描
- 不包含官方叶束索引
- 不支持真实指纹找叶
- 不宣称已经找到某个人的真实纳迪叶
- 不宣称命理预测准确率达到 95%

它做的是：在诚实边界内，用可复用的软件结构，把吠陀盘面转成纳迪风格、可核验、可评分、可迭代的解读报告。

### 可以作为 Nadi 叶入门参考

如果你想了解 Nadi 叶，本项目可以帮助你先理解几个基础问题：

- Nadi 叶报告为什么会按 Kandam 分章？
- 哪些内容可以从普通吠陀盘面中推导？
- 哪些内容必须依赖真实叶片、传承文本或人工校勘？
- 为什么“纳迪风格解读”和“真实纳迪叶原文”必须分开？
- 为什么指纹分类、叶束索引和身份核验不能和普通排盘混为一谈？

因此，本项目更适合被理解为 **Nadi 叶学习参考 / Nadi-style report template / Vedic astrology-based interpretation framework**。

## Quick Start

```bash
git clone https://github.com/joyozhang333-lgtm/jyotish-nadi-template.git
cd jyotish-nadi-template

python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pytest -q
```

Generate an example evaluation:

```bash
./.venv/bin/python scripts/evaluate_reading.py \
  --date 2000-01-01 \
  --time 12:00 \
  --location "Chennai, India" \
  --latitude 13.0827 \
  --longitude 80.2707 \
  --timezone-offset 5.5 \
  --timezone-name Asia/Kolkata \
  --reference-date 2026-04-23 \
  --case-file evaluations/cases/sample-case.json \
  --cross-validate \
  --min-product-score 95
```

Export Markdown reports:

```bash
./.venv/bin/python scripts/export_markdown_reports.py \
  --name "Demo Native" \
  --date 2000-01-01 \
  --time 12:00 \
  --location "Chennai, India" \
  --latitude 13.0827 \
  --longitude 80.2707 \
  --timezone-offset 5.5 \
  --timezone-name Asia/Kolkata \
  --reference-date 2026-04-23 \
  --case-file evaluations/cases/sample-case.json \
  --output-dir reports/demo
```

`reports/` is intentionally ignored by git because generated reports may contain private birth data.

## Skill Usage

The root `SKILL.md` can be used as a Codex skill. It tells an agent how to:

- calculate first, interpret second;
- avoid pretending that a real Nadi leaf has been found;
- keep Nadi-style identity checks separate from real leaf authentication;
- use evidence tags;
- respect health, death, mantra, and fingerprint boundaries.

## Architecture

```text
Input
  -> Chart Adapter
  -> Cross Validator
  -> Reading Engine
  -> Guidance Engine
  -> Report Writer
  -> Quality / Accuracy / Feedback Scoring
```

Key modules:

- `nadi_leaf/chart_adapter.py`: primary PyJHora chart adapter.
- `nadi_leaf/jyotishganit_adapter.py`: secondary engine adapter.
- `nadi_leaf/cross_validator.py`: multi-engine comparison.
- `nadi_leaf/reading_engine.py`: 16 Kandam and theme-pack reading bundle.
- `nadi_leaf/report_writer.py`: readable Markdown report writer.
- `nadi_leaf/evaluation.py`: product quality, accuracy profile, and feedback alignment scoring.
- `nadi_leaf/fingerprint.py`: exploratory fingerprint image quality and pattern classification.

## Quality Philosophy

This project separates three scores:

- **Product quality score**: structure, evidence tags, chapter coverage, boundary discipline, and testability.
- **Chart calculation accuracy**: agreement between calculation engines and benchmark chart fields.
- **Empirical validation maturity**: real cases, expert review, and longitudinal follow-up.

Without a real benchmark corpus and expert review, a high product score must not be marketed as a proven predictive accuracy rate.

## Data and Privacy

This repository is designed to be open-source safe:

- Private generated reports are ignored via `.gitignore`.
- User feedback files are ignored via `.gitignore`.
- The included sample case is anonymous demo data.
- Do not commit real birth data, names, fingerprint images, or generated personal reports.

## License

The template code is released under the MIT License.

Third-party libraries and data keep their own licenses. Review the license terms of `PyJHora`, `jyotishganit`, Swiss Ephemeris / ephemeris data, and any manuscript datasets before commercial distribution.

## Responsible Use

Use this project for research, product prototyping, education, and structured Jyotish/Nadi-style report generation. Do not use it to make medical, legal, financial, or life-critical decisions. Do not represent generated text as original Nadi palm leaf scripture.
