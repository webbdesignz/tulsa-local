#!/usr/bin/env python3
"""
TulsaLocal Business Scraper v2
Pulls businesses from Google Places API (New) and outputs HTML cards.

Usage:
  python3 tulsa_scraper_v2.py
  python3 tulsa_scraper_v2.py --city "Broken Arrow"
  python3 tulsa_scraper_v2.py --city "Jenks"
  python3 tulsa_scraper_v2.py --city "Owasso"
  python3 tulsa_scraper_v2.py --city "Bixby"
  python3 tulsa_scraper_v2.py --city "Sand Springs"
  python3 tulsa_scraper_v2.py --city "Sapulpa"
"""

import urllib.request
import json
import time
import os
import sys

# ============================================================
# PASTE YOUR GOOGLE PLACES API KEY HERE
API_KEY = "AIzaSyBspNJBusEYgLczTiV52zU5m-fhGT7RNrA"
# ============================================================

# City centers for each suburb
CITY_CENTERS = {
    "Tulsa":        (36.1540, -95.9928),
    "Broken Arrow": (36.0526, -95.7906),
    "Jenks":        (35.9914, -95.9734),
    "Owasso":       (36.2695, -95.8547),
    "Bixby":        (35.9420, -95.8828),
    "Sand Springs": (36.1395, -96.1089),
    "Sapulpa":      (35.9987, -96.1147),
}

SEARCH_RADIUS = 12000  # 12km — tighter for suburbs

CATEGORIES = [
    ("restaurant",          "food",         "🍽 Food & Dining",      "#FEF0E8", "#B84A15"),
    ("bar",                 "food",         "🍺 Bar & Lounge",       "#FEF0E8", "#B84A15"),
    ("cafe",                "food",         "☕ Cafe",               "#FEF0E8", "#B84A15"),
    ("bakery",              "food",         "🎂 Bakery",             "#FEF0E8", "#B84A15"),
    ("dentist",             "health",       "🏥 Health",             "#E5F7F0", "#1A7A55"),
    ("doctor",              "medical",      "🩺 Medical",            "#E5F7F0", "#1A7A55"),
    ("gym",                 "fitness",      "🏋 Fitness",            "#FDF1E0", "#995A05"),
    ("hair_care",           "beauty",       "💅 Beauty",             "#FAE8F3", "#991555"),
    ("car_repair",          "auto",         "🚗 Auto",               "#FAEBEB", "#991515"),
    ("pet_store",           "pet",          "🐾 Pet Services",       "#E8F5E9", "#2E7D32"),
    ("veterinary_care",     "pet",          "🐾 Pet Services",       "#E8F5E9", "#2E7D32"),
    ("home_goods_store",    "retail",       "🛍 Retail",             "#EEEAF8", "#4A3D99"),
    ("clothing_store",      "retail",       "🛍 Retail",             "#EEEAF8", "#4A3D99"),
    ("florist",             "home",         "🏡 Home & Garden",      "#F1F8E9", "#558B2F"),
    ("school",              "education",    "🎓 Education",          "#E8EAF6", "#3949AB"),
    ("insurance_agency",    "financial",    "💰 Financial",          "#E8F5E9", "#2E7D32"),
    ("roofing_contractor",  "construction", "🔨 Construction",       "#FBE9E7", "#BF360C"),
    ("general_contractor",  "construction", "🔨 Construction",       "#FBE9E7", "#BF360C"),
    ("lawyer",              "services",     "🔧 Services",           "#E5F0FA", "#175CA0"),
]

PIN_SVG = '<svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>'
PHONE_SVG = '<svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.68A2 2 0 012 .14h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92v2z"/></svg>'
STAR_SVG = '<svg width="10" height="10" viewBox="0 0 24 24" fill="#F4A05A" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'


