"""Parser for Kilter Board layout strings and hold position lookups."""

import re
import sqlite3
from typing import Optional


# Role mappings for Kilter Board Original (product_id=1)
# Verified from placement_roles table in kilter.db
ROLE_MAP = {
    12: "start",
    13: "middle",
    14: "finish",
    15: "foot_only",
}

# Extended role maps for other products (same pattern, different IDs)
# product_id 2 (JUUL): 20-23, product_id 7 (Homewall): 42-45, etc.
ROLE_MAP_EXTENDED = {
    **{i: name for i, name in ROLE_MAP.items()},
    **{i: name for i, name in zip(range(20, 24), ["start", "middle", "finish", "foot_only"])},
    **{i: name for i, name in zip(range(24, 28), ["start", "middle", "finish", "foot_only"])},
    **{i: name for i, name in zip(range(28, 32), ["start", "middle", "finish", "foot_only"])},
    **{i: name for i, name in zip(range(32, 36), ["start", "middle", "finish", "foot_only"])},
    **{i: name for i, name in zip(range(42, 46), ["start", "middle", "finish", "foot_only"])},
}

# Tycho board has different role names (product_id=6, roles 36-41)
ROLE_MAP_EXTENDED.update({
    36: "cyan",
    37: "magenta",
    38: "yellow",
    39: "green",
    40: "red",
    41: "blue",
})

_LAYOUT_PATTERN = re.compile(r"p(\d+)r(\d+)")


def parse_layout(layout_string: str) -> list[dict]:
    """Parse a Kilter Board layout string into structured hold data.

    Layout strings use the format p{placement_id}r{role_id} concatenated.
    Example: "p1145r12p1149r13p1392r14" ->
        [
            {"placement_id": 1145, "role": "start", "role_code": 12},
            {"placement_id": 1149, "role": "middle", "role_code": 13},
            {"placement_id": 1392, "role": "finish", "role_code": 14},
        ]

    Args:
        layout_string: Raw layout string from climbs.frames column.

    Returns:
        List of dicts with placement_id, role (human-readable), and role_code.
    """
    holds = []
    for match in _LAYOUT_PATTERN.finditer(layout_string):
        placement_id = int(match.group(1))
        role_code = int(match.group(2))
        role = ROLE_MAP_EXTENDED.get(role_code, f"unknown_{role_code}")
        holds.append({
            "placement_id": placement_id,
            "role": role,
            "role_code": role_code,
        })
    return holds


def get_hold_positions(
    placement_ids: list[int],
    db_path: str,
) -> dict[int, dict]:
    """Look up x/y coordinates for placement IDs via placements → holes join.

    Args:
        placement_ids: List of placement IDs from parse_layout().
        db_path: Path to the kilter.db SQLite database.

    Returns:
        Dict mapping placement_id -> {"x": int, "y": int, "hole_id": int}.
    """
    if not placement_ids:
        return {}

    placeholders = ",".join("?" for _ in placement_ids)
    query = f"""
        SELECT p.id AS placement_id, p.hole_id, h.x, h.y
        FROM placements p
        JOIN holes h ON p.hole_id = h.id
        WHERE p.id IN ({placeholders})
    """

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(query, placement_ids)
        results = {}
        for row in cursor:
            results[row[0]] = {
                "hole_id": row[1],
                "x": row[2],
                "y": row[3],
            }
        return results
    finally:
        conn.close()


def get_climb_holds_with_positions(
    layout_string: str,
    db_path: str,
) -> list[dict]:
    """Parse layout and enrich with x/y positions. Convenience function.

    Returns:
        List of dicts with placement_id, role, role_code, x, y, hole_id.
    """
    holds = parse_layout(layout_string)
    placement_ids = [h["placement_id"] for h in holds]
    positions = get_hold_positions(placement_ids, db_path)

    for hold in holds:
        pos = positions.get(hold["placement_id"], {})
        hold["x"] = pos.get("x")
        hold["y"] = pos.get("y")
        hold["hole_id"] = pos.get("hole_id")

    return holds


def get_grade_name(difficulty: float, system: str = "boulder") -> Optional[str]:
    """Convert numeric difficulty to grade name.

    Args:
        difficulty: Numeric difficulty value (e.g., 20.0).
        system: "boulder" for V-scale or "route" for YDS.

    Returns:
        Grade string like "6c/V5" or None if not found.
    """
    # Hardcoded from difficulty_grades table (static, doesn't change)
    GRADES = {
        10: ("4a/V0", "5b/5.9"),
        11: ("4b/V0", "5c/5.10a"),
        12: ("4c/V0", "6a/5.10b"),
        13: ("5a/V1", "6a+/5.10c"),
        14: ("5b/V1", "6b/5.10d"),
        15: ("5c/V2", "6b+/5.11a"),
        16: ("6a/V3", "6c/5.11b"),
        17: ("6a+/V3", "6c+/5.11c"),
        18: ("6b/V4", "7a/5.11d"),
        19: ("6b+/V4", "7a+/5.12a"),
        20: ("6c/V5", "7b/5.12b"),
        21: ("6c+/V5", "7b+/5.12c"),
        22: ("7a/V6", "7c/5.12d"),
        23: ("7a+/V7", "7c+/5.13a"),
        24: ("7b/V8", "8a/5.13b"),
        25: ("7b+/V8", "8a+/5.13c"),
        26: ("7c/V9", "8b/5.13d"),
        27: ("7c+/V10", "8b+/5.14a"),
        28: ("8a/V11", "8c/5.14b"),
        29: ("8a+/V12", "8c+/5.14c"),
        30: ("8b/V13", "9a/5.14d"),
    }
    rounded = round(difficulty)
    grade = GRADES.get(rounded)
    if grade is None:
        return None
    return grade[0] if system == "boulder" else grade[1]
