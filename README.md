# Jyotish Nadi Template

**Jyotish Nadi Template** is an open-source template for building Vedic astrology / Jyotish reading systems with a Nadi-style chapter structure. It converts birth data into a structured Vedic chart, maps the chart into 16 common Kandam-style reading chapters, adds timing windows, evidence tags, quality scoring, and clear product boundaries.

> Important: this repository is **not** a collection of original Nadi palm leaf manuscripts, not a digitized Nadi leaf corpus, not an authenticated Agastya Nadi / Bhrigu Nadi text, and not a fingerprint-to-leaf matching system. It is a software template for **Nadi-style interpretation built on Vedic astrology calculations**.

中文：**Jyotish Nadi Template** 是一个开源的吠陀占星 / Jyotish 解读模板，用于把出生资料转成结构化吠陀盘面，并按公开常见的 16 个 Kandam 章节生成纳迪风格报告。它不是纳迪叶原文，不是真实叶片数据库，也不能宣称“已经找到某个人的真实纳迪叶”。

## SEO Keywords

Vedic astrology, Jyotish, Nadi astrology, Nadi Jyotisha, Naadi astrology, Agastya Nadi, Bhrigu Nadi, Kandam, palm leaf astrology, Vedic birth chart, Vimshottari Dasha, Nadi reading template, AI astrology, Codex skill, astrology report generator, 吠陀占星, 纳迪叶, 纳迪占星, 纳迪风格解读, 印度占星, 16 Kandam, 大运分运, 纳迪叶模板。

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

`Jyotish Nadi Template` 是一个“吠陀占星计算 + 纳迪风格章节报告”的开源模板。它适合用来开发：

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

## Quick Start

```bash
git clone https://github.com/<owner>/jyotish-nadi-template.git
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
