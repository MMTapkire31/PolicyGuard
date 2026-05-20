import nltk
from transformers import pipeline

nltk.download('punkt')  # Sentence tokenizer data

# Step 1 — Load DistilBERT fine-tuned on privacy policy text
# 'nlpaueb/legal-bert-small-uncased' is a good base; we'll fine-tune it in Phase 3
# For now we use it as-is for structure
classifier = pipeline(
    "text-classification",
    model="./model/policyguard"
)# Step 2 — Keyword rules: each category has keywords + a risk level
KEYWORD_RULES = {
    "Third Party Sharing": {
        "keywords": ["third party", "third-party", "share your data", "partners", "affiliates", "vendors", "advertisers"],
        "level": "high"
    },
    "Data Retention": {
        "keywords": ["retain", "retention", "store for", "keep your data", "stored for", "years", "indefinitely"],
        "level": "medium"
    },
    "User Rights": {
        "keywords": ["you cannot", "no right", "waive", "forfeit", "opt out not available", "cannot delete"],
        "level": "high"
    },
    "Payment Terms": {
        "keywords": ["non-refundable", "charge", "billing", "subscription", "auto-renew", "no refund"],
        "level": "high"
    },
    "Data Collection": {
        "keywords": ["collect", "we gather", "track", "monitor", "log your", "record"],
        "level": "medium"
    },
    "Location Data": {
        "keywords": ["location", "gps", "geolocation", "whereabouts"],
        "level": "high"
    }
}

def get_category_and_level(sentence):
    """Check sentence against keyword rules, return (category, level)"""
    sentence_lower = sentence.lower()

    for category, rule in KEYWORD_RULES.items():
        for keyword in rule["keywords"]:
            if keyword in sentence_lower:         # Keyword match found
                return category, rule["level"]    # Return immediately on first match

    return "General Risk", "medium"               # Risky but no keyword matched — default

def calculate_risk_score(risky_sentences):
    """Convert list of risky sentences into 0-100 score using your logic"""
    LEVEL_WEIGHTS = {"high": 10, "medium": 5, "low": 2}

    if not risky_sentences:
        return 0

    total_score = sum(LEVEL_WEIGHTS[s["risk_level"]] for s in risky_sentences)
    max_possible = len(risky_sentences) * LEVEL_WEIGHTS["high"]  # If all were high

    return round((total_score / max_possible) * 100)

def analyze_policy(text):
    """Main function — called by app.py"""

    # Step 1 — Split into sentences
    sentences = nltk.sent_tokenize(text)

    risky_sentences = []
    safe_sentences = []

    for sentence in sentences:
        if len(sentence.strip()) < 10:      # Skip very short fragments
            continue

        # Step 2 — DistilBERT classifies risky or safe
        # Truncate to 512 tokens so DistilBERT doesn't crash on long sentences
        result = classifier(sentence, truncation=True, max_length=512)[0]
        label = result['label']             # e.g. 'LABEL_1' or 'LABEL_0'
        confidence = round(result['score'], 3)

        # Step 3 — Map label to risky/safe
        # After fine-tuning, LABEL_1 = risky, LABEL_0 = safe
        is_risky = label == 'LABEL_1'

        if is_risky:
            category, level = get_category_and_level(sentence)
            risky_sentences.append({
                "text": sentence,
                "category": category,
                "risk_level": level,
                "confidence": confidence
            })
        else:
            safe_sentences.append({
                "text": sentence,
                "risk_level": "safe"
            })

    # Step 4 — Calculate overall score using your formula
    overall_score = calculate_risk_score(risky_sentences)

    return {
        "overall_risk_score": overall_score,
        "risky_sentences": risky_sentences,
        "safe_sentences": safe_sentences,
        "total_sentences": len(sentences)
    }