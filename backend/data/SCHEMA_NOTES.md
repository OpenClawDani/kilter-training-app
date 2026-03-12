# Kilter Board Database — Schema Notes
> Source: BoardLib v0.14.1 — `boardlib database kilter data/kilter.db`
> Downloaded: March 2026 — 189MB, 344k+ climbs

---

## Tables Overview

| Table | Rows | Purpose |
|-------|------|---------|
| climbs | 344,504 | All climb problems (name, setter, layout, edges) |
| climb_stats | 348,028 | Per-angle stats (difficulty, ascents, quality) |
| climb_cache_fields | 208,457 | Aggregated cache (total ascents, avg difficulty across angles) |
| difficulty_grades | 39 | Grade lookup (difficulty number → V-scale / Font / YDS) |
| placements | 3,773 | Maps placement_id → hole_id for each layout |
| holes | 3,294 | Physical hole positions (x, y coords) on the board |
| leds | 7,828 | LED position per hole (for BLE commands) |
| placement_roles | 30 | Role definitions (start/middle/finish/foot) per product |
| beta_links | 32,139 | Instagram video links per climb |
| layouts | 8 | Board layout definitions |
| products | 7 | Board products (Kilter Original, Homewall, JUUL, etc.) |
| products_angles | 56 | Valid wall angles per product |
| sets | 11 | Hold sets (different hold generations) |
| kits | 100 | Hold kits (retail packages) |
| circuits | 0 | User-created circuits (empty — requires auth sync) |
| ascents | 0 | User ascent log (empty — requires auth sync) |
| users | 0 | User profiles (empty — requires auth sync) |

---

## Key Relationships

```
climbs.frames → contains p{placement_id}r{role_code} layout string
    ↓ parse
placement_id → placements.id
    ↓
placements.hole_id → holes.id → (x, y) coordinates
placements.set_id → sets.id (which hold set)
    ↓
role_code → placement_roles.id → role name (start/middle/finish/foot_only)

climbs.uuid → climb_stats.climb_uuid + climb_stats.angle
    ↓
climb_stats.display_difficulty → difficulty_grades.difficulty → boulder_name / route_name

climbs.uuid → beta_links.climb_uuid → Instagram video URL
```

---

## Role Code Mappings (Verified)

From `placement_roles` table. Each product has its own set of role IDs but same pattern:

### Kilter Board Original (product_id=1, layout_id=1)
| role_code | name | full_name | LED color | Meaning |
|-----------|------|-----------|-----------|---------|
| 12 | start | Start | #00FF00 (green) | Starting holds — must match both hands |
| 13 | middle | Middle | #00FFFF (cyan) | Intermediate holds |
| 14 | finish | Finish | #FF00FF (magenta) | Top-out hold(s) |
| 15 | foot | Foot Only | #FFA500 (orange) | Feet only, no hands |

### Kilter Board Homewall (product_id=7)
Same pattern: 42=start, 43=middle, 44=finish, 45=foot_only

### Tycho (product_id=6) — Different system!
Uses color names: 36=cyan, 37=magenta, 38=yellow, 39=green, 40=red, 41=blue

---

## Grade System

The `difficulty_grades` table maps a numeric `difficulty` (1-39) to both boulder and route names:

| difficulty | boulder_name | route_name | Listed? |
|-----------|-------------|------------|---------|
| 10 | 4a/V0 | 5b/5.9 | Yes |
| 13 | 5a/V1 | 6a+/5.10c | Yes |
| 15 | 5c/V2 | 6b+/5.11a | Yes |
| 16 | 6a/V3 | 6c/5.11b | Yes |
| 18 | 6b/V4 | 7a/5.11d | Yes |
| 20 | 6c/V5 | 7b/5.12b | Yes |
| 22 | 7a/V6 | 7c/5.12d | Yes |
| 24 | 7b/V8 | 8a/5.13b | Yes |
| 26 | 7c/V9 | 8b/5.13d | Yes |

Grades 1-9 and 34+ are `is_listed = 0` (not shown in filters).

`climb_stats.display_difficulty` is a float (community consensus average). Round to nearest int for grade lookup. Some climbs have fractional difficulties like 15.9964 ≈ V3.

**Important:** Grades are per-angle! A climb at 40° might be V5 but at 50° it's V7. The `climb_stats` table has a composite key `(climb_uuid, angle)`.

---

## Layout String Format

