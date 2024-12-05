from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

print("CUDA Available:", torch.cuda.is_available())

# Initialize FinBERT and GPT-J
finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")
gptj = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-j-6B")

def analyze_financial_news(text):
    result = finbert(text)
    return result[0]['label'], result[0]['score']

def analyze_social_media(text):
    prompt = f"Analyze the sentiment of this text: '{text}'. Is it Positive, Negative, or Neutral?"
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = gptj.generate(**inputs, max_length=50)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Simple keyword check to map sentiment from response
    if "Positive" in response:
        return "Positive"
    elif "Negative" in response:
        return "Negative"
    else:
        return "Neutral"

news_text = "Company X reports record profits for Q3, exceeding expectations."
social_text = "The market is hyped about Company X's performance!"



print("FinBERT News Sentiment:", analyze_financial_news(news_text))
# print("GPT-J Social Media Sentiment:", analyze_social_media(social_text))