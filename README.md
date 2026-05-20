# 🛡️ PolicyGuard

> A Chrome Extension that automatically analyzes privacy policies and highlights hidden risks using DistilBERT — because 90% of users never read what they agree to.

---

## 🔍 Problem Statement

Every time you sign up for a service, you click "I Agree" without reading the privacy policy. These documents are deliberately long and complex. They often contain clauses that allow companies to sell your data, track your location, or retain your information indefinitely. PolicyGuard reads it for you and tells you exactly what to watch out for.

---

## 🎯 What It Does

- Detects privacy policy text on any webpage automatically
- Classifies every sentence as **risky** or **safe** using a fine-tuned DistilBERT model
- Assigns each risky sentence a **risk level** (High / Medium / Low) and a **category** (Third Party Sharing, Data Retention, User Rights, Payment Terms, etc.)
- Displays an **overall risk score** (0–100) with a visual progress bar
- Shows **sentence-by-sentence analysis** grouped by category
- Color coded badges — 🔴 High, 🟠 Medium, 🟡 Low, 🟢 Safe

---

## ⚙️ How It Works

```
User clicks "Analyze Policy" on the extension popup
        ↓
popup.html sends message to content.js via Chrome message passing
        ↓
content.js extracts all <p> text from the webpage
        ↓
popup.html sends extracted text via POST request to Flask backend
        ↓
app.py receives the text and calls analyze_policy()
        ↓
analyzer.py splits text into sentences using NLTK
        ↓
Each sentence is passed to fine-tuned DistilBERT → risky or safe
        ↓
Risky sentences → keyword matching → assigns category + risk level
        ↓
Overall risk score calculated → JSON response returned
        ↓
popup.html renders results with risk score + sentence analysis
```

---

## 📁 Project Structure

```
policyguard/
│
├── extension/                  # Chrome Extension (frontend)
│   ├── manifest.json           # Tells Chrome about the extension, permissions
│   ├── popup.html              # UI shown when user clicks extension icon
│   └── content.js              # Runs on webpage, extracts privacy policy text
│
├── backend/                    # Flask Backend (NLP processing)
│   ├── app.py                  # Flask server, receives POST requests from extension
│   ├── analyzer.py             # Core NLP logic — DistilBERT + risk classification
│   └── train.py                # Fine-tuning script for DistilBERT
│
├── data/
│   └── privacy_dataset.csv     # Labeled training data (sentence, label)
│
├── model/
│   └── policyguard/            # Saved fine-tuned DistilBERT model
│       ├── config.json
│       └── pytorch_model.bin
│
└── requirements.txt            # Python dependencies
```

---

## 🧠 File Explanations

### `content.js`
Runs inside the webpage context (sandboxed by Chrome). Its only job is to find and extract privacy policy text from the page using a priority-based approach:
```
<main> → <article> → <section> → <body>
```
Extracts all `<p>` tags, strips HTML using `.innerText`, filters out short fragments, and sends clean text back to `popup.html` via Chrome message passing.

### `popup.html`
The extension's headquarters. Triggers `content.js`, receives extracted text, sends POST request to Flask, shows a loading progress bar while waiting, then renders the full risk analysis. All Flask communication happens here — not in `content.js` — because Chrome sandboxes content scripts from making external API calls.

### `manifest.json`
Declares extension metadata, permissions (`activeTab`, `scripting`), and allowed hosts (`localhost:5000`). Uses Manifest V3 — the latest Chrome standard.

### `app.py`
A minimal Flask server with a single `/analyze` endpoint. Receives POST requests with policy text, passes it to `analyze_policy()`, returns JSON. `CORS` is enabled so the Chrome extension (different origin) can communicate with it.

### `analyzer.py`
The core NLP engine:
1. Splits text into sentences using NLTK
2. Each sentence → fine-tuned DistilBERT → `risky (1)` or `safe (0)`
3. Risky sentences → keyword rule matching → assigns category + risk level
4. Calculates overall risk score: `high=10pts`, `medium=5pts`, `low=2pts` → normalized to 0–100

### `train.py`
Fine-tunes `distilbert-base-uncased` on labeled privacy policy sentences. Tokenizes using DistilBERT's tokenizer (max 512 tokens, padding, truncation), trains for 3 epochs, saves the best model to `model/policyguard/`.

---

## 🧪 Training Results

![Training Results](../assets/training_results.png)

| Epoch | Eval Loss |
|-------|-----------|
| 1     | 0.6700    |
| 2     | 0.6686    |
| 3     | 0.6461    |

## 🛠️ Tech Stack

| Technology | Purpose | Why chosen |
|---|---|---|
| DistilBERT | Sentence risk classification | 40% smaller than BERT, 60% faster, retains 97% accuracy — ideal for real-time extension use |
| Flask | Backend API server | Lightweight, minimal boilerplate, perfect for serving a single ML endpoint |
| NLTK | Sentence tokenization | Reliable sentence boundary detection for splitting policy text |
| HuggingFace Transformers | Model loading + fine-tuning | Industry standard library for working with BERT-based models |
| Chrome Extensions (MV3) | Browser integration | Manifest V3 is the current Chrome standard, more secure than V2 |
| JavaScript (Vanilla) | Extension frontend | No framework needed for a lightweight popup UI |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Google Chrome
- pip

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/policyguard.git
cd policyguard
```

### 2. Install Python dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Train the model
```bash
py train.py
# This will fine-tune DistilBERT and save the model to model/policyguard/
# Takes approximately 10-30 minutes depending on your machine
```

### 4. Start the Flask backend
```bash
py app.py
# Server runs on http://localhost:5000
```

### 5. Load the Chrome Extension
```
1. Open Chrome and go to chrome://extensions
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the extension/ folder
```

### 6. Test it
Visit any of these pages and click the PolicyGuard icon:
- https://policies.google.com/privacy
- https://www.facebook.com/privacy/policy
- https://twitter.com/en/privacy

---

## 📊 Sample Output

```json
{
  "overall_risk_score": 74,
  "total_sentences": 42,
  "risky_sentences": [
    {
      "text": "We may share your data with third-party partners.",
      "category": "Third Party Sharing",
      "risk_level": "high",
      "confidence": 0.934
    },
    {
      "text": "We retain your information for up to 10 years.",
      "category": "Data Retention",
      "risk_level": "medium",
      "confidence": 0.871
    }
  ]
}
```

---

## 🔮 Future Improvements

- **Larger dataset** — Fine-tune on a comprehensive online dataset such as OPP-115 (115 real annotated privacy policies) for significantly higher accuracy and better generalization across different policy writing styles
- **Plain English summary** — Integrate an LLM to generate a short 3–4 sentence summary of the entire privacy policy in simple language, so users who won't read the full policy still understand what they're agreeing to
- **Risk score history** — Track risk scores across websites the user has visited, allowing comparison and trend analysis
- **Browser notifications** — Alert users automatically when they land on a high-risk privacy policy page without needing to click the extension
- **Export report** — Allow users to download a PDF report of the full risk analysis

---

## 👩‍💻 Author

**Mayuri** — B.Tech CSE (Data Science), VIT Pune  
[GitHub](https://github.com/yourusername) • [LinkedIn](https://linkedin.com/in/yourprofile)