Stored in `climbs.frames` column. Format: concatenated `p{placement_id}r{role_code}` pairs.

Example: `p1113r12p1129r12p1165r13p1200r13p1218r13p1283r13p1322r13p1387r14p1456r15p1467r15p1494r15p1513r15p1542r15`

Parsed:
- 2 start holds (r12): placements 1113, 1129
- 5 middle holds (r13): placements 1165, 1200, 1218, 1283, 1322
- 1 finish hold (r14): placement 1387
- 5 foot-only holds (r15): placements 1456, 1467, 1494, 1513, 1542

**Note:** The IDs in the layout are `placement` IDs (not `hole` IDs). Join through `placements` table to get `hole_id`, then `holes` for x/y coordinates.

---

## Angles

- `climbs.angle` is almost always NULL — ignore this column
- Actual angles come from `climb_stats.angle` (one climb can have stats at multiple angles)
- Valid angles per product are in `products_angles` table
- Most popular angle for Kilter Board Original: 40°

---

## Beta Video Links

Stored in `beta_links` table (32,139 links):
- `climb_uuid` → foreign key to climbs
- `link` → Instagram URL (e.g., `https://www.instagram.com/p/CYeDgWJIJac/`)
- `angle` → wall angle when video was recorded (often NULL)
- `foreign_username` → Instagram username
- `thumbnail` → kilterboardapp.com hosted thumbnail

**Limitation:** All links are Instagram. No YouTube links in the DB. Instagram video downloads are unreliable/ToS-violating, so these are mainly useful for linking out, not for automated comparison.

---

## Useful Queries for Search API

```sql
-- Search climbs by name (autocomplete)
SELECT c.uuid, c.name, c.setter_username, c.layout_id,
       cs.angle, cs.display_difficulty, cs.ascensionist_count, cs.quality_average,
       dg.boulder_name
FROM climbs c
JOIN climb_stats cs ON c.uuid = cs.climb_uuid
JOIN difficulty_grades dg ON CAST(ROUND(cs.display_difficulty) AS INT) = dg.difficulty
WHERE c.name LIKE '%search_term%'
  AND c.layout_id = 1  -- Kilter Board Original
  AND c.is_listed = 1
  AND cs.ascensionist_count > 0
ORDER BY cs.ascensionist_count DESC
LIMIT 10;

-- Get full climb detail with hold positions
SELECT c.uuid, c.name, c.frames, c.setter_username,
       cs.angle, cs.display_difficulty, cs.ascensionist_count, cs.quality_average,
       dg.boulder_name
FROM climbs c
JOIN climb_stats cs ON c.uuid = cs.climb_uuid
JOIN difficulty_grades dg ON CAST(ROUND(cs.display_difficulty) AS INT) = dg.difficulty
WHERE c.uuid = ?;

-- Get beta links for a climb
SELECT link, foreign_username, angle, thumbnail
FROM beta_links
WHERE climb_uuid = ? AND is_listed = 1;

-- Most popular climbs at a specific angle
SELECT c.name, dg.boulder_name, cs.ascensionist_count
FROM climbs c
JOIN climb_stats cs ON c.uuid = cs.climb_uuid
JOIN difficulty_grades dg ON CAST(ROUND(cs.display_difficulty) AS INT) = dg.difficulty
WHERE cs.angle = 40 AND c.layout_id = 1
ORDER BY cs.ascensionist_count DESC
LIMIT 20;
```

---

## Surprises / Notable Findings

1. **189MB database** — larger than expected (RESEARCH.md said ~85MB). Likely grew with more climbs.
2. **climb_stats is per-angle** — same climb UUID appears multiple times with different angles and difficulties. This is critical for search/filter.
3. **Layout uses placement IDs, not hole IDs** — the `p` values in the layout string are `placements.id`, not `holes.id`. Must join through placements to get coordinates.
4. **32k+ beta links** — all Instagram, no YouTube. Good for display but not for automated video comparison.
5. **No user data without auth** — ascents, circuits, users tables are empty. BoardLib needs username/password to sync personal data.
6. **`climb_cache_fields`** has aggregated stats across all angles — useful for overall popularity sorting without specifying an angle.
7. **`is_listed` flag** on climbs — many climbs are unlisted (drafts). Filter with `is_listed = 1` for public climbs.
8. **LED colors are orange (#FFA500) for foot holds** — RESEARCH.md said yellow, but the actual DB shows orange.
