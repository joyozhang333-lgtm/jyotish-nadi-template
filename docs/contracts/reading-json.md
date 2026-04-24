# reading.json 契约

```json
{
  "requested_chapters": [1, 7, 10],
  "requested_theme_packs": ["career", "wealth"],
  "chart_summary": {},
  "identity_checks": [
    {
      "question": "",
      "reason": "",
      "evidence_tag": "classical_rule"
    }
  ],
  "kandam_reading": [
    {
      "kandam": 1,
      "title": "",
      "summary": "",
      "claims": [
        {
          "text": "",
          "evidence_tag": "interpretive_mapping"
        }
      ]
    }
  ],
  "theme_sections": [
    {
      "theme": "career",
      "summary": "",
      "claims": [
        {
          "text": "",
          "evidence_tag": "interpretive_mapping"
        }
      ]
    }
  ],
  "timing_windows": [],
  "remedy_candidates": [],
  "missing_capabilities": []
}
```

## 说明

- 所有对用户可见的文本结论，都必须进入 `claims`
- 每条 claim 必须有 `evidence_tag`
- `requested_chapters` 用来支持章节选择型产品
- `requested_theme_packs` 用来支持事业 / 财富 / 灵性等专题包
