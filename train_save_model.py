import pandas as pd
import string
import pickle
import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# Download stopwords & wordnet
nltk.download('stopwords')
nltk.download('wordnet')

# Preprocessing function
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
def clean_text(text):
    text = str(text).lower()
    text = ''.join([c for c in text if c not in string.punctuation])
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return ' '.join(words)

# Load dataset lokal (harus tersedia hanya untuk pelatihan awal)
csv_path = os.path.join(os.path.dirname(__file__), 'phishing_email.csv')
df = pd.read_csv(csv_path)
df = df.dropna(subset=["text_combined", "label"])
df["clean_text"] = df["text_combined"].apply(clean_text)

# TF-IDF & Model Training
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
X = vectorizer.fit_transform(df["clean_text"])
y = df["label"]

model = MultinomialNB()
model.fit(X, y)

# Simpan model & vectorizer
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Model dan vectorizer berhasil disimpan sebagai .pkl")
