import json
from pathlib import Path

examples_path = Path("prompts/examples/rollup_examples.json")

client_id = 18858422 

input_path = Path(f"prompts/examples/rollup_input_{client_id}.json")

with open(input_path) as f:
    input_data = json.load(f)

summary_output = """
Barbara reached out requesting information and has received a quote. She's planning to call back to book a tour. Based on her interest in **Cortland Park 83**, here’s how our offerings compare to the surrounding market.

#### Internal Property Options

**Cortland Park 83**
- **Average rent**: **$1,554** for **838 sq ft**
- **Minimum**: **$1,395** for **710 sq ft**
- **Maximum**: **$1,700** for **860 sq ft**
- **16 one-bedroom units currently available**
- **Current special**: Look and lease your apartment home and receive up to **one month free!**
- Highlights:
  - Spacious layouts compared to many nearby properties
  - Strong availability for flexible move-in timelines
  - Positioned as a top-tier offering relative to comps in both size and incentives

**Cortland Holcomb Bridge** (also internal)
- **Average rent**: **$1,460** for **735 sq ft**
- **Minimum**: **$1,428**
- **Maximum**: **$1,468**
- **5 one-bedroom units available**
- No active concessions at this time
- Highlights:
  - Compact and efficient layouts
  - Ideal for renters prioritizing budget and location
  - Offers a quieter community with Cortland quality finishes

#### Market Context (External Comparisons)
- Most nearby 1-bedrooms range from **$1,280–$1,691**, typically offering **700–850 sq ft**
- Notable deals currently available:
  - **Roswell Village**: **$1,500 OFF** first full month’s rent
  - **Randolph Perimeter**: **Up to 4 weeks free**
  - **Manchester At Mansell**: 1 month free
- Several properties like **IMT Deerfield**, **2200 Big Creek**, and **Walton Centennial** offer large square footage, but with higher average pricing and fewer consistent incentives

---

### Takeaways
- **Cortland Park 83** stands out with generous square footage, high availability, and an active leasing special that matches or exceeds competitor offers
- For a prospect like Barbara seeking clear value and flexibility, Cortland Park 83 is an excellent fit
- **Cortland Holcomb Bridge** offers a more compact alternative if budget sensitivity is a factor

Let’s follow up with unit-level options at Park 83 — including any with premium finishes or outdoor views — and offer to schedule her tour to take advantage of the current promotion.
""".strip()

example_entry_1 = {
    "input": input_data,
    "output": summary_output
}

client_id = 22215630 

input_path = Path(f"prompts/examples/rollup_input_{client_id}.json")

with open(input_path) as f:
    input_data = json.load(f)

summary_output = """
Samruddhi is relocating with a roommate and already has some familiarity with the area. She's looking for a 2-bedroom unit with **in-unit laundry**, **no first-floor options**, and **access to a fitness center**. Parking flexibility is noted, and she’s most interested in **Cortland Oak Lawn**.

#### Internal Property Option

**Cortland Oak Lawn**
- **Average rent**: **$2,235** for **1,037 sq ft**
- **Minimum**: **$2,235**, **Maximum**: **$2,235** — one consistent unit offering
- **1 two-bedroom unit currently available**
- No current concessions at this time
- Highlights:
  - Located in a central Oak Lawn location, near her existing social network
  - Includes in-unit laundry and access to a full fitness center
  - Cortland-level finishes and quality, with a quiet boutique-style feel
  - Strong match for her preferences — especially for layout and amenity needs
  - Unit likely not on the first floor due to limited availability (confirm with on-site)

#### Market Context (External Comparisons)
- Most comps fall between **$1,900–$2,750**, with average sizes around **1,100–1,250 sq ft**
- **4123 Cedar Springs** and **The Lucas Apartments** offer good value per square foot and more availability, but may lack Cortland's finishes or amenities
- Several external communities are running specials:
  - **Seville Uptown**: Up to **4 weeks free**
  - **Griffis Oak Lawn**: 1 month free or **$1,000 off** pre-leased homes
  - **4110 Fairmount**: One month free
  - **2929 Wycliff**: Up to **$1,000 off** first full month

---

### Takeaways
- **Cortland Oak Lawn** is a strong match for Samruddhi’s needs, with in-unit laundry, fitness center access, and a premium living experience — even without concessions
- While competitors offer short-term specials, none match the combination of quality, location, and layout alignment offered by Cortland
- Given limited availability, recommend scheduling a tour promptly to ensure the remaining 2-bed unit is still available

Let’s follow up with unit details and confirm floor level and amenity access before booking a showing.
""".strip()

example_entry_2 = {
    "input": input_data,
    "output": summary_output
}

# --- Load existing examples ---
if examples_path.exists():
    with open(examples_path) as f:
        existing = json.load(f)
else:
    existing = []

# --- Append new examples and save ---
existing.append(example_entry_1)
existing.append(example_entry_2)

with open(examples_path, "w") as f:
    json.dump(existing, f, indent=2)