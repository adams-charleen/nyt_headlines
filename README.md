## 🧠 What is Sentiment Analysis?

Sentiment analysis is a natural language processing (NLP) technique used to determine the emotional tone or attitude expressed in a piece of text, such as a headline, review, or social media post. It typically categorizes text as **positive**, **negative**, or **neutral**, and can sometimes detect more specific emotions like happiness, anger, or sadness.

In this case, sentiment analysis is applied to headlines from *The New York Times (NYT)* to assess how the newspaper portrays topics related to **Israeli** and **Palestinian** issues.

---

## ⚙️ How the Sentiment Analysis Works

This sentiment analysis focuses on NYT headlines that mention specific terms related to Israeli or Palestinian topics. The process uses a tool called **VADER** (Valence Aware Dictionary and sEntiment Reasoner), which is particularly effective for analyzing short texts like headlines.

### 1. 🛠 Tools and Setup

**VADER** is a lexicon and rule-based sentiment analysis tool designed for short texts. It assigns sentiment scores using:

- A dictionary of words and phrases
- Punctuation emphasis (e.g., `"Great!"` vs. `"Great"`)
- Degree modifiers (e.g., `"very good"` vs. `"good"`)

**Key Terms** used to identify headlines:
- **Israeli terms:** `"Israel"`, `"Israeli"`, `"IDF"`
- **Palestinian terms:** `"Palestinian"`, `"Palestine"`, `"Hamas"`, `"Gaza"`

---

### 2. 📏 Calculating Sentiment Scores

For each headline, VADER’s `polarity_scores` method computes a **compound sentiment score**, ranging from:

- `-1`: Most negative sentiment  
- `0`: Neutral sentiment  
- `+1`: Most positive sentiment

**Example:**  
- `"Israel achieves breakthrough"` → compound score ≈ `0.7`  
- `"Gaza faces crisis"` → compound score ≈ `-0.6`

---

### 3. 🧮 Categorizing Headlines

The script checks each headline for Israeli or Palestinian terms:

- If it contains an **Israeli** term, its score is added to `israeli_sentiments`, and the count of Israeli mentions is incremented.
- If it contains a **Palestinian** term, the score is added to `palestinian_sentiments`, and the Palestinian mention count increases.

> 💡 Headlines that mention **both** (e.g., `"Israel and Gaza clash"`) contribute to **both** categories.

---

### 4. 📊 Summarizing Results

After processing all headlines:

- **Average sentiment** for Israeli mentions = sum of `israeli_sentiments` ÷ number of Israeli mentions  
- **Average sentiment** for Palestinian mentions = sum of `palestinian_sentiments` ÷ number of Palestinian mentions

Also reported:
- Total **number of mentions** for each group
- **Mention ratio** (e.g., `2:1` if Israeli terms appear twice as often)

---

### 5. 📁 Output and Visualization

- `sentiment_analysis.txt`: Contains the final summary of average sentiments, mention counts, and mention ratio.
- **Bar Plot**: Comparison of average sentiment scores for Israeli vs. Palestinian mentions.
- **Histogram**: Distribution of sentiment scores to show whether the tone is centered or polarized.

---
