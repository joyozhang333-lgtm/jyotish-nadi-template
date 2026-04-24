# request.json 契约

```json
{
  "birth": {
    "date": "2000-01-01",
    "time": "12:00:00",
    "timezone": "Asia/Kolkata",
    "location": "Chennai, India"
  },
  "question": "我更适合创业还是稳定职业路线？",
  "requested_chapters": [1, 10, 12],
  "requested_theme_packs": ["career", "wealth"],
  "fingerprint_image_path": null
}
```

## 说明

- `requested_chapters` 为可选；为空时，系统走默认高频章节策略
- `requested_theme_packs` 当前支持：
  - `career`
  - `wealth`
  - `spirituality`
- `fingerprint_image_path` 为可选输入，只用于探索性分析