def search_places(query, city, lat, lng):
    url = "https://places.googleapis.com/v1/places:searchText"
    payload = {
        "textQuery": f"{query} in {city} Oklahoma",
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": SEARCH_RADIUS
            }
        },
        "maxResultCount": 20,
        "languageCode": "en"
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.rating,places.userRatingCount,places.websiteUri,places.photos,places.businessStatus"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"  Error: {e}")
        return {}


def get_photo_url(photo_name):
    if not photo_name:
        return None
    return f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=600&key={API_KEY}"


def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text


def phone_to_tel(phone):
    if not phone:
        return ""
    digits = ''.join(c for c in phone if c.isdigit())
    return f"+1{digits}" if len(digits) == 10 else f"+{digits}"


def make_card(place, category_data, seen_names, city):
    place_type, cat_key, cat_label, cat_bg, cat_color = category_data
    name = place.get("displayName", {}).get("text", "")
    if not name or name in seen_names:
        return None
    if place.get("businessStatus") == "PERMANENTLY_CLOSED":
        return None
    seen_names.add(name)

    address = place.get("formattedAddress", f"{city}, OK")
    address = address.replace(", USA", "").replace(", United States", "")
    phone = place.get("nationalPhoneNumber", "")
    rating = place.get("rating", "")
    review_count = place.get("userRatingCount", "")
    photos = place.get("photos", [])
    photo_url = get_photo_url(photos[0].get("name")) if photos else None
    slug = slugify(name)
    tel = phone_to_tel(phone)

    if photo_url:
        photo_html = f'<img src="{photo_url}" alt="{name} {city} OK" loading="lazy">'
    else:
        emoji = cat_label.split()[0]
        photo_html = f'<div class="card-photo-placeholder" style="background:{cat_bg}20">{emoji}</div>'

    rating_html = ""
    if rating and review_count:
        rating_html = f'<div class="card-photo-rating">{STAR_SVG} {rating} <span style="opacity:0.6">({review_count:,})</span></div>'

    if phone and tel:
        call_btn = f'<a href="tel:{tel}" class="btn-call">{PHONE_SVG} Call</a>'
    elif place.get("websiteUri"):
        call_btn = f'<a href="{place["websiteUri"]}" target="_blank" class="btn-call">Website</a>'
    else:
        call_btn = ""

    card = f"""
    <div class="biz-card" data-category="{cat_key}" data-name="{name}" data-is-open="true">
      <div class="card-photo">{photo_html}<div class="card-photo-badge"><span class="chamber-badge">&#10003; Verified</span></div>{rating_html}</div>
      <div class="card-body">
        <div class="biz-name">{name}</div>
        <span class="category-badge" style="background:{cat_bg};color:{cat_color}">{cat_label}</span>
        <div class="card-details">
          <div class="detail-row">{PIN_SVG}<span>{address}</span></div>
          {"<div class='detail-row'>" + PHONE_SVG + "<span>" + phone + "</span></div>" if phone else ""}
        </div>
      </div>
      <div class="card-footer">
        <a href="../businesses/{slug}.html" class="view-btn">View Listing &#8594;</a>
        <div class="card-actions">{call_btn}</div>
      </div>
    </div>"""
    return card


