import pandas as pd
import sqlite3
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import spacy
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import os
import numpy as np

# Download NLTK data
nltk.download("vader_lexicon")
nltk.download("stopwords")

# Initialize spaCy for tokenization and entity recognition
nlp = spacy.load("en_core_web_sm")

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Set up stopwords
stop_words = set(stopwords.words("english"))

# Create directories for results and high-DPI figures
results_dir = "/Users/charleenadams/nyt/results_2"
figures_dir = "/Users/charleenadams/nyt/results_high_dpi"
os.makedirs(results_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)

# Step 1: Load metadata from the database
print("Loading metadata from nyt_articles_metadata.db...")
conn = sqlite3.connect("/Users/charleenadams/nyt/nyt_articles_metadata.db")
df = pd.read_sql_query("SELECT * FROM articles", conn)
conn.close()
print(f"Loaded {len(df)} articles from the database.")

# Define Israeli and Palestinian terms
israeli_terms = ["Israel", "Israeli", "IDF"]
palestinian_terms = ["Palestinian", "Palestine", "Hamas", "Gaza"]

# Step 2: Sentiment Analysis
print("\nPerforming Sentiment Analysis...")
israeli_sentiments = []
palestinian_sentiments = []
israeli_mentions = 0
palestinian_mentions = 0

for headline in df["headline"]:
    sentiment_scores = sia.polarity_scores(headline)
    compound_score = sentiment_scores["compound"]

    headline_lower = headline.lower()
    has_israeli = any(term.lower() in headline_lower for term in israeli_terms)
    has_palestinian = any(term.lower() in headline_lower for term in palestinian_terms)

    if has_israeli:
        israeli_sentiments.append(compound_score)
        israeli_mentions += 1
    if has_palestinian:
        palestinian_sentiments.append(compound_score)
        palestinian_mentions += 1

# Calculate average sentiment
avg_israeli_sentiment = sum(israeli_sentiments) / len(israeli_sentiments) if israeli_sentiments else 0
avg_palestinian_sentiment = sum(palestinian_sentiments) / len(palestinian_sentiments) if palestinian_sentiments else 0

# Save sentiment results to a file
with open(os.path.join(results_dir, "sentiment_analysis.txt"), "w") as f:
    f.write("Sentiment Analysis Results:\n")
    f.write(f"Average sentiment for headlines mentioning Israeli terms: {avg_israeli_sentiment:.3f}\n")
    f.write(f"Average sentiment for headlines mentioning Palestinian terms: {avg_palestinian_sentiment:.3f}\n")
    f.write(f"Total mentions of Israeli terms: {israeli_mentions}\n")
    f.write(f"Total mentions of Palestinian terms: {palestinian_mentions}\n")
    f.write(f"Ratio of mentions (Israeli:Palestinian): {israeli_mentions/palestinian_mentions:.2f}\n" if palestinian_mentions else "N/A\n")

# Visualization: Sentiment Comparison
plt.figure(figsize=(8, 6))
sns.barplot(x=["Israeli", "Palestinian"], y=[avg_israeli_sentiment, avg_palestinian_sentiment], palette="coolwarm")
plt.title("Average Sentiment in Headlines", fontsize=14)
plt.ylabel("Average Sentiment Score", fontsize=12)
plt.ylim(-1, 1)
plt.savefig(os.path.join(figures_dir, "sentiment_comparison.png"), dpi=600)
plt.close()

# Visualization: Sentiment Distribution
plt.figure(figsize=(10, 6))
sns.histplot(israeli_sentiments, bins=20, kde=True, color="blue", label="Israeli Mentions")
sns.histplot(palestinian_sentiments, bins=20, kde=True, color="red", label="Palestinian Mentions")
plt.title("Sentiment Distribution in Headlines", fontsize=14)
plt.xlabel("Sentiment Score", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.legend()
plt.savefig(os.path.join(figures_dir, "sentiment_distribution.png"), dpi=600)
plt.close()

# Step 3: Keyword Frequency and Co-Occurrence
print("Performing Keyword Frequency and Co-Occurrence Analysis...")
all_words = []
israeli_cooccur = []
palestinian_cooccur = []

for headline in df["headline"]:
    doc = nlp(headline)
    words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop and token.text.lower() not in stop_words]
    all_words.extend(words)

    headline_lower = headline.lower()
    has_israeli = any(term.lower() in headline_lower for term in israeli_terms)
    has_palestinian = any(term.lower() in headline_lower for term in palestinian_terms)

    if has_israeli:
        israeli_cooccur.extend(words)
    if has_palestinian:
        palestinian_cooccur.extend(words)

