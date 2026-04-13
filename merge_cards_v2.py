import os

index_path = os.path.expanduser("~/Desktop/tulsa-local/index.html")
cards_path = os.path.expanduser("~/Desktop/tulsa_cards_raw.html")

with open(index_path, "r") as f:
    index = f.read()

with open(cards_path, "r") as f:
    cards = f.read()

start_marker = '    <!-- Mahogany Prime Steakhouse -->'
end_marker = '  </div>\n</section>\n\n<!-- NEWSLETTER -->'

start_pos = index.find(start_marker)
end_pos = index.find(end_marker)

if start_pos == -1:
    print("ERROR: Could not find start marker")
    exit()
if end_pos == -1:
    print("ERROR: Could not find end marker")
    exit()

new_index = index[:start_pos] + cards.strip() + "\n\n  </div>\n</section>\n\n<!-- NEWSLETTER -->" + index[end_pos + len(end_marker):]

with open(index_path, "w") as f:
    f.write(new_index)

print(f"Done! index.html updated with {cards.count('biz-card')} businesses.")
