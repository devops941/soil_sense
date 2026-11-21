"""Madurai District geographical definitions, boundaries, and validation constants.

SoilSense is strictly scoped to Madurai District, Tamil Nadu, India.
All records must have district = 'Madurai'.
"""

from __future__ import annotations

from typing import List, Optional

TARGET_DISTRICT: str = "Madurai"
TARGET_STATE: str = "Tamil Nadu"
TARGET_COUNTRY: str = "India"

# Official 13 Community Development Blocks and 11 Revenue Taluks of Madurai District
MADURAI_BLOCKS: List[str] = [
    "Madurai East",
    "Madurai West",
    "Melur",
    "Vadipatti",
    "Usilampatti",
    "Thirumangalam",
    "Thirupparankundram",
    "Peraiyur",
    "Sedapatti",
    "Kottampatti",
    "Alanganallur",
    "Chellampatti",
    "T.Kallupatti",
]

MADURAI_TALUKS: List[str] = [
    "Madurai East",
    "Madurai West",
    "Madurai North",
    "Madurai South",
    "Melur",
    "Vadipatti",
    "Usilampatti",
    "Thirumangalam",
    "Thirupparankundram",
    "Peraiyur",
    "Kalligudi",
]


def is_valid_madurai_district(district: Optional[str]) -> bool:
    """Return True if the district string corresponds to Madurai."""
    if not district:
        return False
    return district.strip().lower() == "madurai"


def normalize_location_name(name: Optional[str]) -> str:
    """Normalize whitespace and capitalization for location names."""
    if not name:
        return ""
    return " ".join(name.strip().split())
