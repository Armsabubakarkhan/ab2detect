# AB2DETECT — REST API Reference

**Base URL:** `http://localhost:8000`

**Interactive docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Endpoints

### GET /health

Check backend status.

**Response**
```json
{
  "status": "ok",
  "model": "ModernBERT-base (simulated)",
  "version": "1.0.0"
}
```

---

### POST /detect

Run hallucination detection on a single sample.

**Request body**
```json
{
  "context": "Sachin Tendulkar scored 15,921 runs in 200 Test matches.",
  "question": "How many Test runs did Sachin Tendulkar score?",
  "answer": "Sachin Tendulkar scored 18,000 runs in 220 matches."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| context | string | yes | Retrieved passage |
| question | string | no | User question |
| answer | string | yes | LLM-generated answer to check |

**Response**
```json
{
  "is_hallucinated": true,
  "confidence": 0.86,
  "spans": ["18,000", "220"],
  "hall_rate": 0.0645,
  "token_count": 12,
  "hall_count": 2,
  "latency_ms": 148.3
}
```

| Field | Type | Description |
|---|---|---|
| is_hallucinated | bool | True if any hallucinated spans found |
| confidence | float | Detection confidence [0, 1] |
| spans | string[] | List of hallucinated span strings |
| hall_rate | float | hall_count / token_count |
| token_count | int | Total tokens in answer |
| hall_count | int | Number of hallucinated spans |
| latency_ms | float | Inference time in milliseconds |

**Error responses**
```json
{ "detail": "context and answer are required" }  // 400
```

---

### POST /detect/batch

Run detection on multiple samples at once.

**Request body**
```json
{
  "samples": [
    {
      "context": "...",
      "question": "...",
      "answer": "..."
    }
  ]
}
```

**Response**
```json
{
  "results": [...],
  "total": 5,
  "hallucinated_count": 3
}
```

---

## Python Usage

```python
import requests

response = requests.post("http://localhost:8000/detect", json={
    "context": "Australia won the 2023 ICC Cricket World Cup in Ahmedabad.",
    "question": "Who won the 2023 Cricket World Cup?",
    "answer": "India won the 2023 Cricket World Cup in Mumbai."
})

data = response.json()
print(f"Hallucinated: {data['is_hallucinated']}")
print(f"Spans: {data['spans']}")
print(f"Confidence: {data['confidence']:.2f}")
```

---

## LangChain Integration

```python
from langchain.schema import BaseOutputParser
import requests

class HallucinationOutputParser(BaseOutputParser):
    def parse(self, text: str) -> dict:
        # Call AB2DETECT before returning the answer
        result = requests.post("http://localhost:8000/detect", json={
            "context": self.context,
            "answer": text,
        }).json()
        
        if result["is_hallucinated"]:
            raise ValueError(f"Hallucination detected: {result['spans']}")
        return text
```
