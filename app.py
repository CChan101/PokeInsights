from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter

import os
import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html, Input, Output

app = dash.Dash(__name__)
app.title = 'PokeInsights'
server = app.server

colors = {
    # Change color of background
    'background_color': '#404040',
    'text': '#FFFFFF'
}
df_final = pd.read_excel("sample_data.xlsx")
df_teammates = pd.read_csv("smogon_teammates_data.csv")
df_checks = pd.read_csv("smogon_checks_data.csv")

app.layout = html.Div(
    style={'backgroundColor': colors['background_color'], 'color': colors['text'], 'height': '100vh',
           "marginTop": "0px",
           "marginBottom": "0px",
           "paddingTop": "12.5px",
           "paddingBottom": "12.5px",
           "paddingLeft": "10px",
           "textAlign": "center", }, className='dynamic-width',
    children=[
        html.Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        html.Img(src=r"/assets/PokeInsights Logo.png",
                 className='image-zoom', style={'textAlign': 'center'}),
        html.H4(
            "Hello! An easy-to-use tool for gathering insights on statistics within competitive Pokemon(Smogon) and "
            "measuring trends such as usage rate. Use the dropdown and click on a point to get started!",
            className='responsive-text',
            style={
                'font-family': 'Roboto, sans-serif',
                'text-align': 'left',
                'color': "#FFFFFF"
            }),
        html.H4(
            children=[
                "For more information on the tool itself visit my ",
                html.A(
                    "Github Repository",
                    href="https://github.com/CChan101/PokeInsights",
                    target="_blank",
                    style={'color': '#1E90FF', 'text-decoration': 'underline'}  # Optional styling for the link
                ),
                "."
            ],
            className='responsive-text',
            style={
                'font-family': 'Roboto, sans-serif',
                'text-align': 'left',
                'color': "#FFFFFF"
            }
        ),
        dcc.Dropdown(
            id='top-n-results',
            options=[
                {'label': 'Top 5 Results', 'value': 5},
                {'label': 'Top 10 Results', 'value': 10},
                {'label': 'Top 25 Results', 'value': 25}
            ],
            value=5,  # Default Value
            searchable=False,
            clearable=False,
            style={
                'width': '150px',
                'font-family': 'Roboto, sans-serif',
            },
        ), dcc.Dropdown(
            id='tier-dropdown',
            options=[
                {'label': 'GEN9OU', 'value': 'gen9ou'},
                {'label': 'GEN9UBERS', 'value': 'gen9ubers'},
                {'label': 'GEN9UU', 'value': 'gen9uu'},
                {'label': 'GEN9RU', 'value': 'gen9ru'},
                {'label': 'GEN9NU', 'value': 'gen9nu'},
                {'label': 'GEN9PU', 'value': 'gen9pu'},
                {'label': 'GEN9ZU', 'value': 'gen9zu'},
                {'label': 'GEN8OU', 'value': 'gen8ou'},
                {'label': 'GEN7OU', 'value': 'gen7ou'},
                {'label': 'GEN6OU', 'value': 'gen6ou'},
                {'label': 'GEN5OU', 'value': 'gen5ou'},
                {'label': 'GEN4OU', 'value': 'gen4ou'},
                {'label': 'GEN3OU', 'value': 'gen3ou'},
                {'label': 'GEN2OU', 'value': 'gen2ou'},
                {'label': 'GEN1OU', 'value': 'gen1ou'},
            ],
            style={
                'width': '150px',
                'font-family': 'Roboto, sans-serif',
            },
            value='gen9ou',  # Default Value
            searchable=False,
            clearable=False
        ), dcc.Dropdown(
            id='ladder-ranking',
            options=[],
            value=None,
            searchable=False,
            clearable=False,
            style={'width': '150px', 'font-family': 'Roboto, sans-serif'}
        ),
        dcc.Graph(id='line-graph', className='center dash-graph', responsive=True),
        html.Div([
            html.H4(id='selected-name', style={'font-family': 'Roboto, '
                                                              'sans-serif', 'font-size': '30px', 'color': 'white',
                                               'position': 'absolute',
                                               'top': '10px',
                                               'left': '40px',
                                               'z-index': '10'}),
            html.Div(id='image-container',
                     style={'margin-top': '200px', 'margin-right': '600px', 'position': 'absolute', 'z-index': '10'}),
            dcc.Graph(id='stats-graph', className='responsive-graph', responsive=True),
        ], style={'position': 'relative', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
                  'border': '2px solid white', 'padding': '10px', 'backgroundColor': '#111111',
                  'width': '800px', 'height': '450px', 'marginTop': '50px'},
            className='center dash-zoom'),
        html.Div(id='conditional-text', style= {
            'clear': 'both',
            'paddingTop': '30px',
            'marginTop': '50px',
            'margin': '0 auto',
            'font-family': 'Roboto, sans-serif',
            'text-align': 'center'
        }, className='fun-facts'),
        # In your app.layout children array, add:
        html.Div([
            html.H3("Meta Analysis", style={'marginTop': '50px'}),
            dcc.Loading(
                id="ai-analysis-loading",
                type="circle",
                children=html.Div(id='ai-meta-summary', style={
                    'whiteSpace': 'pre-line',
                    'textAlign': 'left',
                    'border': '2px solid #1E90FF',
                    'padding': '20px',
                    'margin': '20px auto',
                    'maxWidth': '800px'
                })
            )
        ], className='ai-analysis-section'),
        html.Div([
            html.P('v1.1'),
            html.P('Automated insights feature to provide users with data-driven recommendations and trends*', style={'margin': 0}),
            html.P('Monthly graph transitions now accurately display 0% usage for months when a Pokemon is banned, ensuring clearer data representation', style={'margin': 0}),
            html.P("v1.01"),
            html.P('Added support for past OU generations and tier rankings', style={'margin': 0}),
            html.P('Changed interesting insights to just measure latest month for ease of use', style={'margin': 0}),
            html.P("Future Plans:"),
            html.P("Add missing Pokemon Sprites", style={'margin': 0}),
            html.P("Improve functionality of stats box", style={'margin': 0}),
            html.P("Choose specific range of dates in graph", style={'margin': 0}),
            html.P("*Automated insights are generated using data I personally scraped from public Smogon data, ensuring no third-party or user data is involved.")
        ], style={'marginTop': '50px',
                  'font-family': 'Roboto, sans-serif',
                  'text-align': 'left'}, className='update-text')
    ])


