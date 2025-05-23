import requests
from bs4 import BeautifulSoup
import pandas as pd
import dash
from datetime import datetime
from dateutil.relativedelta import relativedelta

print("Running...")

pd.set_option('display.max_colwidth', None)
# Define the URL of the page to scrape
sprite_url = 'https://pokemondb.net/sprites'
response = requests.get(sprite_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all infocard elements
pokemon_cards = soup.select('a.infocard')
sprite_list = []

# Loop through each infocard element to extract the data
for card in pokemon_cards:
    name = card.text.strip()  # Extract the Pokémon name

    # Find the image source within the picture tag
    img_tag = card.find('img')
    img_url = img_tag['src'] if img_tag else None

    # Append the data to the list
    sprite_list.append({'Name': name, 'Image URL': img_url})

sprite_links = pd.DataFrame(sprite_list)
# Get pokemon stats from "list_of_pokemon_df.csv"
pokemon_stats = pd.read_csv("list_of_pokemon_df.csv")

# Set start and end months
start = datetime.strptime("2022-10", "%Y-%m")
# Use last month as the endpoint
end = (datetime.today().replace(day=1) - relativedelta(months=1))
months_avaliable = []
current = end
while current >= start:
    months_avaliable.append(current.strftime("%Y-%m"))
    current -= relativedelta(months=1)

tier_list = ["gen9ubers", "gen9ou", "gen9uu", "gen9ru", "gen9nu", "gen9pu", "gen9zu", "gen8ou", "gen7ou", "gen6ou", "gen5ou", "gen4ou", "gen3ou", "gen2ou", "gen1ou"]
ladder_ranking = ["0", "1500", "1630", "1760", "1825"] #1825 is the highest measured ranking threshold for OU, while 1760 is the highest threshold for other tiers

# List to hold the dataframes
list_df = []

app = dash.Dash(__name__)

url = 'https://www.smogon.com/stats/{}/{}-{}.txt'

# Set the max amount of column
pd.set_option('display.max_columns', 7)

# Read the csv with each loop iteration until you get the full list
for months in months_avaliable:
    for tier in tier_list:
        for ranking in ladder_ranking:
            try:
                # Keep going through each tier/generation in successive for loop
                full_link = url.format(months, tier, ranking)

                # Read the link every iteration
                new_df = pd.read_csv(full_link)

                # Manipulate Data until you get seperate columns
                new_df.columns = ['All']
                new_df = new_df.drop([0, 1, 2, 3, ])
                split_lines = new_df['All'].str.split('|', n=7, expand=True)
                new_df['Rank'] = split_lines[1]
                new_df['Name'] = split_lines[2]
                new_df['Usage Rate'] = split_lines[3]
                new_df['Raw Usage'] = split_lines[4]
                new_df['Raw %'] = split_lines[5]
                new_df['Real Usage'] = split_lines[6]
                new_df['Real %'] = split_lines[7]
                new_df.drop(columns=["All"], inplace=True)
                new_df.dropna(inplace=True)
                columns_to_drop = ['Real Usage', 'Real %']
                new_df = new_df.drop(columns=columns_to_drop)
                new_df['Tier'] = tier
                new_df['Month'] = months
                new_df['Ranking'] = ranking

                # Append the new DataFrame to the list
                list_df.append(new_df)
            except Exception as e:
                print(f"Error processing {months} {tier} {ranking}: {e}")
                continue  # Continue with the next tier instead of breaking the month loop

# Concatenate all DataFrames in the list into one DataFrame
df_final = pd.concat(list_df, ignore_index=True)

# Normalize the 'Name' and Stats columns in each DataFrame
sprite_links['Name'] = sprite_links['Name'].str.strip().str.title()
df_final['Name'] = df_final['Name'].str.strip().str.title()
pokemon_stats['Name'] = pokemon_stats['Name'].str.strip().str.title()
pokemon_stats['HP'] = pokemon_stats['HP'].astype(str)
pokemon_stats['HP'] = pokemon_stats['HP'].str.strip().str.title()

# Recreate the mapping Series with normalized names
name_to_image_url = sprite_links.set_index('Name')['Image URL']
pokemon_stats_unique = pokemon_stats.drop_duplicates(subset='Name', keep='first')
hp = pokemon_stats_unique.set_index('Name')['HP']
attack = pokemon_stats_unique.set_index('Name')['Attack']
defense = pokemon_stats_unique.set_index('Name')['Defense']
sp_attack = pokemon_stats_unique.set_index('Name')['Sp.Attack']
sp_defense = pokemon_stats_unique.set_index('Name')['Sp.Defense']
speed = pokemon_stats_unique.set_index('Name')['Speed']
type_one = pokemon_stats_unique.set_index('Name')['Type1']
type_two = pokemon_stats_unique.set_index('Name')['Type2']

# Map the 'Name' column in df_final to 'Sprite Links' using the created mapping Series
df_final['Sprite Links'] = df_final['Name'].map(name_to_image_url)
df_final['HP'] = df_final['Name'].map(hp)
df_final['Attack'] = df_final['Name'].map(attack)
df_final['Defense'] = df_final['Name'].map(defense)
df_final['Sp.Attack'] = df_final['Name'].map(sp_attack)
df_final['Sp.Defense'] = df_final['Name'].map(sp_defense)
df_final['Speed'] = df_final['Name'].map(speed)
df_final['Type1'] = df_final['Name'].map(type_one)
df_final['Type2'] = df_final['Name'].map(type_two)

# Get BST of each pokemon
columns_to_sum = ['HP', 'Attack', 'Defense', "Sp.Attack", "Sp.Defense", "Speed"]

# Convert columns to numeric, forcing any errors to NaN
df_final[columns_to_sum] = df_final[columns_to_sum].apply(pd.to_numeric, errors='coerce')
df_final['BST'] = df_final[columns_to_sum].sum(axis=1)

# Convert entire 'Month' column to datetime format
df_final['Month'] = pd.to_datetime(df_final['Month'], format='%Y-%m')
df_final['Month'] = df_final['Month'].dt.strftime('%Y-%m')
# Convert entire 'Usage' column to numeric
df_final['Usage Rate'] = df_final['Usage Rate'].str.replace('%', '')
df_final['Usage Rate'] = df_final['Usage Rate'].apply(pd.to_numeric)

df_final.to_excel('sample_data.xlsx')
print("Data successfully scraped!")

