"""Stat canonicalization based on YAML configuration.

This module loads sport-specific stat canonicalization rules from
config/stat_canonicalization_rules.yaml and exposes canonicalize_stat_type.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import re
import structlog
import yaml

logger = structlog.get_logger()


UNKNOWN_STAT = "UNKNOWN_STAT"


@dataclass
class CanonicalStatRule:
  canonical: str
  patterns: List[str]


@dataclass
class SportRules:
  clean_patterns: List[str]
  canonical_stats: List[CanonicalStatRule]


@dataclass
class CanonicalizationConfig:
  global_clean_patterns: List[str]
  sports: Dict[str, SportRules]


def _load_raw_config() -> dict:
  base_dir = Path(__file__).resolve().parents[1]  # Go from /processing/ to /kashrock-main/
  config_path = base_dir / "config" / "stat_canonicalization_rules.yaml"
  if not config_path.exists():
    logger.warning("Stat canonicalization config missing", path=str(config_path))
    return {}
  with config_path.open("r", encoding="utf-8") as f:
    return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_config() -> CanonicalizationConfig:
  raw = _load_raw_config()
  global_clean = raw.get("global_clean_patterns", []) or []
  sports: Dict[str, SportRules] = {}
  for sport_key, sport_cfg in raw.items():
    if sport_key == "global_clean_patterns":
      continue
    clean = sport_cfg.get("clean_patterns", []) or []
    canonical_stats_cfg = sport_cfg.get("canonical_stats", {}) or {}
    rules: List[CanonicalStatRule] = []
    for canonical_name, rule_cfg in canonical_stats_cfg.items():
      patterns = rule_cfg.get("patterns", []) or []
      # Preserve ordering: most specific first
      rules.append(CanonicalStatRule(canonical=canonical_name, patterns=patterns))
    sports[sport_key.upper()] = SportRules(clean_patterns=clean, canonical_stats=rules)
  
  return CanonicalizationConfig(global_clean_patterns=global_clean, sports=sports)


def _normalize_sport(sport: str) -> str:
  if not sport:
    return ""
  s = sport.lower()
  if "nba" in s or "basketball" in s:
    return "nba"
  if "nfl" in s or ("football" in s and "college" not in s):
    return "nfl"
  if "mlb" in s or "baseball" in s or "cbb" in s:
    return "mlb"
  if "nhl" in s or ("hockey" in s):
    return "nhl"
  if "soccer" in s or "football_soc" in s or "futbol" in s:
    return "soccer"
  return s


def _apply_clean_patterns(value: str, patterns: List[str]) -> str:
  cleaned = value
  for pat in patterns:
    if not pat:
      continue
    cleaned = cleaned.replace(pat.lower(), "")
  return cleaned.strip()


def _strip_player_name_from_stat(raw_stat: str, player_name: Optional[str] = None) -> str:
  """Remove player name prefix from stat type if present.
  
  Handles formats like:
  - "Aaron Rodgers - Passing Yds" -> "Passing Yds"
  - "Lamar Jackson: Interception" -> "Interception"
  - "Player Name - Stat" -> "Stat"
  """
  if not player_name:
    return raw_stat
  
  stat_lower = raw_stat.lower()
  name_lower = player_name.lower()
  
  # Try to match "Player Name - Stat" or "Player Name: Stat" or "Player Name Stat"
  patterns = [
    rf"^{re.escape(name_lower)}\s*-\s*",  # "Name - Stat"
    rf"^{re.escape(name_lower)}\s*:\s*",  # "Name: Stat"
    rf"^{re.escape(name_lower)}\s+",      # "Name Stat"
  ]
  
  for pattern in patterns:
    match = re.match(pattern, stat_lower, re.IGNORECASE)
    if match:
      # Remove the matched prefix from original string (preserving case)
      return raw_stat[match.end():].strip()
  
  return raw_stat


def _preprocess_raw_stat(raw_stat: str, sport: str, cfg: CanonicalizationConfig, player_name: Optional[str] = None) -> (str, Optional[SportRules]):
  # Strip player name prefix if present (must happen before other normalization)
  if player_name:
    raw_stat = _strip_player_name_from_stat(raw_stat, player_name)
  
  normalized = raw_stat.strip().lower()
  if not normalized:
    return "", None

  # normalize whitespace and plus signs
  normalized = re.sub(r"\s+", " ", normalized)
  normalized = normalized.replace(" +", "+").replace("+ ", "+").replace(" + ", "+")

  # apply global and sport-specific clean patterns
  normalized = _apply_clean_patterns(normalized, [p.lower() for p in cfg.global_clean_patterns])
  sport_key = _normalize_sport(sport)
  sport_rules = cfg.sports.get(sport_key.upper()) if sport_key else None

  if sport_rules:
    normalized = _apply_clean_patterns(normalized, [p.lower() for p in sport_rules.clean_patterns])

  return normalized, sport_rules


def _matches_pattern(stat: str, pattern: str) -> bool:
  """Return True if stat matches the given pattern.

  Rules:
  - If pattern starts with "re:", treat the rest as a regex (case-insensitive).
  - Otherwise, require stat to contain pattern as a substring (case-insensitive).
  """
  if not pattern:
    return False
  if pattern.startswith("re:"):
    expr = pattern[3:]
    try:
      return re.search(expr, stat, flags=re.IGNORECASE) is not None
    except re.error:
      logger.debug("Invalid regex pattern in stat canonicalization", pattern=pattern)
      return False
  # substring match (already lowercased upstream)
  return pattern.lower() in stat


def canonicalize_stat_type(raw_stat: str, sport: str = "", player_name: Optional[str] = None) -> str:
  """Canonicalize a stat type to a sport-specific canonical ID.

  Returns a string like "NBA_POINTS", "NFL_PASSING_YARDS", etc., or
  UNKNOWN_STAT if no rule matches.
  
  Args:
    raw_stat: Raw stat string from source
    sport: Sport key for context
    player_name: Player name to strip from stat if present (e.g., "Aaron Rodgers - Passing Yds")
  """
  if not raw_stat or not isinstance(raw_stat, str):
    return "" if raw_stat is None else raw_stat

  cfg = load_config()
  normalized, sport_rules = _preprocess_raw_stat(raw_stat, sport, cfg, player_name)
  if not normalized:
    return ""

  normalized_sport = _normalize_sport(sport)

  # If sport is known, try sport-specific rules first
  if sport_rules:
    logger.debug("Trying sport-specific rules", sport=normalized_sport)
    for rule in sport_rules.canonical_stats:
      for pat in rule.patterns:
        if _matches_pattern(normalized, pat):
          logger.debug(
            "Stat type matched via YAML rule",
            raw=raw_stat,
            sport=normalized_sport.upper() if normalized_sport else "",
            canonical=rule.canonical,
            pattern=pat,
          )
          return rule.canonical



  logger.warning(
    "Unknown stat type after YAML canonicalization",
    raw_stat=raw_stat,
    sport=normalized_sport,
  )
  return UNKNOWN_STAT