@app.callback(
    [Output('ladder-ranking', 'options'),
     Output('ladder-ranking', 'value')],
    [Input('tier-dropdown', 'value')]
)
def update_ladder_ranking_options(selected_tier):
    if selected_tier == 'gen9ou':
        options = [
            {'label': '1000', 'value': 1000},
            {'label': '1500', 'value': 1500},
            {'label': '1825', 'value': 1825}
        ]
        default_value = 1000

    else:
        options = [
            {'label': '1000', 'value': 1000},
            {'label': '1500', 'value': 1500},
            {'label': '1760', 'value': 1760}
        ]
        default_value = 1000

    return options, default_value

def fill_missing_months(df, top_n_array):
    df['Month'] = pd.to_datetime(df['Month'])
    all_months = pd.date_range(df['Month'].min(), df['Month'].max(), freq='MS')
    result = []
    for name in top_n_array:
        group = df[df['Name'] == name].set_index('Month').reindex(all_months, fill_value=0).reset_index()
        group['Name'] = name
        # Copy over other columns if needed (e.g., 'Sprite Links')
        for col in ['Sprite Links', 'Ranking', 'Tier']:
            if col in df.columns:
                group[col] = df[df['Name'] == name][col].iloc[0] if not df[df['Name'] == name][col].empty else None
        result.append(group)
    df_filled = pd.concat(result)
    df_filled.rename(columns={'index': 'Month'}, inplace=True)
    return df_filled

