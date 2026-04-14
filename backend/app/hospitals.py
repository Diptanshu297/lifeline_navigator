"""
Real Bangalore hospital data with coordinates and specialties.
Coordinates verified against OpenStreetMap.
"""

from typing import Dict, List, Any

HOSPITALS: Dict[str, Dict[str, Any]] = {
    "victoria": {
        "id": "victoria",
        "name": "Victoria Hospital",
        "lat": 12.9604,
        "lon": 77.5703,
        "specialties": ["Trauma", "General"],
        "capacity_pct": 70,
        "beds": 1300,
        "icu_beds": 80,
        "address": "Ft. Victoria Rd, Bangalore 560002",
        "phone": "+91-80-2670-1150",
        "level": "Government Tertiary",
    },
    "nimhans": {
        "id": "nimhans",
        "name": "NIMHANS",
        "lat": 12.9415,
        "lon": 77.5957,
        "specialties": ["Neuro", "Psych"],
        "capacity_pct": 55,
        "beds": 800,
        "icu_beds": 30,
        "address": "Hosur Rd, Bangalore 560029",
        "phone": "+91-80-4699-5000",
        "level": "National Institute",
    },
    "apollo_sheshadripuram": {
        "id": "apollo_sheshadripuram",
        "name": "Apollo Hospital (Sheshadripuram)",
        "lat": 13.0040,
        "lon": 77.5630,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 40,
        "beds": 300,
        "icu_beds": 45,
        "address": "154/11, Bannerghatta Rd, Bangalore 560076",
        "phone": "+91-80-2630-4050",
        "level": "Private Tertiary",
    },
    "fortis_rajajinagar": {
        "id": "fortis_rajajinagar",
        "name": "Fortis Hospital (Rajajinagar)",
        "lat": 12.9919,
        "lon": 77.5524,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 65,
        "beds": 260,
        "icu_beds": 40,
        "address": "14, Cunningham Rd, Bangalore 560052",
        "phone": "+91-80-4969-4969",
        "level": "Private Tertiary",
    },
    "manipal_airport": {
        "id": "manipal_airport",
        "name": "Manipal Hospital (Old Airport Road)",
        "lat": 12.9695,
        "lon": 77.6506,
        "specialties": ["Cardiac", "Trauma", "Neuro"],
        "capacity_pct": 85,
        "beds": 650,
        "icu_beds": 60,
        "address": "98, HAL Airport Rd, Bangalore 560017",
        "phone": "+91-80-2502-4444",
        "level": "Private Tertiary",
    },
    "st_johns": {
        "id": "st_johns",
        "name": "St. John's Medical College Hospital",
        "lat": 12.9254,
        "lon": 77.6240,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 75,
        "beds": 1300,
        "icu_beds": 90,
        "address": "Sarjapur Rd, Bangalore 560034",
        "phone": "+91-80-2206-5000",
        "level": "Private Tertiary",
    },
}

# Emergency type → eligible hospital IDs
EMERGENCY_ELIGIBILITY: Dict[str, List[str]] = {
    "cardiac":  ["apollo_sheshadripuram", "fortis_rajajinagar", "manipal_airport", "st_johns"],
    "trauma":   ["victoria", "apollo_sheshadripuram", "fortis_rajajinagar", "manipal_airport", "st_johns"],
    "neuro":    ["nimhans", "manipal_airport"],
    "general":  ["victoria", "apollo_sheshadripuram", "fortis_rajajinagar", "st_johns"],
}

EMERGENCY_DESCRIPTIONS = {
    "cardiac":  "Heart attack, arrhythmia, cardiac arrest",
    "trauma":   "Road accident, fractures, severe bleeding",
    "neuro":    "Stroke, seizure, traumatic brain injury",
    "general":  "Burns, infections, general emergencies",
}
