import os
import logging
import time
from typing import List, Optional, Dict, Any, Tuple
from collections import Counter, defaultdict
from itertools import combinations
from dataclasses import dataclass

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RETAIL_CSV = os.environ.get(
    "RETAIL_CSV",
    "./Retail/CMPE256_Hackathon_market_basket_analysis_Release.csv"
)

app = FastAPI(title="Hackathon Retail API", version="1.1-fixed")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@dataclass
class RetailModel:
    catalog: List[str]
    total_tx: int
    item_counter: Counter
    item_support: Dict[str, float]
    pair_counter: Counter
    top_pairs_per_item: Dict[str, List[Tuple[str, float, int]]]  # item -> [(partner, lift, count)]

_model: Optional[RetailModel] = None

def _pair(a: str, b: str) -> Tuple[str, str]:
    return tuple(sorted((a, b)))

def _detect_columns(df: pd.DataFrame):
    txn_col = next((c for c in df.columns if c.lower() in (
        "transaction_id","invoice","invoiceid","txn","transaction","basket_id","billno","order_id"
    )), None) or df.columns[0]
    item_cols = [c for c in df.columns if c.lower().startswith("item_")]
    if not item_cols:
        item_cols = [c for c in df.columns if any(k in c.lower() for k in ["item","product","description","sku"])]
    item_cols = [c for c in item_cols if c != txn_col]
    if not item_cols:
        raise RuntimeError("Could not find item columns.")
    return txn_col, item_cols

def load_model(csv_path: str) -> RetailModel:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Retail CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    txn_col, item_cols = _detect_columns(df)
    long = df.melt(id_vars=[txn_col], value_vars=item_cols, var_name="pos", value_name="item").dropna()
    long["item"] = long["item"].astype(str).str.strip()
    long[txn_col] = long[txn_col].astype(str).str.strip()
    baskets = long.groupby(txn_col)["item"].apply(lambda s: sorted(set(s.tolist())))

    item_counter = Counter()
    pair_counter = Counter()
    for b in baskets:
        item_counter.update(b)
        for a, c in combinations(b, 2):
            pair_counter[_pair(a, c)] += 1

    total_tx = len(baskets)
    item_support = {k: v/total_tx for k, v in item_counter.items()}
    catalog = sorted(item_counter.keys())
    
    # Pre-compute top pairs for each item (performance optimization)
    top_pairs = defaultdict(list)
    for (a, b), count in pair_counter.items():
        p_pair = count / total_tx
        lift = p_pair / (item_support[a] * item_support[b])
        top_pairs[a].append((b, lift, count))
        top_pairs[b].append((a, lift, count))
    
    # Keep only top 100 pairs per item, sorted by lift
    for item in top_pairs:
        top_pairs[item].sort(key=lambda x: x[1], reverse=True)
        top_pairs[item] = top_pairs[item][:100]
    
    return RetailModel(catalog, total_tx, item_counter, item_support, pair_counter, dict(top_pairs))

def ensure():
    global _model
    if _model is None:
        _model = load_model(RETAIL_CSV)

def lift_sum(cart: List[str], cand: str, m: RetailModel):
    s = 0.0; co = 0
    for it in cart:
        c = m.pair_counter.get(_pair(it, cand), 0)
        if c == 0: continue
        p_pair = c / m.total_tx
        s += p_pair / (m.item_support[it] * m.item_support[cand])
        co += c
    return s, co

def _reasons(cart: List[str], cand: str, m: RetailModel):
    rows = []
    for it in cart:
        c = m.pair_counter.get(_pair(it, cand), 0)
        if c == 0: continue
        p_pair = c / m.total_tx
        conf = c / m.item_counter[it]
        lift = p_pair / (m.item_support[it] * m.item_support[cand])
        rows.append({"from_item": it, "pair_count": int(c),
                     "confidence_from_item": float(conf), "lift_with_item": float(lift)})
    return rows