# Callback to update the graph
@app.callback(
    Output('line-graph', 'figure'),
    [Input('tier-dropdown', 'value'),
     Input('top-n-results', 'value'),
     Input('ladder-ranking', 'value')]
)
def update_graph(given_tier, top_n, ladder_ranking):
    # Filter df_final by the selected tier and ladder ranking
    filtered_df = df_final[(df_final['Tier'] == given_tier) & (df_final['Ranking'] == ladder_ranking)]
    if filtered_df.empty:
        print("No data avaliable for tier: {'given_tier} in filtered_df!")
        return px.line(title=f'Top {top_n} Results')

    filtered_df['Month'] = pd.to_datetime(filtered_df['Month'])
    # Sort by Month and Usage Rate
    sorted_df = filtered_df.sort_values(by=['Month', 'Usage Rate'], ascending=[True, False])

    # Identify the latest month
    latest_month = sorted_df['Month'].max()

    # Get the top N Pokémon for the latest month
    latest_top_n = sorted_df[sorted_df['Month'] == latest_month].nlargest(top_n, 'Usage Rate')
    top_n_array = latest_top_n['Name'].unique()

    # Filter the DataFrame to include only those top n Pokémon across all months
    concat_df = sorted_df[sorted_df['Name'].isin(top_n_array)]

    if concat_df.empty:
        print(f"No data available for the top {top_n} Pokémon in tier: {given_tier} in concat_df!")
        return px.line(title=f'Top {top_n} Results')

    concat_df_filled = fill_missing_months(concat_df, top_n_array)
    fig = px.line(concat_df_filled, x='Month', y='Usage Rate', color="Name",
                  title=None, markers=True, custom_data=['Sprite Links', 'Name'])

    fig.update_layout(template='plotly_dark', font=dict(color=colors['text']),
                      legend=dict(
                          font=dict(size=7.5),  # Smaller font
                          itemsizing='constant',
                          itemwidth=30,  # Smaller symbol size
                          # Adjust items for 768px and below (tablet)
                      ),
                      title={
                          'text': f"Usage Rate for {given_tier}",
                          'y': 0.95,
                          'x': 0.5,
                          'xanchor': 'center',
                          'yanchor': 'top',
                          'font': dict(
                              size=24,
                              color='#FFFFFF'
                          )
                      }
                      )

    # Set the x-axis range
    start_date = datetime(2022, 10, 1)
    end_date = datetime.today().replace(day=1) - relativedelta(months=1)

    fig.update_xaxes(dtick='M3', tickformat='%b %Y', range=[start_date, end_date])
    return fig


# Callback to display the image on click
@app.callback(
    Output('image-container', 'children'),
    Input('line-graph', 'clickData')
)
def display_image(clickData):
    if clickData is None:
        return ""

    # Extract the sprite link from clickData's customdata
    sprite_link = clickData['points'][0]['customdata'][0]

    return html.Img(src=sprite_link,
                    style={
                        ''"margin-top": "-75px", "left": "-20px", "top": "20px", "width": "210px", "height": "210px",
                        "max-width": "100%", "max-height": "100%"}, className='center')


@app.callback(
    Output('selected-name', 'children'),
    Input('line-graph', 'clickData')
)
def update_selected_name(clickData):
    if clickData is None:
        return "No selection"

    print(clickData)
    try:
        points = clickData.get('points', [])
        if not points:
            return "No points data available"

        customdata = points[0].get('customdata', [])
        if len(customdata) < 2:
            return "No stats data available"

        pokemon_name = customdata[1]
        print(f"Clicked Pokémon: {pokemon_name}")

        return f"{pokemon_name}"
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error accessing custom data: {e}")
        return "Error displaying stats"


