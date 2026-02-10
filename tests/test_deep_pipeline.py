"""Tests for terminal.deep_pipeline — Deep analysis file-based pipeline."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Optional, Any, List

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestResearchDir:
    """Test that company_db creates research subdir."""

    def test_get_company_dir_creates_research(self, tmp_path):
        with patch("terminal.company_db._COMPANIES_DIR", tmp_path):
            from terminal.company_db import get_company_dir

            d = get_company_dir("TEST")
            assert (d / "research").is_dir()
