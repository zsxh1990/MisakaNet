---
{
  "title": "Freshness Decay Model: protection period + tiered rates + boost signals",
  "domain": "architecture",
  "tags": ["freshness", "decay", "quality", "knowledge-base", "scoring"],
  "status": "published",
  "evidence_level": "E2",
  "source": "pr-1262",
  "created": "2026-08-23"
}
---

## Problem

Knowledge base entries never lose value over time — a 2-year-old lesson about a deprecated API scores the same as a fresh one. No mechanism to automatically deprioritize outdated content.

## Solution

Implement a freshness decay model with three key components:

### 1. Protection Period

No decay for the first N days after merge (default: 14 days). This prevents premature deprioritization of new content.

```python
if days_since_merge <= protection_days:
    return {"score": base_score, "protected": True}
```

### 2. Tiered Decay Rates

Two-speed decay to prevent rapid degradation:

- **Normal decay**: 1.0 points/day above threshold (50)
- **Slow decay**: 0.5 points/day below threshold

```python
if score > slow_threshold:
    # Normal decay until threshold
    days_at_normal = (score - slow_threshold) / decay_rate
    decay_points += days_at_normal * decay_rate
    # Slow decay for remaining days
    remaining_days = decay_days - days_at_normal
    decay_points += remaining_days * slow_decay_rate
else:
    # Already below threshold
    decay_points = decay_days * slow_decay_rate
```

### 3. Boost Signals

Events that reset or boost freshness:

| Signal | Boost | Use Case |
|--------|-------|----------|
| `was_used` | +5 | Lesson used in evaluation |
| `helpful_vote` | +3 | User marked helpful |
| `maintainer_edit` | +10 | Updated by maintainer |
| `pinned` | 100 | Pinned by maintainer (exempt) |

### 4. Freshness Tiers

| Tier | Score | Badge | Action |
|------|-------|-------|--------|
| Fresh | ≥80 | 🟢 | Default display |
| Stable | ≥60 | 🔵 | Normal |
| Aging | ≥40 | 🟡 | Show warning |
| Stale | ≥20 | 🟠 | Deprioritize |
| Outdated | <20 | 🔴 | Auto-flag |

## Key Points

- Protection period prevents premature decay of new content
- Two-speed decay (fast then slow) creates natural floor
- Boost signals reward active/useful content
- Pinned items are exempt from decay
- Score never goes below 0 or above 100
- Tier badges provide quick visual classification

## Integration Points

- **Search API**: Return freshness badge in results
- **Quality scorer**: Add freshness as weighted dimension (10%)
- **CI cron**: Nightly recalculation for all lessons
- **Demand board**: Show stale lessons needing review

## Verification

```python
from freshness import compute_freshness

# New lesson — full score, protected
result = compute_freshness({"created": "2026-08-23"}, today=datetime(2026, 8, 23))
assert result["score"] == 100
assert result["protected"] is True

# Old lesson — decayed
result = compute_freshness({"provenance": {"merged_at": "2026-06-01"}}, today=datetime(2026, 8, 23))
assert result["score"] < 80
assert result["tier"]["tier"] in ("stable", "aging", "stale", "outdated")
```
