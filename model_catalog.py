
import copy
from typing import Dict, Any

_MODELS = {
    "utaut": {
        "description": "Unified Theory of Acceptance and Use of Technology",
        "config": {
            "sample_size": 400,
            "latents": {
                "PerfExpectancy": ["pe1", "pe2", "pe3", "pe4"],
                "EffortExpectancy": ["ee1", "ee2", "ee3", "ee4"],
                "SocialInfluence": ["si1", "si2", "si3"],
                "FacilitatingCond": ["fc1", "fc2", "fc3"],
                "BehIntention": ["bi1", "bi2", "bi3"],
                "UseBehavior": ["use1", "use2", "use3"]
            },
            "observed": ["Age", "Gender", "Experience", "Voluntariness"],
            "paths": [
                # Core UTAUT
                "PerfExpectancy -> BehIntention (sig)",
                "EffortExpectancy -> BehIntention (sig)",
                "SocialInfluence -> BehIntention (sig)",
                "FacilitatingCond -> UseBehavior (sig)",
                "BehIntention -> UseBehavior (sig)",
                # Moderators (simplified as direct effects/controls for this mock)
                "Age -> BehIntention (ns)",
                "Gender -> BehIntention (ns)"
            ],
            "controls": []
        }
    },
    "tpb": {
        "description": "Theory of Planned Behavior",
        "config": {
            "sample_size": 300,
            "latents": {
                "Attitude": ["att1", "att2", "att3", "att4"],
                "SubjectiveNorm": ["sn1", "sn2", "sn3"],
                "PBC": ["pbc1", "pbc2", "pbc3"],
                "Intention": ["int1", "int2", "int3"],
                "Behavior": ["beh1", "beh2"]
            },
            "paths": [
                "Attitude -> Intention (sig)",
                "SubjectiveNorm -> Intention (sig)",
                "PBC -> Intention (sig)",
                "PBC -> Behavior (sig)",
                "Intention -> Behavior (sig)"
            ]
        }
    },
    "tam2": {
        "description": "Technology Acceptance Model 2",
        "config": {
            "sample_size": 400,
            "latents": {
                "SubjectiveNorm": ["sn1", "sn2"],
                "Image": ["img1", "img2", "img3"],
                "JobRelevance": ["jr1", "jr2", "jr3"],
                "OutputQuality": ["oq1", "oq2"],
                "ResultDem": ["rd1", "rd2"],
                "PU": ["pu1", "pu2", "pu3", "pu4"],
                "PEU": ["peu1", "peu2", "peu3"],
                "Intention": ["bi1", "bi2", "bi3"],
                "Usage": ["use1", "use2"]
            },
            "paths": [
                "SubjectiveNorm -> PU (sig)",
                "Image -> PU (sig)",
                "JobRelevance -> PU (sig)",
                "OutputQuality -> PU (sig)",
                "ResultDem -> PU (sig)",
                "PEU -> PU (sig)",
                "PU -> Intention (sig)",
                "PEU -> Intention (sig)",
                "Intention -> Usage (sig)",
                "SubjectiveNorm -> Image (sig)"
            ],
            "controls": ["Experience", "Voluntariness"]
        }
    }
}

def list_models() -> Dict[str, str]:
    return {k: v["description"] for k, v in _MODELS.items()}

def get_model_config(name: str) -> Dict[str, Any]:
    config = _MODELS.get(name, {}).get("config")
    return copy.deepcopy(config) if config is not None else None
