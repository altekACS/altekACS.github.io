#from transformers import pipeline

positive_words = {
    "高": 2, "增長": 3, "收益": 3, "利潤": 4, "上升": 2, 
    "突破": 5, "創新": 4, "穩健": 3, "卓越": 5, "蓬勃": 4, 
    "繁榮": 5, "提升": 3
}
negative_words = {
    "衰退": -4, "減少": -3, "縮水": -4, "降": -2, "腰斬": -5, 
    "疲弱": -3, "下跌": -4, "風險": -3, "損失": -4, "危機": -5, 
    "波動": -2, "困難": -3
}



def analyze_market_sentiment(sentence):
    """Analyze market sentiment (optimistic or panic) based on sentence sentiment."""
 #   sentiment_analyzer = pipeline("sentiment-analysis")
    try:

        positive_score = sum(positive_words[word] for word in positive_words if word in sentence)
        negative_score = sum(negative_words[word] for word in negative_words if word in sentence)
        sentiment = positive_score - negative_score

        # sentiment = sentiment_analyzer(sentence)[0]

        # if sentiment['label'] == 'POSITIVE':
        #     return 1
        # elif sentiment['label'] == 'NEGATIVE':
        #     return -1
        # else:
        return sentiment

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0