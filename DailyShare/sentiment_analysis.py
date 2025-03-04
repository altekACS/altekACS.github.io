#from transformers import pipeline
positive_words = {
    "高": 2, "增長": 3, "收益": 3, "利潤": 4, "上升": 2, 
    "突破": 5, "創新": 4, "穩健": 3, "卓越": 5, "蓬勃": 4, 
    "繁榮": 5, "提升": 3, "飆升": 5, "新高": 5, "回升": 3,
    "多頭": 4, "強勢": 4, "增值": 3, "買盤": 3, "利多": 4,
    "復甦": 3, "回報": 4, "看漲": 4, "上攻": 3, "強勁": 4,
    "穩定": 3, "增強": 4, "強化": 4, "豐收": 4, "上揚": 3,
    "增進": 4, "支持": 3, "利好": 4, "良好": 3, "欣欣向榮": 5, 
    "樂觀": 4, "紅盤": 5, "活躍": 4, "成長": 4, "豐厚": 5, 
    "潛力": 4, "漲停": 5, "看好": 4, "創紀錄": 5, "穩步": 3, 
    "優秀": 4, "加速": 4, "買入": 3, "擴大": 4, "盈利": 5, 
    "可觀": 4, "成就": 4, "反彈": 3, "新突破": 5, "主動": 3, 
    "集中": 3, "熱絡": 4, "樂觀情緒": 4, "標竿": 5, "指標": 3, 
    "飛躍": 5, "優勢": 4, "有利": 4, "穩增": 4, "增速": 4, "上漲": 4, "大漲": 4, 
    "歷史新高": 5, "耀眼": 5, "壓倒性": 5, "熱潮": 4, "關鍵": 3, 
    "佔優": 4, "成功": 4, "引領": 4, "亮眼": 5, "飛升": 5, 
    "收益穩定": 4, "利潤豐厚": 5, "回暖": 3, "支撐": 3, "熱賣": 4, 
    "價值提升": 4, "高需求": 4, "受益": 4, "平穩": 3, "正向發展": 4, 
    "基礎穩固": 4, "好轉": 3, "驅動": 4, "超越": 5, "受青睞": 4, 
    "深受歡迎": 4, "大幅上揚": 5, "高成長": 5, "優良表現": 4, "穩步上漲": 5,
    "業績增長": 5, "股價攀升": 5, "創新高": 5, "長期向好": 4, "盈利穩健": 4, 
    "增強信心": 4, "市值增加": 4, "市場回暖": 4, "財報利多": 5, "吸引投資": 4, 
    "創造價值": 4, "資金流入": 4, "業績優異": 5, "市場認可": 4, "股票熱度": 4, 
    "資本增長": 5, "預測樂觀": 4, "業績亮眼": 5, "正向循環": 4, "創歷史新高": 5,
    "股東回報": 4, "強勁表現": 5, "競爭力強": 4, "吸金能力": 5, "機構看好": 4,
    "獲利成長": 5, "產業利多": 4, "訂單大增": 5, "創收能力": 4, "企業盈利": 5
}


negative_words = {
    "衰退": -4, "減少": -3, "縮水": -4, "降": -2, "腰斬": -5, 
    "疲弱": -3, "下跌": -4, "風險": -3, "損失": -4, "危機": -5, 
    "波動": -2, "困難": -3, "崩盤": -5, "空頭": -4, "拋售": -4,
    "大跌": -5, "跳水": -5, "賣壓": -3, "虧損": -4, "跌停": -5,
    "壓力": -3, "負面": -4, "疲軟": -3, "下滑": -3, "暴跌": -5,
    "隱患": -4, "惡化": -4, "衰弱": -3, "暴露": -3, "走弱": -3,
    "萎縮": -4, "搖擺": -3, "回落": -3, "拖累": -3, "退步": -4,
    "急跌": -5, "困境": -4, "縮減": -4, "重挫": -5, "低迷": -3,
    "受挫": -3, "失利": -4, "壓抑": -3, "低落": -3, "恐慌": -5,
    "危險": -4, "負增長": -4, "衝擊": -4, "逆風": -3, "縮量": -3,
    "斷崖": -5, "不利": -4, "落後": -3, "驟降": -5, "不穩": -3,
    "裁員": -4, "停滯": -4, "低潮": -3, "減值": -4, "停牌": -4,
    "疲憊": -3, "流失": -4, "過剩": -4, "警報": -5, "壓縮": -4,
    "下壓": -3, "惡性": -5, "泡沫": -4, "混亂": -4, "撕裂": -5,
    "缺乏": -3, "限縮": -3, "動盪": -4, "崩潰": -5, "分裂": -4,
    "倒閉": -5, "潰敗": -5, "不穩定": -4, "削減": -4, "走低": -3,
    "惡化趨勢": -4, "拖後腿": -4, "衝突": -4, "負成長": -5, "嚴峻": -4,
    "危險信號": -5, "分歧": -3, "放緩": -3, "震盪": -4, "急速下降": -5,
    "資金外流": -4, "債務問題": -5, "拖欠": -4, "信用風險": -4, "違約": -5,
    "恐慌性拋售": -5, "銀行倒閉": -5, "信用破產": -5, "衝突加劇": -4, "利空消息": -5,
    "負債累累": -5, "融資困難": -4, "業績下滑": -4, "市場冷清": -3, "需求萎縮": -4,
    "失業率上升": -5, "經濟疲弱": -4, "通貨緊縮": -5, "企業破產": -5, "財政赤字": -5,
    "政策不確定": -4, "市場悲觀": -4, "資本緊縮": -4, "金融動盪": -5, "大幅縮水": -5,
    "通膨壓力": -4, "供應鏈中斷": -4, "經濟下滑": -5, "銷量下降": -4, "股東損失": -5,
    "投資風險": -4, "預警信號": -5, "市場崩潰": -5, "短線受挫": -4, "市場泡沫": -5,
    "價格戰": -4, "無法償還": -5, "債務違約": -5, "業務縮減": -4, "需求下滑": -4,
    "裁員潮": -5, "市場低迷": -4, "大幅度下跌": -5, "金融風暴": -5, "恐慌拋售": -5
}

weight_deep_word = {
    "positive": 1.3,  
    "negative": -1.3
}

def analyze_market_sentiment(sentence):
    """Analyze market sentiment (optimistic or panic) based on sentence sentiment."""
 #   sentiment_analyzer = pipeline("sentiment-analysis")
    try:

        # calculate whole words sentiment score
        positive_score = sum(positive_words[word] for word in positive_words if word in sentence)
        negative_score = sum(negative_words[word] for word in negative_words if word in sentence)
        sentiment = positive_score + negative_score

        # spit sentence into words by "，" and "。"
        sentence_splits = sentence.split("，") + sentence.split("。")
        positive_score_deep = sum(positive_words[word] for word in positive_words if word in sentence_splits)
        negative_score_deep = sum(negative_words[word] for word in negative_words if word in sentence_splits)
        sentiment_deep = positive_score_deep*weight_deep_word["positive"] + negative_score_deep*weight_deep_word["negative"]

        setiment_final = sentiment + sentiment_deep

        return setiment_final

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0