# Keyword frequency
word_freq = Counter(all_words)
israeli_cooccur_freq = Counter(israeli_cooccur)
palestinian_cooccur_freq = Counter(palestinian_cooccur)

# Save keyword frequency results
with open(os.path.join(results_dir, "keyword_frequency.txt"), "w") as f:
    f.write("Top 20 Most Frequent Words in Headlines:\n")
    for word, freq in word_freq.most_common(20):
        f.write(f"{word}: {freq}\n")
    f.write("\nTop 20 Words Co-Occurring with Israeli Terms:\n")
    for word, freq in israeli_cooccur_freq.most_common(20):
        f.write(f"{word}: {freq}\n")
    f.write("\nTop 20 Words Co-Occurring with Palestinian Terms:\n")
    for word, freq in palestinian_cooccur_freq.most_common(20):
        f.write(f"{word}: {freq}\n")

# Visualization: Word Clouds
wordcloud_all = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(dict(word_freq))
wordcloud_israeli = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(dict(israeli_cooccur_freq))
wordcloud_palestinian = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(dict(palestinian_cooccur_freq))

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_all, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud: All Headlines", fontsize=14)
plt.savefig(os.path.join(figures_dir, "wordcloud_all.png"), dpi=600)
plt.close()

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_israeli, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud: Israeli Co-Occurrence", fontsize=14)
plt.savefig(os.path.join(figures_dir, "wordcloud_israeli.png"), dpi=600)
plt.close()

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_palestinian, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud: Palestinian Co-Occurrence", fontsize=14)
plt.savefig(os.path.join(figures_dir, "wordcloud_palestinian.png"), dpi=600)
plt.close()

# Step 4: Named Entity Recognition (NER)
print("Performing Named Entity Recognition (NER)...")
entities = []
israeli_entities = []
palestinian_entities = []

for headline in df["headline"]:
    doc = nlp(headline)
    headline_entities = [(ent.text, ent.label_) for ent in doc.ents]
    entities.extend(headline_entities)

    headline_lower = headline.lower()
    has_israeli = any(term.lower() in headline_lower for term in israeli_terms)
    has_palestinian = any(term.lower() in headline_lower for term in palestinian_terms)

    if has_israeli:
        israeli_entities.extend(headline_entities)
    if has_palestinian:
        palestinian_entities.extend(headline_entities)

# Count entities
entity_freq = Counter([ent[0] for ent in entities])
israeli_entity_freq = Counter([ent[0] for ent in israeli_entities])
palestinian_entity_freq = Counter([ent[0] for ent in palestinian_entities])

# Save NER results
with open(os.path.join(results_dir, "ner_results.txt"), "w") as f:
    f.write("Top 20 Most Frequent Entities in Headlines:\n")
    for ent, freq in entity_freq.most_common(20):
        f.write(f"{ent}: {freq}\n")
    f.write("\nTop 20 Entities in Headlines Mentioning Israeli Terms:\n")
    for ent, freq in israeli_entity_freq.most_common(20):
        f.write(f"{ent}: {freq}\n")
    f.write("\nTop 20 Entities in Headlines Mentioning Palestinian Terms:\n")
    for ent, freq in palestinian_entity_freq.most_common(20):
        f.write(f"{ent}: {freq}\n")

# Visualization: Entity Frequency
top_entities = [ent for ent, freq in entity_freq.most_common(10)]
top_entity_freqs = [freq for ent, freq in entity_freq.most_common(10)]

plt.figure(figsize=(10, 6))
sns.barplot(x=top_entity_freqs, y=top_entities, palette="viridis")
plt.title("Top 10 Entities in Headlines", fontsize=14)
plt.xlabel("Frequency", fontsize=12)
plt.ylabel("Entity", fontsize=12)
plt.savefig(os.path.join(figures_dir, "entity_frequency.png"), dpi=600)
plt.close()

# Entity Sentiment Association
print("Performing Entity Sentiment Association...")
top_entities = [ent for ent, freq in entity_freq.most_common(5)]
entity_sentiments = {}

for ent in top_entities:
    ent_sentiments = []
    for headline in df["headline"]:
        if ent.lower() in headline.lower():
            sentiment_scores = sia.polarity_scores(headline)
            ent_sentiments.append(sentiment_scores["compound"])
    if ent_sentiments:
        entity_sentiments[ent] = sum(ent_sentiments) / len(ent_sentiments)
    else:
        entity_sentiments[ent] = 0