# Callback to update the stats graph based on clicked Pokémon
@app.callback(
    [Output('stats-graph', 'figure'),
     Output('stats-graph', 'style')],
    Input('line-graph', 'clickData')
)
def update_stats_graph(clickData):
    if clickData is None or not clickData['points']:
        # Return an empty figure
        return {'data': []}, {'display': 'none'}

    try:
        customdata = clickData['points'][0].get('customdata', [])
        if len(customdata) < 2:
            return px.bar(title="No stats data available"), {'display': 'block'}

        pokemon_name = customdata[1]

        # Filter pokemon_stats DataFrame to get stats for the selected Pokémon
        pokemon_stats_df = df_final[df_final['Name'] == pokemon_name]

        if pokemon_stats_df.empty:
            return px.bar(title=f"No stats available for {pokemon_name}"), {'display': 'block'}

        # Example: Assuming you have columns like 'HP', 'Attack', 'Defense'
        stats_columns = ['HP', 'Attack', 'Defense', 'Sp.Attack', 'Sp.Defense',
                         'Speed']  # Replace with your actual stat columns

        # Select only the stats columns for the selected Pokémon
        stats_data = pokemon_stats_df[stats_columns].iloc[0]

        # Create a DataFrame suitable for plotting with Plotly Express
        stats_df = pd.DataFrame({
            'Stat': stats_data.index,
            'Value': stats_data.values
        })

        fig = px.bar(stats_df, x='Stat', y='Value',
                     title=f'Stats for {pokemon_name}')
        fig.update_layout(template='plotly_dark', yaxis_title=None,
                          xaxis_title=None, title="")

        return fig, {'display': 'block'}
    except (IndexError, KeyError) as e:
        print(f"Error accessing custom data: {e}")
        return px.bar(title="Error displaying stats"), {'display': 'block', 'width': '60%', 'height': '80%'}


cutoff_df = df_final[(df_final['Month'] == '2024-06') &
    (df_final['Usage Rate'] >= 3.406)]
cutoff_df.to_excel('test_date.xlsx')

combined_cutoff_df = pd.concat([cutoff_df[['Name', 'Tier', 'Month', 'Type1']].rename(columns={'Type1': 'Type'}),
                                cutoff_df[['Name', 'Tier', 'Month', 'Type2']].rename(columns={'Type2': 'Type'})])
#Remove all null boxes and boxes with "---"
combined_cutoff_df = combined_cutoff_df.loc[
    combined_cutoff_df['Type'].notna() & (combined_cutoff_df['Type'] != '') & (combined_cutoff_df['Type'] != '---')]
combined_cutoff_df.to_excel('test_data_two.xlsx')

# Determine the most common type for each tier
most_common_types = combined_cutoff_df.groupby('Tier')['Type'].agg(lambda x: x.value_counts().idxmax()).to_dict()

# Determine the least common type for each tier
least_common_types = combined_cutoff_df.groupby('Tier')['Type'].agg(lambda x: x.value_counts().idxmin()).to_dict()

# Determine the highest BST Pokémon for each tier
highest_bst_pokemon = cutoff_df.loc[cutoff_df.groupby('Tier')['BST'].idxmax()].set_index('Tier')['Name'].to_dict()

# Determine the lowest BST Pokémon for each tier
lowest_bst_pokemon = cutoff_df.loc[cutoff_df.groupby('Tier')['BST'].idxmin()].set_index('Tier')['Name'].to_dict()

# Determine the average BST of the Pokemon in each tier
average_bst_tier = cutoff_df.groupby('Tier')['BST'].mean().round().to_dict()

