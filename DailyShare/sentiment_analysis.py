#from transformers import pipeline

def analyze_market_sentiment(sentence):
    """Analyze market sentiment (optimistic or panic) based on sentence sentiment."""
 #   sentiment_analyzer = pipeline("sentiment-analysis")
    try:
        # sentiment = sentiment_analyzer(sentence)[0]

        # if sentiment['label'] == 'POSITIVE':
        #     return 1
        # elif sentiment['label'] == 'NEGATIVE':
        #     return -1
        # else:
        return 0

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0