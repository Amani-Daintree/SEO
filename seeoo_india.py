import csv
import random
from pathlib import Path
import re

def extract_crawler_keywords(title):
    """
    Intelligently extracts 5 top-rated, high-intent Google Shopping 
    and SEO keywords tailored exactly to the specific product title.
    """
    title_clean = title.strip()
    title_lower = title_clean.lower()
    brand_device = ""
    if "surface pro" in title_lower:
        brand_device = "surface pro"
    elif "galaxy z fold" in title_lower or "z fold" in title_lower:
        brand_device = "galaxy z fold"
    elif "galaxy" in title_lower:
        brand_device = "galaxy"
    elif "ipad" in title_lower:
        brand_device = "ipad"
    elif "samsung" in title_lower:
        brand_device = "samsung"
    elif "microsoft" in title_lower:
        brand_device = "microsoft"
    elif "black" in title_lower and "decker" in title_lower:
        brand_device = "black decker"
    prod_cat = ""
    if "keyboard case" in title_lower:
        prod_cat = "keyboard case"
    elif "keyboard mouse" in title_lower:
        prod_cat = "keyboard mouse set"
    elif "tab keyboard" in title_lower or "tablet keyboard" in title_lower:
        prod_cat = "tablet keyboard"
    elif "cooler" in title_lower:
        prod_cat = "phone cooler"
    elif "garment steamer" in title_lower or "clothes steamer" in title_lower:
        prod_cat = "garment steamer"
    elif "steamer" in title_lower:
        prod_cat = "steamer"
    if not prod_cat:
        words = [w for w in re.findall(r'\b\w{4,}\b', title_lower) if w not in {"with", "that", "this", "your", "online", "best"}]
        prod_cat = " ".join(words[:2]) if words else "product"
    keywords_pool = []
    if brand_device and prod_cat:
        keywords_pool.append(f"{brand_device} {prod_cat}")
        keywords_pool.append(f"buy {brand_device} {prod_cat}")
        keywords_pool.append(f"best {brand_device} {prod_cat}")
        keywords_pool.append(f"{brand_device} {prod_cat} online")
    else:
        keywords_pool.append(prod_cat)
        keywords_pool.append(f"buy {prod_cat}")
        keywords_pool.append(f"best {prod_cat}")
        keywords_pool.append(f"{prod_cat} online")
    keywords_pool.extend([
        f"top rated {prod_cat}",
        f"premium {prod_cat}",
        f"best selling {prod_cat}"
    ])
    final_keywords = []
    for kw in keywords_pool:
        kw_clean = " ".join(kw.split()).strip()
        if kw_clean not in final_keywords and len(final_keywords) < 5:
            final_keywords.append(kw_clean)
    while len(final_keywords) < 5:
        final_keywords.append(prod_cat)
    return ", ".join(final_keywords[:5])
def extract_seo_title_noun(title):
    """
    Intelligently extracts the most important device name + product type 
    from anywhere in the title, strictly avoiding raw starting text fallback.
    """
    title_lower = title.strip().lower()
    device = ""
    if "surface pro" in title_lower:
        device = "Surface Pro"
    elif "galaxy" in title_lower:
        device = "Galaxy"
    elif "z fold" in title_lower:
        fold_match = re.search(r"z\s*fold\s*\d+", title_lower)
        device = fold_match.group(0).title() if fold_match else "Galaxy Z Fold"
    elif "ipad" in title_lower:
        device = "iPad"
    elif "samsung" in title_lower:
        device = "Samsung"
    elif "microsoft" in title_lower:
        device = "Microsoft"
    product_type = ""
    if "keyboard mouse" in title_lower or "mouse pen" in title_lower:
        product_type = "Keyboard Mouse Set"
    elif "keyboard case" in title_lower:
        product_type = "Keyboard Case"
    elif "tab keyboard" in title_lower or "tablet keyboard" in title_lower:
        product_type = "Tablet Keyboard"
    elif "cooler" in title_lower:
        product_type = "Phone Cooler"
    elif "steamer" in title_lower:
        product_type = "Garment Steamer"
    else:
        product_type = "Gaming Accessory"
    if device:
        if device.lower() in product_type.lower():
            return product_type.title()
        return f"{device} {product_type}"
    important_words = []
    words = re.findall(r'\b[a-zA-Z0-9_]{3,}\b', title.strip())
    ignore_words = {"with", "and", "for", "the", "online", "buy", "best", "price", "at", "more", "from", "that", "this", "your", "portable", "flip", "leather", "stand", "bluetooth", "wireless"}
    for w in words:
        if w.lower() not in ignore_words:
            important_words.append(w)
            if len(important_words) >= 3:
                break                
    if important_words:
        fallback_noun = " ".join(important_words).title()
        fallback_noun = re.sub(r'\s*(Keyboard Case|Tablet Keyboard|Garment Steamer|Phone Cooler)$', '', fallback_noun, flags=re.IGNORECASE).strip()
        return f"{fallback_noun} {product_type}"
    return product_type
