# CartSpark — Retail Market-Basket Recommender

A clean, cart-aware recommender that uses **co-occurrence (lift)** to suggest add-ons in real time.  
If the data gives no signal, CartSpark falls back to strong pairs and popularity — never random.

- **Catalog** (searchable)
- **Cart** (quantities, totals, **Proceed to Checkout**)
- **Recommendations** (Top-K) with **“Why this?”** explanations
- **Lift chart** (Chart.js)
- **Checkout drawer** with **Pay (demo)** (clears cart only)

---

## 📦 What’s in this repo

```
CartSpark_Recommender/
├─ backend/
│  └─ main.py                # FastAPI app (lift + fallbacks + explanations)
├─ frontend/
│  └─ index.html             # UI (catalog, cart, recs, checkout drawer)
├─ Retail/
│  └─ CMPE256_Hackathon_market_basket_analysis_Release.csv  # (optional: or set RETAIL_CSV)
├─ requirements.txt
├─ README.md
├─ run_api.bat               # Windows helper (optional)
└─ run_frontend.bat          # Windows helper (optional)
```

**Data format:** one CSV with a transaction id column (auto-detected: `transaction_id`, `invoice`, `txn`, `order_id`, etc.) and one or more item columns (`item_1..item_n`) or columns containing `item` / `product` / `description` / `sku`.

---

## ✅ Prerequisites

- **Python 3.12.x** (recommended; `pandas` wheels install cleanly)
- A modern browser (Chrome / Edge / Firefox / Safari)
- Your retail CSV file (place in `./Retail/` or set the `RETAIL_CSV` environment variable)

> **Important:** Always open the site via **HTTP** (e.g., `http://127.0.0.1:5500/`). Opening `file:///…/index.html` bypasses the API and **recommendations won’t load**.

---

## 🚀 Quick Start

> The app has two parts:
> - **API (FastAPI)** → **http://127.0.0.1:8000/**
> - **Frontend (static server)** → **http://127.0.0.1:5500/**

### Windows (PowerShell)

```powershell
# 1) Go to the project folder you unzipped/cloned
cd $HOME\Downloads\CartSpark_Recommender

# 2) Tell the app where your CSV is (or copy it under .\Retail\ with this filename)
$env:RETAIL_CSV = "$HOME\Downloads\Retail\CMPE256_Hackathon_market_basket_analysis_Release.csv"

# 3) Create a virtual env and install dependencies
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4) Start the API (keep this terminal open)
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
# Health link: http://127.0.0.1:8000/api/health

# 5) Open a NEW PowerShell and run the frontend server
cd $HOME\Downloads\CartSpark_Recommender
python -m http.server 5500 -d frontend

# 6) Open the site
start http://127.0.0.1:5500/index.html
```

### macOS / Linux (bash/zsh)

```bash
# 1) Go to the project folder
cd ~/Downloads/CartSpark_Recommender

# 2) CSV path (or copy it under ./Retail/ with this filename)
export RETAIL_CSV="$HOME/Downloads/Retail/CMPE256_Hackathon_market_basket_analysis_Release.csv"

# 3) Create venv & install deps
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) Start the API (keep this window open)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
# Health link: http://127.0.0.1:8000/api/health

# 5) NEW terminal → run the frontend server
cd ~/Downloads/CartSpark_Recommender
python -m http.server 5500 -d frontend

# 6) Open the site
open http://127.0.0.1:5500/index.html        # macOS
# or:
xdg-open http://127.0.0.1:5500/index.html    # Linux
```

---

## 🔎 Verify it’s working

1) API health: **http://127.0.0.1:8000/api/health** → `{"ok": true}`  
2) Catalog: **http://127.0.0.1:8000/api/catalog** → `{"items":["…"]}`  
3) Site: **http://127.0.0.1:5500/** (or **/index.html**)  
4) In the UI, click **Add** on a few products → recommendations appear on the right  
5) Click **Proceed to Checkout** → drawer opens; **Pay (demo)** clears cart

---

## 🔌 Useful Links (click once servers are running)

- **Site (Frontend):** http://127.0.0.1:5500/
- **Health (API):** http://127.0.0.1:8000/api/health
- **Catalog (API):** http://127.0.0.1:8000/api/catalog
- **Swagger UI (optional):** http://127.0.0.1:8000/docs

Quick API test (paste in browser DevTools Console):
```js
fetch("http://127.0.0.1:8000/api/recommend", {
  method: "POST",
  headers: {"Content-Type":"application/json"},
  body: JSON.stringify({
    cart: ["Bosch B5512 Control Panel (SKU: B5512)"],
    top_k: 8,
    min_pairs: 1,
    min_lift: 0.0
  })
}).then(r=>r.json()).then(console.log);
```

---

## 🧠 How the model ranks items

- Build baskets per transaction
- Count **items** and **pairs**; compute support and pair frequencies
- Score each candidate for the current cart by **sum of lifts** vs each cart item
- If nothing qualifies:
  1) show strongest **pair counts** for single-item carts
  2) show most **popular** items (by support)
- “Why this?” shows per-item **lift**, **confidence**, and **pair counts**

---

## 🛠️ Troubleshooting

**“Proceed to Checkout” does nothing**  
- Make sure you’re on **http://127.0.0.1:5500/index.html** (not `file:///…`)  
- Hard refresh (**Ctrl+F5**)  

**PowerShell blocks venv activation**  
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or run without activation:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**`pip` is slow/stuck on building pandas**  
Use **Python 3.12.x**. If you must use 3.13, bump pandas in `requirements.txt` to a wheel build (e.g. `pandas>=2.2.3`) and then:
```
pip install --only-binary=:all: -r requirements.txt
```

**“No relevant recommendations.”**  
- API running? → http://127.0.0.1:8000/api/health  
- CSV path correct? (`RETAIL_CSV`) or file in `./Retail/`  
- Try denser anchors:
  - `Bosch B5512 Control Panel (SKU: B5512)`
  - `Bosch B810 Wireless Receiver (SKU: B810)`
  - `Axis P3225-LVE Network Camera (SKU: 0935-001)`

**Port is busy / firewall prompt**  
- Use another port:  
  - API → `--port 8001` → http://127.0.0.1:8001/  
  - Frontend → `python -m http.server 5501 -d frontend` → http://127.0.0.1:5501/  
- Allow Python through Windows Firewall when prompted.

---

## ⚙️ Configuration & Customization

- **CSV path:** set `RETAIL_CSV` or put the file into `./Retail/`  
- **Top-K / thresholds:** edit the body of the `/api/recommend` fetch in `frontend/index.html`  
- **Branding / colors / logo:** Tailwind classes in `frontend/index.html`  
- **Chart:** Chart.js options in `frontend/index.html` (`getOrCreateChart()`)

---

## 🔒 Notes

- For hackathon / educational use only. **Pay (demo)** is non-functional and only clears the cart.
- Data stays local; nothing is sent to external services.

---

## 🙌 Credits

- UI: **Tailwind CSS** + **Chart.js**  
- API: **FastAPI** (Python)  
- Model: co-occurrence counts, support, and **lift** with clear fallbacks and explanations.
