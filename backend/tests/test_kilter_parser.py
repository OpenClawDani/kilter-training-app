"""Tests for Kilter Board layout parser and hold position lookup."""

import os
import pytest

from app.utils.kilter_parser import (
    ROLE_MAP,
    ROLE_MAP_EXTENDED,
    get_climb_holds_with_positions,
    get_grade_name,
    get_hold_positions,
    parse_layout,
)

# Real layout string from a JustinKo climb in the DB
SAMPLE_LAYOUT = "p1113r12p1129r12p1165r13p1200r13p1218r13p1283r13p1322r13p1387r14p1456r15p1467r15p1494r15p1513r15p1542r15"

# Path to the downloaded Kilter Board database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "kilter.db")


class TestParseLayout:
    def test_basic_parsing(self):
        result = parse_layout("p1145r12p1149r13p1392r14")
        assert len(result) == 3
        assert result[0] == {"placement_id": 1145, "role": "start", "role_code": 12}
        assert result[1] == {"placement_id": 1149, "role": "middle", "role_code": 13}
        assert result[2] == {"placement_id": 1392, "role": "finish", "role_code": 14}

    def test_foot_only_role(self):
        result = parse_layout("p1456r15")
        assert result[0]["role"] == "foot_only"
        assert result[0]["role_code"] == 15

    def test_real_climb_layout(self):
        result = parse_layout(SAMPLE_LAYOUT)
        assert len(result) == 13
        # Two start holds
        starts = [h for h in result if h["role"] == "start"]
        assert len(starts) == 2
        # One finish hold
        finishes = [h for h in result if h["role"] == "finish"]
        assert len(finishes) == 1
        assert finishes[0]["placement_id"] == 1387
        # Multiple middle holds
        middles = [h for h in result if h["role"] == "middle"]
        assert len(middles) == 5
        # Foot only holds
        feet = [h for h in result if h["role"] == "foot_only"]
        assert len(feet) == 5

    def test_empty_string(self):
        assert parse_layout("") == []

    def test_all_kilter_role_codes_mapped(self):
        """All role codes for Kilter Board Original (product_id=1) are handled."""
        for code in [12, 13, 14, 15]:
            assert code in ROLE_MAP
            assert not ROLE_MAP[code].startswith("unknown")

    def test_all_role_codes_in_extended_map(self):
        """All known role codes across all products are in the extended map."""
        # Product 1 (Kilter Original): 12-15
        # Product 2 (JUUL): 20-23
        # Product 7 (Homewall): 42-45
        for code in [12, 13, 14, 15, 20, 21, 22, 23, 42, 43, 44, 45]:
            assert code in ROLE_MAP_EXTENDED

    def test_unknown_role_code(self):
        result = parse_layout("p100r99")
        assert result[0]["role"] == "unknown_99"


@pytest.mark.skipif(
    not os.path.exists(DB_PATH),
    reason="Kilter DB not downloaded (run: boardlib database kilter backend/data/kilter.db)",
)
class TestHoldPositions:
    def test_lookup_known_placements(self):
        # Verified values from kilter.db:
        # placement 1113 -> hole 1348 (56, 24)
        # placement 1129 -> hole 1343 (48, 32)
        positions = get_hold_positions([1113, 1129], DB_PATH)
        assert 1113 in positions
        assert positions[1113] == {"hole_id": 1348, "x": 56, "y": 24}
        assert 1129 in positions
        assert positions[1129] == {"hole_id": 1343, "x": 48, "y": 32}

    def test_empty_list(self):
        assert get_hold_positions([], DB_PATH) == {}

    def test_nonexistent_placement(self):
        positions = get_hold_positions([9999999], DB_PATH)
        assert 9999999 not in positions

    def test_full_climb_positions(self):
        holds = get_climb_holds_with_positions(SAMPLE_LAYOUT, DB_PATH)
        assert len(holds) == 13
        # All holds should have positions (they're from a real climb)
        for hold in holds:
            assert hold["x"] is not None, f"placement {hold['placement_id']} missing x"
            assert hold["y"] is not None, f"placement {hold['placement_id']} missing y"
            assert hold["hole_id"] is not None

    def test_finish_hold_position(self):
        """Finish hold (placement 1387) should be at top of board (high y)."""
        holds = get_climb_holds_with_positions(SAMPLE_LAYOUT, DB_PATH)
        finish = [h for h in holds if h["role"] == "finish"][0]
        assert finish["placement_id"] == 1387
        assert finish["x"] == 72
        assert finish["y"] == 152


class TestGradeName:
    def test_v5(self):
        assert get_grade_name(20.0) == "6c/V5"

    def test_v3(self):
        assert get_grade_name(16.0) == "6a/V3"

    def test_route_system(self):
        assert get_grade_name(20.0, system="route") == "7b/5.12b"

    def test_fractional_rounds(self):
        assert get_grade_name(15.9964) == "6a/V3"

    def test_out_of_range(self):
        assert get_grade_name(1.0) is None
        assert get_grade_name(50.0) is None
