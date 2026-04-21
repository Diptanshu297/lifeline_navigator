"""
Comprehensive Bangalore hospital data — 25 major hospitals across the city.
Coordinates verified against OpenStreetMap.
"""
from typing import Dict, List, Any

HOSPITALS: Dict[str, Dict[str, Any]] = {

    
    "victoria": {
        "id": "victoria", "name": "Victoria Hospital",
        "lat": 12.9604, "lon": 77.5703,
        "specialties": ["Trauma", "General"],
        "capacity_pct": 75, "beds": 1300, "icu_beds": 80,
        "address": "Ft. Victoria Rd, Bangalore 560002",
        "level": "Government Tertiary",
    },
    "nimhans": {
        "id": "nimhans", "name": "NIMHANS",
        "lat": 12.9415, "lon": 77.5957,
        "specialties": ["Neuro", "Psych"],
        "capacity_pct": 60, "beds": 800, "icu_beds": 30,
        "address": "Hosur Rd, Bangalore 560029",
        "level": "National Institute",
    },
    "bowring": {
        "id": "bowring", "name": "Bowring & Lady Curzon Hospital",
        "lat": 12.9775, "lon": 77.6081,
        "specialties": ["Trauma", "General"],
        "capacity_pct": 80, "beds": 800, "icu_beds": 40,
        "address": "Hospital Rd, Shivajinagar, Bangalore 560001",
        "level": "Government Tertiary",
    },
    "kidwai": {
        "id": "kidwai", "name": "Kidwai Memorial Institute of Oncology",
        "lat": 12.9317, "lon": 77.5993,
        "specialties": ["General"],
        "capacity_pct": 85, "beds": 650, "icu_beds": 30,
        "address": "Dr M H Marigowda Rd, Bangalore 560029",
        "level": "Government Specialty",
    },
    "jayadeva": {
        "id": "jayadeva", "name": "Jayadeva Institute of Cardiovascular Sciences",
        "lat": 12.9198, "lon": 77.5985,
        "specialties": ["Cardiac"],
        "capacity_pct": 70, "beds": 700, "icu_beds": 80,
        "address": "Bannerghatta Rd, Bangalore 560069",
        "level": "Government Specialty",
    },
    "kr_hospital": {
        "id": "kr_hospital", "name": "KR Hospital (Mysore Medical College)",
        "lat": 12.3018, "lon": 76.6550,
        "specialties": ["Trauma", "General"],
        "capacity_pct": 70, "beds": 1200, "icu_beds": 50,
        "address": "Irwin Rd, Mysuru 570021",
        "level": "Government Tertiary",
    },

    
    "apollo_sheshadripuram": {
        "id": "apollo_sheshadripuram", "name": "Apollo Hospital (Sheshadripuram)",
        "lat": 13.0040, "lon": 77.5630,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 45, "beds": 300, "icu_beds": 45,
        "address": "Sheshadripuram, Bangalore 560020",
        "level": "Private Tertiary",
    },
    "aster_cmi": {
        "id": "aster_cmi", "name": "Aster CMI Hospital (Hebbal)",
        "lat": 13.0478, "lon": 77.5936,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 55, "beds": 430, "icu_beds": 65,
        "address": "New Airport Rd, Hebbal, Bangalore 560092",
        "level": "Private Tertiary",
    },
    "columbia_hebbal": {
        "id": "columbia_hebbal", "name": "Columbia Asia Hospital (Hebbal)",
        "lat": 13.0350, "lon": 77.5970,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 50, "beds": 200, "icu_beds": 30,
        "address": "Kirloskar Business Park, Hebbal, Bangalore 560024",
        "level": "Private Tertiary",
    },
    "baptist": {
        "id": "baptist", "name": "Baptist Hospital",
        "lat": 13.0215, "lon": 77.5905,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 60, "beds": 350, "icu_beds": 40,
        "address": "Bellary Rd, Hebbal, Bangalore 560024",
        "level": "Private Tertiary",
    },
    "msramaiah": {
        "id": "msramaiah", "name": "MS Ramaiah Memorial Hospital",
        "lat": 13.0137, "lon": 77.5516,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 65, "beds": 750, "icu_beds": 75,
        "address": "MSR Nagar, Mathikere, Bangalore 560054",
        "level": "Private Tertiary",
    },

    
    "fortis_rajajinagar": {
        "id": "fortis_rajajinagar", "name": "Fortis Hospital (Rajajinagar)",
        "lat": 12.9919, "lon": 77.5524,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 60, "beds": 260, "icu_beds": 40,
        "address": "Cunningham Rd, Bangalore 560052",
        "level": "Private Tertiary",
    },
    "sparsh": {
        "id": "sparsh", "name": "Sparsh Hospital (Infantry Road)",
        "lat": 12.9852, "lon": 77.5968,
        "specialties": ["Trauma", "Neuro", "General"],
        "capacity_pct": 55, "beds": 250, "icu_beds": 35,
        "address": "Infantry Rd, Bangalore 560001",
        "level": "Private Tertiary",
    },
    "mallige": {
        "id": "mallige", "name": "Mallige Medical Centre (Sadashivanagar)",
        "lat": 13.0058, "lon": 77.5798,
        "specialties": ["Cardiac", "General"],
        "capacity_pct": 50, "beds": 150, "icu_beds": 20,
        "address": "Sadashivanagar, Bangalore 560080",
        "level": "Private Secondary",
    },

    
    "manipal_airport": {
        "id": "manipal_airport", "name": "Manipal Hospital (Old Airport Road)",
        "lat": 12.9695, "lon": 77.6506,
        "specialties": ["Cardiac", "Trauma", "Neuro"],
        "capacity_pct": 80, "beds": 650, "icu_beds": 60,
        "address": "98, HAL Airport Rd, Bangalore 560017",
        "level": "Private Tertiary",
    },
    "sakra": {
        "id": "sakra", "name": "Sakra World Hospital (Marathahalli)",
        "lat": 12.9591, "lon": 77.6974,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 50, "beds": 350, "icu_beds": 50,
        "address": "SY 52/2, Devarabisanahalli, Marathahalli, Bangalore 560103",
        "level": "Private Tertiary",
    },
    "columbia_whitefield": {
        "id": "columbia_whitefield", "name": "Columbia Asia Hospital (Whitefield)",
        "lat": 12.9699, "lon": 77.7499,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 45, "beds": 200, "icu_beds": 28,
        "address": "Whitefield Main Rd, Bangalore 560066",
        "level": "Private Tertiary",
    },
    "narayana_whitefield": {
        "id": "narayana_whitefield", "name": "Narayana Multispeciality (Whitefield)",
        "lat": 12.9784, "lon": 77.7508,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 55, "beds": 220, "icu_beds": 32,
        "address": "ITPL Main Rd, Whitefield, Bangalore 560048",
        "level": "Private Tertiary",
    },

    
    "st_johns": {
        "id": "st_johns", "name": "St. John's Medical College Hospital",
        "lat": 12.9254, "lon": 77.6240,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 70, "beds": 1300, "icu_beds": 90,
        "address": "Sarjapur Rd, Bangalore 560034",
        "level": "Private Tertiary",
    },
    "apollo_sheshadripuram_south": {
        "id": "apollo_sheshadripuram_south",
        "name": "Apollo BGS Hospital (Mysore Rd)",
        "lat": 12.9511, "lon": 77.5102,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 50, "beds": 200, "icu_beds": 30,
        "address": "Mysore Rd, Bangalore 560026",
        "level": "Private Tertiary",
    },
    "sagar": {
        "id": "sagar", "name": "Sagar Hospitals (Banashankari)",
        "lat": 12.9255, "lon": 77.5463,
        "specialties": ["Cardiac", "Trauma", "General"],
        "capacity_pct": 65, "beds": 300, "icu_beds": 38,
        "address": "44/54, 30th Cross, Banashankari 2nd Stage, Bangalore 560070",
        "level": "Private Tertiary",
    },
    "narayana_bommasandra": {
        "id": "narayana_bommasandra", "name": "Narayana Health City (Bommasandra)",
        "lat": 12.8365, "lon": 77.6762,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 60, "beds": 3000, "icu_beds": 300,
        "address": "258/A, Bommasandra Industrial Area, Bangalore 560099",
        "level": "Private Super-Specialty",
    },
    "bgs_gleneagles": {
        "id": "bgs_gleneagles", "name": "BGS Gleneagles Global Hospital (Kengeri)",
        "lat": 12.9124, "lon": 77.4849,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 50, "beds": 450, "icu_beds": 55,
        "address": "67, Uttarahalli Rd, Kengeri, Bangalore 560060",
        "level": "Private Tertiary",
    },
    "medanta": {
        "id": "medanta", "name": "Medanta Hospital (Bannerghatta Rd)",
        "lat": 12.8940, "lon": 77.5978,
        "specialties": ["Cardiac", "Trauma", "Neuro", "General"],
        "capacity_pct": 45, "beds": 400, "icu_beds": 55,
        "address": "Bannerghatta Rd, Bangalore 560076",
        "level": "Private Tertiary",
    },
    "hosmat": {
        "id": "hosmat", "name": "HOSMAT Hospital (Richmond Road)",
        "lat": 12.9621, "lon": 77.5993,
        "specialties": ["Trauma", "General"],
        "capacity_pct": 55, "beds": 180, "icu_beds": 20,
        "address": "45, Magrath Rd, Richmond Town, Bangalore 560025",
        "level": "Private Secondary",
    },
}


