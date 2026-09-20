# CartSpark — market-basket recommender

A cart-aware "customers also bought" demo for a CMPE 256 hackathon. It counts
how often items appear together in past transactions and, for whatever is in
your cart, ranks other items by the sum of their lift against each cart item.
A FastAPI service holds the counts; a single HTML page is the storefront.

## What's here

- `backend/main.py` — FastAPI app. Loads the CSV once into item counts, pair
  counts and supports, then serves `/api/health`, `/api/catalog` and
  `POST /api/recommend` (body: `cart`, `top_k`, `min_pairs`, `min_lift`). Each
  recommendation comes back with its lift, confidence and pair count so the UI
  can explain itself. If nothing clears the thresholds it falls back to the
  strongest pairs for a single-item cart, then to the most popular items.
  Column names are auto-detected (`transaction_id`/`invoice`/`order_id`,
  `item_1..n` or anything containing item/product/description/sku).
- `frontend/index.html` — the whole UI in one file: catalog search, cart with
  quantities and totals, recommendation panel with "Why this?", a Chart.js lift
  chart, and a checkout drawer. Tailwind and Chart.js from CDN.
- `CartSpark_Market_Basket_Analysis.ipynb` — the same algorithm worked out in a
  notebook, with three sample carts and two plots. Committed without outputs.
- `tests/test_recommendations.py` — pytest checks on `load_model` and `rank`:
  catalog non-empty, `top_k` respected, cart items never recommended, expected
  keys present.
- `run_api.bat`, `run_frontend.bat` — Windows launchers.
- `check_notebook.py` — small helper that prints the notebook's cell counts.

## Data

`Retail/CMPE256_Hackathon_market_basket_analysis_Release.csv`, the dataset
handed out with the hackathon: 1,000 transactions over 40 security and
surveillance products (Bosch, Honeywell, Hanwha, Axis), 2-5 items per basket,
3.6 on average. Point `RETAIL_CSV` at another CSV in the same shape to use your
own.

## Running it

Two processes — the API and a static server for the page:

```bash
pip install -r requirements.txt
export RETAIL_CSV="$PWD/Retail/CMPE256_Hackathon_market_basket_analysis_Release.csv"
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
python -m http.server 5500 -d frontend    # in a second terminal
```

Then open http://127.0.0.1:5500/ — over HTTP, not `file://`, or the page cannot
reach the API. Health check: http://127.0.0.1:8000/api/health. Swagger:
http://127.0.0.1:8000/docs. Tests: `pytest tests/`. On Windows, `run_api.bat`
and `run_frontend.bat` do the same thing. Python 3.12 is the smoothest for the
pinned pandas.

## Course context

CMPE 256 (Recommender Systems) hackathon submission, SJSU.

## Limitations

Counting-based only — no Apriori/FP-growth, no model training, no personalization
or user history, and nothing is evaluated (no precision@k or holdout split). With
1,000 baskets and 40 items the pair counts are thin, which is why the fallbacks
exist. Checkout is cosmetic: "Pay (demo)" just empties the cart. Everything runs
locally and no data leaves the machine.

## Credits

Dataset supplied for the CMPE 256 hackathon. UI built with Tailwind CSS and
Chart.js; API with FastAPI.
