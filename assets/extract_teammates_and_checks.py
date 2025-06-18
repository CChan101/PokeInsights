import re
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time

def extract_teammates_and_checks(text):
    teammates_data = []
    checks_data = []

    sections = re.split(r'\+\-+\+\s*\n\s*\|\s*(.*?)\s*\|\s*\n\s*\+\-+\+', text)

    for name, block in zip(sections[1::2], sections[2::2]):
        current_pokemon = name.strip()
        lines = block.splitlines()
        section = None

        for line in lines:
            line = line.strip()

            if line.startswith('| Teammates'):
                section = 'teammates'
                continue
            elif line.startswith('| Checks and Counters'):
                section = 'checks'
                continue
            elif line.startswith('+') or not line.startswith('|'):
                section = None
                continue

            if section == 'teammates' and '%' in line:
                match = re.match(r'\|\s*(.*?)\s+([\d.]+)%\s*\|', line)
                if match:
                    teammate, usage = match.groups()
                    teammates_data.append({
                        "Pokemon": current_pokemon,
                        "Teammate": teammate.strip(),
                        "Usage %": float(usage)
                    })

            elif section == 'checks':
                match = re.match(r'\|\s*(.*?)\s+([\d.]+)\s+\((.*?)\)\s*\|', line)
                if match:
                    check, usage, performance = match.groups()
                    checks_data.append({
                        "Pokemon": current_pokemon,
                        "Check": check.strip(),
                        "Usage %": float(usage),
                        "Performance": performance.strip()
                    })

    return pd.DataFrame(teammates_data), pd.DataFrame(checks_data)

# Set start and end months
start = datetime.strptime("2022-10", "%Y-%m")
end = (datetime.today().replace(day=1) - relativedelta(months=1))
months_available = []
current = end
while current >= start:
    months_available.append(current.strftime("%Y-%m"))
    current -= relativedelta(months=1)

tier_list = ["gen9ubers", "gen9ou", "gen9uu", "gen9ru", "gen9nu", "gen9pu", "gen9zu",
             "gen8ou", "gen7ou", "gen6ou", "gen5ou", "gen4ou", "gen3ou", "gen2ou", "gen1ou"]
ladder_ranking = ["0", "1500", "1630", "1695", "1760", "1825"]
url_template = 'https://www.smogon.com/stats/{}/moveset/{}-{}.txt'

all_teammates = []
all_checks = []

for month in months_available:
    for tier in tier_list:
        for rating in ladder_ranking:
            url = url_template.format(month, tier, rating)
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch {url}")
                    continue
                text = response.text

                df_teammates, df_checks = extract_teammates_and_checks(text)
                if not df_teammates.empty:
                    df_teammates["Month"] = month
                    df_teammates["Tier"] = tier
                    df_teammates["Rating"] = rating
                    all_teammates.append(df_teammates)

                if not df_checks.empty:
                    df_checks["Month"] = month
                    df_checks["Tier"] = tier
                    df_checks["Rating"] = rating
                    all_checks.append(df_checks)

                print(f"Processed: {month}, {tier}, rating {rating}")
                time.sleep(1)  # Be polite to the server
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue

for df in all_teammates:
    df['Rating'] = df['Rating'].replace('0', '1000')
for df in all_checks:
    df['Rating'] = df['Rating'].replace('0', '1000')

# Combine all results into final DataFrames
final_teammates = pd.concat(all_teammates, ignore_index=True)
final_checks = pd.concat(all_checks, ignore_index=True)

# Save to CSV
final_teammates.to_csv("smogon_teammates_data.csv", index=False)
final_checks.to_csv("smogon_checks_data.csv", index=False)

print("Data saved to CSV.")