# Save entity sentiment results
with open(os.path.join(results_dir, "entity_sentiment.txt"), "w") as f:
    f.write("Average Sentiment for Top Entities:\n")
    for ent, sent in entity_sentiments.items():
        f.write(f"{ent}: {sent:.3f}\n")

# Visualization: Entity Sentiment
plt.figure(figsize=(10, 6))
sns.barplot(x=list(entity_sentiments.keys()), y=list(entity_sentiments.values()), palette="coolwarm")
plt.title("Average Sentiment for Top Entities", fontsize=14)
plt.xlabel("Entity", fontsize=12)
plt.ylabel("Average Sentiment Score", fontsize=12)
plt.ylim(-1, 1)
plt.xticks(rotation=45)
plt.savefig(os.path.join(figures_dir, "entity_sentiment.png"), dpi=600)
plt.close()

# Step 5: Topic Modeling
print("Performing Topic Modeling...")
vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["headline"])
nmf = NMF(n_components=5, random_state=42)
nmf_matrix = nmf.fit_transform(tfidf_matrix)
feature_names = vectorizer.get_feature_names_out()

# Extract topics
topics = []
for topic_idx, topic in enumerate(nmf.components_):
    top_words = [feature_names[i] for i in topic.argsort()[-10:]]
    topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")

# Save topic modeling results
with open(os.path.join(results_dir, "topic_modeling.txt"), "w") as f:
    f.write("Topic Modeling Results (5 Topics):\n")
    for topic in topics:
        f.write(f"{topic}\n")

# Visualization: Topic Word Distribution
plt.figure(figsize=(12, 8))
for topic_idx, topic in enumerate(nmf.components_):
    top_words_idx = topic.argsort()[-5:]
    top_words = [feature_names[i] for i in top_words_idx]
    top_scores = topic[top_words_idx]
    plt.subplot(3, 2, topic_idx + 1)
    sns.barplot(x=top_scores, y=top_words, palette="magma")
    plt.title(f"Topic {topic_idx + 1}", fontsize=12)
    plt.xlabel("Score", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "topic_word_distribution.png"), dpi=600)
plt.close()

# Step 6: Temporal Analysis
print("Performing Temporal Analysis...")
df["pub_date"] = pd.to_datetime(df["pub_date"])
df["month"] = df["pub_date"].dt.to_period("M")

# Count mentions by month
monthly_israeli_mentions = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in israeli_terms]))].groupby("month").size()
monthly_palestinian_mentions = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in palestinian_terms]))].groupby("month").size()

# Calculate average sentiment by month
monthly_israeli_sentiment = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in israeli_terms]))].groupby("month")["headline"].apply(lambda x: sia.polarity_scores(" ".join(x))["compound"])
monthly_palestinian_sentiment = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in palestinian_terms]))].groupby("month")["headline"].apply(lambda x: sia.polarity_scores(" ".join(x))["compound"])

# Save temporal analysis results
with open(os.path.join(results_dir, "temporal_analysis.txt"), "w") as f:
    f.write("Monthly Mentions of Israeli Terms:\n")
    f.write(monthly_israeli_mentions.to_string() + "\n")
    f.write("\nMonthly Mentions of Palestinian Terms:\n")
    f.write(monthly_palestinian_mentions.to_string() + "\n")
    f.write("\nMonthly Sentiment for Israeli Terms:\n")
    f.write(monthly_israeli_sentiment.to_string() + "\n")
    f.write("\nMonthly Sentiment for Palestinian Terms:\n")
    f.write(monthly_palestinian_sentiment.to_string() + "\n")

# Visualization: Temporal Trends
plt.figure(figsize=(12, 6))
monthly_israeli_mentions.plot(label="Israeli Mentions", color="blue")
monthly_palestinian_mentions.plot(label="Palestinian Mentions", color="red")
plt.title("Monthly Mentions Over Time", fontsize=14)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Number of Mentions", fontsize=12)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "temporal_mentions.png"), dpi=600)
plt.close()

plt.figure(figsize=(12, 6))
monthly_israeli_sentiment.plot(label="Israeli Sentiment", color="blue")
monthly_palestinian_sentiment.plot(label="Palestinian Sentiment", color="red")
plt.title("Monthly Sentiment Over Time", fontsize=14)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Average Sentiment Score", fontsize=12)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "temporal_sentiment.png"), dpi=600)
plt.close()