def main():
    # Parse city argument
    city = "Tulsa"
    if "--city" in sys.argv:
        idx = sys.argv.index("--city")
        if idx + 1 < len(sys.argv):
            city = sys.argv[idx + 1]

    if city not in CITY_CENTERS:
        print(f"Unknown city: {city}")
        print(f"Available: {', '.join(CITY_CENTERS.keys())}")
        return

    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("ERROR: Add your API key at the top of this script.")
        return

    lat, lng = CITY_CENTERS[city]
    city_slug = slugify(city)

    print(f"TulsaLocal Scraper v2 — {city}, OK")
    print("=" * 40)

    all_cards = []
    seen_names = set()
    total = 0

    for place_type, cat_key, cat_label, cat_bg, cat_color in CATEGORIES:
        query = place_type.replace("_", " ")
        print(f"Searching: {cat_label}...")
        result = search_places(query, city, lat, lng)
        places = result.get("places", [])
        count = 0
        for place in places:
            card = make_card(place, (place_type, cat_key, cat_label, cat_bg, cat_color), seen_names, city)
            if card:
                all_cards.append(card)
                count += 1
                total += 1
        print(f"  Found {count} businesses")
        time.sleep(0.3)

    print(f"\nTotal: {total} businesses in {city}")

    # Save raw cards
    raw_path = os.path.expanduser(f"~/Desktop/cards_{city_slug}.html")
    with open(raw_path, "w") as f:
        f.write("\n".join(all_cards))

    # Save preview
    preview_path = os.path.expanduser(f"~/Desktop/preview_{city_slug}.html")
    with open(preview_path, "w") as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{city} Cards Preview</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{ --navy:#1B2B40;--orange:#D96B2D;--orange-light:#F4A05A;--cream:#FDF5E8;--cream-dark:#F0E6D0;--white:#FFFFFF;--text:#1B2B40;--text-muted:#6B7A8D;--border:#E2D9C8;--radius:14px; }}
body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: var(--cream); padding: 2rem; }}
h1 {{ font-family: 'Playfair Display', serif; color: var(--navy); margin-bottom: 1.5rem; }}
.business-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.25rem; }}
.biz-card {{ background: var(--white); border: 1.5px solid var(--border); border-radius: var(--radius); overflow: hidden; display: flex; flex-direction: column; }}
.card-photo {{ position: relative; height: 160px; overflow: hidden; background: #f0e6d0; }}
.card-photo img {{ width: 100%; height: 100%; object-fit: cover; }}
.card-photo-placeholder {{ width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }}
.card-photo-badge {{ position: absolute; top: 8px; left: 8px; }}
.card-photo-rating {{ position: absolute; bottom: 8px; right: 8px; background: rgba(27,43,64,0.85); color: #FDF5E8; font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.55rem; border-radius: 6px; display: flex; align-items: center; gap: 0.3rem; }}
.chamber-badge {{ display: inline-flex; align-items: center; background: #EEF5FF; color: #1A5CA0; font-size: 0.68rem; font-weight: 600; padding: 0.18rem 0.5rem; border-radius: 4px; border: 1px solid #C0D8F4; }}
.card-body {{ padding: 1.25rem 1.25rem 0.75rem; flex: 1; }}
.biz-name {{ font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem; }}
.category-badge {{ display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.25rem 0.75rem; border-radius: 100px; font-size: 0.73rem; font-weight: 600; margin-bottom: 0.85rem; }}
.card-details {{ display: flex; flex-direction: column; gap: 0.45rem; }}
.detail-row {{ display: flex; align-items: flex-start; gap: 0.6rem; font-size: 0.83rem; color: var(--text-muted); }}
.card-footer {{ padding: 0.75rem 1.25rem; border-top: 1px solid var(--cream-dark); display: flex; align-items: center; justify-content: space-between; }}
.view-btn {{ font-size: 0.8rem; font-weight: 600; color: var(--orange); text-decoration: none; }}
.btn-call {{ display: flex; align-items: center; gap: 0.4rem; padding: 0 0.85rem; height: 32px; background: var(--navy); color: var(--cream); border: none; border-radius: 8px; font-size: 0.78rem; font-weight: 600; text-decoration: none; }}
.card-actions {{ display: flex; gap: 0.5rem; }}
</style></head><body>
<h1>{city}, OK — Card Preview ({total} businesses)</h1>
<div class="business-grid">
{"".join(all_cards)}
</div></body></html>""")

    print(f"\nFiles saved to Desktop:")
    print(f"  cards_{city_slug}.html — paste into neighborhood page")
    print(f"  preview_{city_slug}.html — open in browser to preview")
    print(f"\nDone!")


if __name__ == "__main__":
    main()
