from transformers import pipeline
import torch

# Initialize sentiment analysis pipeline
try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1
    )
except Exception as e:
    print(f"Warning: Could not load sentiment model: {e}")
    sentiment_analyzer = None

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of complaint text
    Returns: sentiment (Positive/Negative/Neutral), score (0-1), emotion label
    """
    if not sentiment_analyzer:
        return {
            "sentiment": "Neutral",
            "sentiment_score": 0.5,
            "emotion": "Calm"
        }
    
    try:
        result = sentiment_analyzer(text[:512])[0]  # Limit to 512 tokens
        
        label = result['label']
        score = result['score']
        
        # Map to our sentiment labels
        if label == "POSITIVE":
            sentiment = "Positive"
            emotion = "Calm"
        else:  # NEGATIVE
            sentiment = "Negative"
            # Map score to emotion intensity
            if score > 0.9:
                emotion = "Furious"
            elif score > 0.75:
                emotion = "Angry"
            elif score > 0.6:
                emotion = "Frustrated"
            else:
                emotion = "Concerned"
        
        return {
            "sentiment": sentiment,
            "sentiment_score": score,
            "emotion": emotion
        }
        
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return {
            "sentiment": "Neutral",
            "sentiment_score": 0.5,
            "emotion": "Calm"
        }

def calculate_priority_score(severity: str, sentiment_score: float, customer_tier: str, is_regulatory: bool) -> float:
    """
    Calculate priority score (0-10) based on multiple factors
    """
    # Severity weight (0-10)
    severity_map = {"Critical": 10, "High": 8, "Medium": 5, "Low": 2}
    severity_weight = severity_map.get(severity, 5)
    
    # Sentiment weight (0-10) - higher score = more negative = higher priority
    sentiment_weight = sentiment_score * 10 if sentiment_score > 0.5 else 0
    
    # Customer tier weight (0-10)
    tier_weight = 10 if customer_tier == "premium" else 5
    
    # Regulatory weight (0-10)
    regulatory_weight = 10 if is_regulatory else 0
    
    # Weighted formula
    priority = (
        severity_weight * 0.35 +
        sentiment_weight * 0.25 +
        tier_weight * 0.20 +
        regulatory_weight * 0.20
    )
    
    return round(min(priority, 10), 2)