# Keyword Evolution Over Time
print("Performing Keyword Evolution Analysis...")
key_terms = ["attack", "peace", "conflict"]
monthly_key_term_counts = {}
for term in key_terms:
    monthly_key_term_counts[term] = df[df["headline"].str.lower().str.contains(term.lower())].groupby("month").size()

# Visualization: Keyword Evolution
plt.figure(figsize=(12, 6))
for term in key_terms:
    monthly_key_term_counts[term].plot(label=term)
plt.title("Monthly Mentions of Key Terms Over Time", fontsize=14)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Number of Mentions", fontsize=12)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "keyword_evolution.png"), dpi=600)
plt.close()

# Step 7: Framing Analysis (Word Choice)
print("Performing Framing Analysis...")
israeli_adjectives = []
palestinian_adjectives = []

for headline in df["headline"]:
    doc = nlp(headline)
    adjectives = [token.text.lower() for token in doc if token.pos_ == "ADJ" and token.text.lower() not in stop_words]

    headline_lower = headline.lower()
    has_israeli = any(term.lower() in headline_lower for term in israeli_terms)
    has_palestinian = any(term.lower() in headline_lower for term in palestinian_terms)

    if has_israeli:
        israeli_adjectives.extend(adjectives)
    if has_palestinian:
        palestinian_adjectives.extend(adjectives)

# Count adjectives
israeli_adj_freq = Counter(israeli_adjectives)
palestinian_adj_freq = Counter(palestinian_adjectives)

# Save framing analysis results
with open(os.path.join(results_dir, "framing_analysis.txt"), "w") as f:
    f.write("Top 20 Adjectives in Headlines Mentioning Israeli Terms:\n")
    for adj, freq in israeli_adj_freq.most_common(20):
        f.write(f"{adj}: {freq}\n")
    f.write("\nTop 20 Adjectives in Headlines Mentioning Palestinian Terms:\n")
    for adj, freq in palestinian_adj_freq.most_common(20):
        f.write(f"{adj}: {freq}\n")

# Visualization: Adjective Frequency
top_israeli_adjs = [adj for adj, freq in israeli_adj_freq.most_common(10)]
top_israeli_freqs = [freq for adj, freq in israeli_adj_freq.most_common(10)]
top_palestinian_adjs = [adj for adj, freq in palestinian_adj_freq.most_common(10)]
top_palestinian_freqs = [freq for adj, freq in palestinian_adj_freq.most_common(10)]

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.barplot(x=top_israeli_freqs, y=top_israeli_adjs, palette="Blues_d")
plt.title("Top 10 Adjectives (Israeli)", fontsize=12)
plt.xlabel("Frequency", fontsize=10)
plt.subplot(1, 2, 2)
sns.barplot(x=top_palestinian_freqs, y=top_palestinian_adjs, palette="Reds_d")
plt.title("Top 10 Adjectives (Palestinian)", fontsize=12)
plt.xlabel("Frequency", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "framing_adjectives.png"), dpi=600)
plt.close()

# Step 8: Mention Ratio
print("Calculating Mention Ratio...")
# Already calculated in sentiment analysis (israeli_mentions, palestinian_mentions)

# Step 9: Section Analysis
print("Performing Section Analysis...")
section_israeli_mentions = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in israeli_terms]))].groupby("section").size()
section_palestinian_mentions = df[df["headline"].str.lower().str.contains("|".join([term.lower() for term in palestinian_terms]))].groupby("section").size()

# Save section analysis results
with open(os.path.join(results_dir, "section_analysis.txt"), "w") as f:
    f.write("Section Distribution of Israeli Mentions:\n")
    f.write(section_israeli_mentions.to_string() + "\n")
    f.write("\nSection Distribution of Palestinian Mentions:\n")
    f.write(section_palestinian_mentions.to_string() + "\n")

# Visualization: Section Distribution
plt.figure(figsize=(10, 6))
section_israeli_mentions.plot(kind="bar", alpha=0.5, label="Israeli Mentions", color="blue")
section_palestinian_mentions.plot(kind="bar", alpha=0.5, label="Palestinian Mentions", color="red")
plt.title("Mentions by Section", fontsize=14)
plt.xlabel("Section", fontsize=12)
plt.ylabel("Number of Mentions", fontsize=12)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "section_distribution.png"), dpi=600)
plt.close()

print(f"\nAll analyses complete! Results saved to {results_dir} and high-DPI figures saved to {figures_dir}")