def rank(cart: List[str], m: RetailModel, top_k: int, min_pairs: int = 1, min_lift: float = 0.0, fallback: bool = True):
    cart = [x for x in cart if x in m.item_support]
    if not cart: return []

    # Build candidate set from pre-computed pairs (performance optimization)
    candidates = set()
    for cart_item in cart:
        if cart_item in m.top_pairs_per_item:
            # Only consider items that co-occur with this cart item
            candidates.update(item for item, _, _ in m.top_pairs_per_item[cart_item])
    
    # Remove items already in cart
    candidates -= set(cart)
    
    # If no candidates from pairs, fall back to full catalog
    if not candidates:
        candidates = set(m.catalog) - set(cart)

    scored = []
    for cand in candidates:  # Changed from m.catalog - much smaller set!
        ls, co = lift_sum(cart, cand, m)
        if co >= min_pairs and ls >= min_lift:
            scored.append((ls, co, m.item_support[cand], cand))

    if scored:
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        out = []
        for ls, co, supp, cand in scored[:top_k]:
            out.append({"candidate_item": cand, "lift_sum": float(ls),
                        "cooccurrence_count_sum": int(co), "support": float(supp),
                        "reasons": _reasons(cart, cand, m)})
        return out

    if not fallback: return []

    if len(cart) == 1:
        anchor = cart[0]
        pairs = []
        for (a,b), cnt in m.pair_counter.items():
            if anchor in (a,b):
                cand = b if a == anchor else a
                if cand in cart: continue
                pairs.append((cnt, m.item_support.get(cand, 0.0), cand))
        if pairs:
            pairs.sort(key=lambda t: (t[0], t[1]), reverse=True)
            out = []
            for cnt, supp, cand in pairs[:top_k]:
                ls, co = lift_sum([anchor], cand, m)
                out.append({"candidate_item": cand, "lift_sum": float(ls),
                            "cooccurrence_count_sum": int(co), "support": float(supp),
                            "reasons": _reasons([anchor], cand, m)})
            return out

    popular = sorted(((m.item_support[it], it) for it in m.catalog if it not in cart), reverse=True)[:top_k]
    return [{"candidate_item": it, "lift_sum": 0.0, "cooccurrence_count_sum": 0, "support": float(supp), "reasons": []}
            for supp, it in popular]

class RecommendRequest(BaseModel):
    cart: List[str]; top_k: int = 8
    min_pairs: Optional[int] = None; min_lift: Optional[float] = None

class RecommendResponse(BaseModel):
    items: List[Dict[str, Any]]

@app.get("/api/health")
def health(): return {"ok": True}

@app.get("/api/catalog")
def catalog():
    ensure(); return {"items": _model.catalog}

@app.get("/api/analytics")
def analytics():
    """Get dataset statistics and insights"""
    ensure()
    
    # Top items by support
    top_items = sorted(_model.item_support.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Strongest pairs by lift
    top_pairs = []
    for (a, b), count in sorted(_model.pair_counter.items(), key=lambda x: x[1], reverse=True)[:10]:
        p_pair = count / _model.total_tx
        lift = p_pair / (_model.item_support[a] * _model.item_support[b])
        top_pairs.append({
            "items": [a, b],
            "lift": round(lift, 3),
            "count": count,
            "support_pct": round(p_pair * 100, 2)
        })
    
    return {
        "total_items": len(_model.catalog),
        "total_transactions": _model.total_tx,
        "total_pairs": len(_model.pair_counter),
        "avg_items_per_transaction": round(sum(_model.item_counter.values()) / _model.total_tx, 2),
        "top_items": [{"item": k, "support_pct": round(v*100, 2)} for k, v in top_items],
        "top_pairs": top_pairs
    }

@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    start_time = time.time()
    ensure()
    
    items = rank(req.cart, _model, top_k=int(req.top_k or 8),
                 min_pairs=(req.min_pairs if req.min_pairs is not None else 1),
                 min_lift=(req.min_lift if req.min_lift is not None else 0.0),
                 fallback=True)
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Log request metrics
    logger.info(f"Recommendation request: cart_size={len(req.cart)}, "
                f"results={len(items)}, duration={duration_ms:.2f}ms, "
                f"top_k={req.top_k}")
    
    return {"items": items}
