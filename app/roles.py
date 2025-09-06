from pydantic import BaseModel
from typing import Optional, Dict, List

class Roles(BaseModel):
    time: Optional[str] = None
    metric: str
    category: Optional[str] = None
    id: Optional[str] = None
    normalize_by: Optional[str] = None

def guess_roles(columns: List[str]) -> Dict[str, str]:
    cols_lower = {c.lower(): c for c in columns}
    out = {}
    for key, candidates in {
        "time": ["date","time","timestamp","published","created","start"],
        "metric": ["subscriber","subs","value","amount","revenue","score","count","metric"],
        "category": ["category","segment","type","dept","major","region"],
        "id": ["id","name","channel","user","order","patient","student","store"]
    }.items():
        for k in candidates:
            for c in cols_lower:
                if k in c:
                    out[key] = cols_lower[c]
                    break
            if key in out: break
    return out