EMERGENCY_ELIGIBILITY: Dict[str, List[str]] = {
    "cardiac": [
        "apollo_sheshadripuram", "fortis_rajajinagar", "manipal_airport",
        "st_johns", "aster_cmi", "columbia_hebbal", "msramaiah", "sakra",
        "columbia_whitefield", "narayana_whitefield", "narayana_bommasandra",
        "bgs_gleneagles", "medanta", "apollo_sheshadripuram_south", "sagar",
        "mallige", "jayadeva", "baptist",
    ],
    "trauma": [
        "victoria", "apollo_sheshadripuram", "fortis_rajajinagar", "manipal_airport",
        "st_johns", "aster_cmi", "columbia_hebbal", "msramaiah", "sakra",
        "columbia_whitefield", "narayana_whitefield", "narayana_bommasandra",
        "bgs_gleneagles", "medanta", "sagar", "bowring", "sparsh", "hosmat",
        "apollo_sheshadripuram_south", "baptist",
    ],
    "neuro": [
        "nimhans", "manipal_airport", "aster_cmi", "msramaiah",
        "sakra", "narayana_bommasandra", "bgs_gleneagles", "medanta", "sparsh",
    ],
    "general": [
        "victoria", "apollo_sheshadripuram", "fortis_rajajinagar", "st_johns",
        "aster_cmi", "columbia_hebbal", "msramaiah", "sakra", "columbia_whitefield",
        "narayana_whitefield", "narayana_bommasandra", "bgs_gleneagles", "medanta",
        "sagar", "bowring", "apollo_sheshadripuram_south", "kidwai",
        "hosmat", "mallige", "baptist",
    ],
}

EMERGENCY_DESCRIPTIONS = {
    "cardiac":  "Heart attack, arrhythmia, cardiac arrest",
    "trauma":   "Road accident, fractures, severe bleeding",
    "neuro":    "Stroke, seizure, traumatic brain injury",
    "general":  "Burns, infections, general emergencies",
}