def smart_truncate(text, max_len):
    """Safely truncates string at a word boundary so words never get cut in half."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(' ')
    if last_space != -1:
        return truncated[:last_space].strip()
    return truncated.strip()
def generate_seo(title, asin):
    clean = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", clean)
    slug = slug.strip("-")
    important_noun = extract_seo_title_noun(title)
    brand_suffix = " | Waterberry India"
    max_noun_len = 50 - len(brand_suffix)
    clean_noun = smart_truncate(important_noun, max_noun_len)
    seo_title = f"{clean_noun}{brand_suffix}"
    features = []
    if "touchpad" in clean or "mouse" in clean:
        features.append("touchpad")
    if "backlit" in clean or "7-color" in clean:
        features.append("backlit keys")
    if "leather" in clean:
        features.append("premium leather protective cover")
    if "magnetic" in clean or "detachable" in clean:
        features.append("magnetic bluetooth design")
    else:
        if not any("cover" in f for f in features):
            features.append("protective cover")
    if len(features) >= 2:
        feature_text = f"with {features[0]} and {features[1]}"
    elif len(features) == 1:
        feature_text = f"with {features[0]}"
    else:
        feature_text = "with wireless bluetooth connectivity"
    desc_layouts = [
        f"Shop {clean_noun} {feature_text} layout ideal for smooth typing work study and travel use",
        f"Buy {clean_noun} {feature_text} optimized perfectly for fast typing remote work and travel use",
        f"Get this {clean_noun} {feature_text} designed seamlessly for responsive typing work and travel use"
    ]
    description = random.choice(desc_layouts).strip()
    description = description.replace(".", "")
    if len(description) > 150:
        description = smart_truncate(description, 150)
    seo_keywords = extract_crawler_keywords(title)
    canonical = f"https://www.thewaterberry.com/product/{asin}/{slug}"
    return {
        "asin": asin,
        "title": title,
        "seo_title": seo_title,
        "description": description,
        "seo_keywords": seo_keywords,
        "canonical": canonical,
    }
# input_file = "input.csv"
# output_file = "output.csv"


input_file = Path("input.csv")
output_file = Path("output.csv")
try:
    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        next(reader, None)
        with open(
            output_file, mode="w", newline="", encoding="utf-8"
        ) as outfile:
            writer = csv.writer(outfile)
            writer.writerow(
                [
                    "ASIN",
                    "Title",
                    "SEO Title",
                    "Description",
                    "SEO_Keywords",
                    "Canonical",
                ]
            )
            for row in reader:
                if not row or len(row) < 2:
                    continue
                asin = row[0].strip()
                title = row[1].strip()
                seo_data = generate_seo(title, asin)
                writer.writerow(
                    [
                        seo_data["asin"],
                        seo_data["title"],
                        seo_data["seo_title"],
                        seo_data["description"],
                        seo_data["seo_keywords"],
                        seo_data["canonical"],
                    ]
                )
    print("SEO CSV Generated Successfully")
except FileNotFoundError:
    print(
        f"Error: Could not find '{input_file}'. Please ensure it is in the same directory."
    )