# Callback to update conditional text based on dropdown selection
@app.callback(
    Output('conditional-text', 'children'),
    [Input('tier-dropdown', 'value')]
)
def update_conditional_text(given_tier):
    common_type = most_common_types.get(given_tier, "Unknown")
    highest_bst = highest_bst_pokemon.get(given_tier, "Unknown")
    lowest_bst = lowest_bst_pokemon.get(given_tier, "Unknown")
    average_bst = average_bst_tier.get(given_tier, "Unknown")

    # Define types to exclude based on generation (given_tier)
    excluded_types = []
    if given_tier in ["gen1ou"]:
        excluded_types.extend(['dark', 'steel', 'fairy'])
    elif given_tier in ["gen2ou", "gen3ou", "gen4ou", "gen5ou"]:
        excluded_types.append('fairy')

    # Function to get least common type, excluding specified types
    def least_common_excluding(types):
        type_counts = Counter(types)
        for type_, count in type_counts.most_common()[::-1]:
            if type_ not in excluded_types:
                return type_
        return "Unknown"

    # Get the types for the given tier
    tier_types = combined_cutoff_df[combined_cutoff_df['Tier'] == given_tier]['Type'].tolist()
    uncommon_type = least_common_excluding(tier_types)

    table_style = {
        'border-collapse': 'collapse',
        'width': '40%',
        'border': '1px solid black',
        'margin': '0 auto'
    }
    cell_style = {
        'border': '1px solid white',
        'padding': '8px',
        'text-align': 'center',
        'background-color': 'black',
        'color': 'white'
    }

    return html.Div([
        html.H3("Interesting Insights", style={'text-align': 'center'}),
        html.Table([
            html.Tbody([
                html.Tr([html.Td(f"Most common type in {given_tier}: {common_type}", style=cell_style)]),
                html.Tr([html.Td(f"Least common type in {given_tier}: {uncommon_type}", style=cell_style)]),
                html.Tr([html.Td(f"Highest BST Pokémon in {given_tier}: {highest_bst}", style=cell_style)]),
                html.Tr([html.Td(f"Lowest BST Pokémon in {given_tier}: {lowest_bst}", style=cell_style)]),
                html.Tr([html.Td(f"Average BST of {given_tier}: {average_bst}", style=cell_style)])
            ])
        ], style=table_style)
    ], style={
        'font-family': 'Arial, sans-serif',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'width': '100%'
    })

# Initialize client once (outside callbacks)

import google.generativeai as genai

genai.configure(api_key="######") #Use your own API key

@app.callback(
    Output('ai-meta-summary', 'children'),
    [Input('tier-dropdown', 'value'),
     Input('top-n-results', 'value'),
     Input('ladder-ranking', 'value')]
)

def generate_meta_summary(given_tier, top_n, ladder_ranking):

    filtered_df = df_final[
        (df_final['Tier'] == given_tier) &
        (df_final['Ranking'] == ladder_ranking)
    ]

    if filtered_df.empty:
        return "No data available for analysis"

    filtered_df['Month'] = pd.to_datetime(filtered_df['Month'])
    latest_month = filtered_df['Month'].max()
    # Ensure only Pokémon that are legal in this tier *this month* are considered
    latest_data = filtered_df[
        (filtered_df['Month'] == latest_month) &
        (filtered_df['Tier'] == given_tier)
        ].nlargest(top_n, 'Usage Rate')


    #Get prev month data
    prev_month = (pd.to_datetime(latest_month) - pd.DateOffset(months=1))
    prev_data = filtered_df[
        (filtered_df['Month'] == prev_month) &
        (filtered_df['Tier'] == given_tier)
        ].nlargest(top_n, 'Usage Rate')
    # (Optional) Markdown tables
    current_md_table = latest_data[['Name', 'Usage Rate', 'Tier', 'Type1', 'Type2', 'BST', 'Month']].to_markdown(
        index=False)
    prev_md_table = prev_data[['Name', 'Usage Rate', 'Tier', 'Type1', 'Type2', 'BST', 'Month']].to_markdown(index=False)

    prompt = f"""You are a competitive Pokémon analyst for {given_tier.upper()} format in.

    TASK: Generate a 100-word meta analysis focusing on usage shifts from {prev_month} to {latest_month} in {ladder_ranking}.

    ANALYSIS RULES:
    - Only analyze Pokémon in the provided {given_tier.upper()} data
    - Reference specific Pokémon names and percentages
    - Do not invent roles or abilities not in the dataset
    - Only base analysis on Usage Rate for a pokemon throughout {prev_month} to {latest_month}
    - If a mon's usage is 0% for a month, assume it is not in the tier/banned
    - current_md_table has the data for the current month. prev_md_table has the data for the previous month

    DATA: {current_md_table}, {prev_md_table}

"""

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"


if __name__ == "__main__":
    # Get the port from the environment variable or use 8050 as default
    # Run the server
    port = int(os.environ.get("PORT", 8080))
    app.run_server(debug=False, host="0.0.0.0", port=port)


def update_graph_callback(top_n, given_tier, ladder_ranking):
    return update_graph(top_n, given_tier, ladder_ranking)




