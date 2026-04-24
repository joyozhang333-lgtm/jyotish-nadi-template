# chart.json 契约

```json
{
  "input_quality": {
    "birth_time_precision": "minute|hour|day",
    "location_precision": "exact|city|timezone_only",
    "warnings": []
  },
  "birth": {
    "date": "2000-01-01",
    "time": "12:00:00",
    "timezone": "Asia/Kolkata",
    "location": "Chennai, India"
  },
  "chart_summary": {
    "lagna": "",
    "moon_sign": "",
    "nakshatra": "",
    "pada": 0
  },
  "planets": [],
  "dashas": [],
  "source_engine": "pyjhora"
}
```

## 说明

- 这是 skill 与 engine 之间的最小稳定边界
- 任何底层引擎都先转成这个结构，再给解释层消费
