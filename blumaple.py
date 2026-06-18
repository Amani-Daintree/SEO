import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import os

INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"

# 150-160 chars is the SEO best-practice range (Google truncates around there).
META_MAX_LEN = 160

# Create input file if missing
if not os.path.exists(INPUT_FILE):
    pd.DataFrame(columns=[
        "asin",
        "title"
    ]).to_csv(INPUT_FILE, index=False)

    print("input.csv created. Add data and run again.")
    exit()

# Read input
df = pd.read_csv(INPUT_FILE)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Validate columns
required_columns = ["asin", "title"]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

headers = {
    "User-Agent": "Mozilla/5.0"
}

results = []


# ==========================
# SEO HELPERS
# ==========================

def clean_text(text):
    """Collapse all whitespace/newlines into single spaces."""
    return " ".join(str(text).split())


def trim_to_length(text, max_len=META_MAX_LEN):
    """Trim to max_len without cutting a word in half."""
    text = clean_text(text)

    if len(text) <= max_len:
        return text

    cut = text[:max_len].rsplit(" ", 1)[0]
    cut = cut.rstrip(" ,;:-")
    return cut


def clean_product_name(title):
    """
    Pull the main product name out of a messy title.
    The real product name is almost always the part before the
    first comma or pipe (e.g. brand + model + type).
    """
    name = clean_text(title)

    for sep in ["|", ","]:
        if sep in name:
            name = name.split(sep)[0].strip()

    # Keep it reasonable in length (first ~14 words)
    words = name.split()
    if len(words) > 14:
        name = " ".join(words[:14])

    return clean_text(name)


def category_benefit(title):
    """A short, fitting benefit line based on the product type."""
    t = str(title).lower()

    if "headset" in t:
        return "immersive sound and clear communication for gaming and entertainment."
    elif "alarm clock" in t:
        return "dependable alarms and handy bedside features for everyday use."
    elif "keyboard" in t and "mouse" in t:
        return "comfortable typing and precise control for work and play."
    elif "keyboard" in t:
        return "comfortable, responsive typing for work and play."
    elif "camera" in t:
        return "capture sharp, memorable photos with easy everyday use."
    elif "speaker" in t:
        return "rich, wireless audio and reliable performance for daily listening."
    elif "mouse" in t:
        return "smooth tracking and ergonomic control for work and study."
    else:
        return "trusted quality and dependable performance for everyday value."


def build_meta_description(title):
    """
    Build a neat, meaningful, SEO-friendly description that stays
    faithful to the title's meaning:
      [real product name]. [Fitting benefit]
    """
    name = clean_product_name(title)
    benefit = category_benefit(title)

    # Capitalize the first letter of the benefit so it reads as a sentence
    benefit = benefit[0].upper() + benefit[1:]

    description = f"{name} {benefit}"
    return trim_to_length(description)


# ==========================
# MAIN LOOP
# ==========================

for _, row in df.iterrows():

    asin = str(row["asin"]).strip()
    title = str(row["title"]).strip()

    canonical_product = ""

    try:

        search_url = (
            f"https://blumaple.com/search?q={quote_plus(title)}"
        )

        response = requests.get(
            search_url,
            headers=headers,
            timeout=30
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        links = soup.find_all("a", href=True)

        for link in links:

            href = link["href"]

            if "/products/" in href:

                if href.startswith("/"):
                    canonical_product = (
                        "https://blumaple.com" + href
                    )
                else:
                    canonical_product = href

                canonical_product = (
                    canonical_product.split("?")[0]
                )

                break

    except Exception as e:
        print(f"Error: {title}")
        print(e)

    results.append({
        "asin": asin,
        "title": title,
        "canonical_product": canonical_product,
        "meta_description": build_meta_description(title)
    })

    time.sleep(1)

# Save output
output_df = pd.DataFrame(results)

output_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Done! Output saved to {OUTPUT_FILE}")