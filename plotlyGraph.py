import datetime
import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html, Input, Output

app = dash.Dash()

colors = {
    # Change color of background
    'background_color': '#404040',
    'text': '#FFFFFF'
}
df_final = pd.read_excel("sample_data.xlsx")

app.layout = html.Div(
    style={'backgroundColor': colors['background_color'], 'color': colors['text'], 'height': '100vh',
           "marginTop": "0px",
           "marginBottom": "0px",
           "paddingTop": "12.5px",
           "paddingBottom": "12.5px",
           "paddingLeft": "10px",
           "textAlign": "center", }, className='dynamic-width',
    children=[
        html.Img(src=r"/assets/PokeInsights Logo.png",
                 className='image-zoom', style={'textAlign': 'center'}),
        html.H4(
            "An easy-to-use tool for gathering insights on statistics within competitive Pokemon(Smogon) and "
            "measuring trends such as usage rate. Use the dropdown and click on a point to get started!",
            className='responsive-text',
            style={
                'font-family': 'Roboto, sans-serif',
                'text-align': 'left',
                'color': "#FFFFFF"
            }),
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
            ],
            style={
                'width': '150px',
                'font-family': 'Roboto, sans-serif',
            },
            value='gen9ou',  # Default Value
            searchable=False,
            clearable=False
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
            dcc.Graph(id='stats-graph', className='responsive-graph', responsive=True)
        ], style={'position': 'relative', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
                  'border': '2px solid white', 'padding': '10px', 'backgroundColor': '#111111',
                  'width': '800px', 'height': '450px', 'marginTop': '50px'},
            className='center dash-zoom'),
        html.Div(id='conditional-text', style={  # Add div for conditional text
            'clear': 'both',  # Clears any floating elements
            'paddingTop': '30px',
            'marginTop': '50px',
            'margin': '0 auto',
            'font-family': 'Roboto, sans-serif',
            'text-align': 'center'  # Adjust as needed)
        }, className='fun-facts'),
        html.Div([
            html.P('v1.0'),
            html.P("Future Plans:"),
            html.Br(),
            html.P("Add missing Pokemon Sprites", style={'margin': 0}),
            html.P("Add more generations to dropdown", style={'margin': 0}),
            html.P("Improve functionality of stats box", style={'margin': 0}),
            html.P("Choose specific range of dates in graph", style={'margin': 0})
        ], style={'marginTop': '50px',
                  'font-family': 'Roboto, sans-serif',
                  'text-align': 'left'}, className='update-text')
    ])


# Callback to update the graph
@app.callback(
    Output('line-graph', 'figure'),
    [Input('tier-dropdown', 'value'),
     Input('top-n-results', 'value')]
)
def update_graph(given_tier, top_n):
    # Filter df_final by the selected tier
    filtered_df = df_final[df_final['Tier'] == given_tier]
    if filtered_df.empty:
        print("No data avaliable for tier: {'given_tier}")
        return px.line(title=f'Top {top_n} Results')

    filtered_df['Month'] = pd.to_datetime(filtered_df['Month'])
    # Sort by Month and Usage Rate
    sorted_df = filtered_df.sort_values(by=['Month', 'Usage Rate'], ascending=[True, False])

    # Identify the latest month
    latest_month = sorted_df['Month'].max()

    # Get the top N Pokémon for the latest month
    latest_top_n = sorted_df[sorted_df['Month'] == latest_month].nlargest(top_n, 'Usage Rate')
    top_n_array = latest_top_n['Name'].unique()

    # Filter the DataFrame to include only those Pokémon across all months
    concat_df = sorted_df[sorted_df['Name'].isin(top_n_array)]

    if concat_df.empty:
        print(f"No data available for the top {top_n} Pokémon in tier: {given_tier}")
        return px.line(title=f'Top {top_n} Results')

    fig = px.line(concat_df, x='Month', y='Usage Rate', color="Name",
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
    start_date = datetime.datetime(2022, 10, 1)
    end_date = datetime.datetime(2024, 7, 1)

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


cutoff_df = df_final[df_final['Usage Rate'] >= 3.406]
# print(cutoff_df)
combined_cutoff_df = pd.concat([cutoff_df[['Name', 'Tier', 'Month', 'Type1']].rename(columns={'Type1': 'Type'}),
                                cutoff_df[['Name', 'Tier', 'Month', 'Type2']].rename(columns={'Type2': 'Type'})])
# print(combined_cutoff_df)
# cutoff_df.to_excel('test_data.xlsx')
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
    uncommon_type = least_common_types.get(given_tier, "Unknown")
    highest_bst = highest_bst_pokemon.get(given_tier, "Unknown")
    lowest_bst = lowest_bst_pokemon.get(given_tier, "Unknown")
    average_bst = average_bst_tier.get(given_tier, "Unknown")
    # highest_bst_pokemon_name = highest_bst_pokemon.get(given_tier, "Unknown")

    table_style = {
        'border-collapse': 'collapse',
        'width': '40%',
        'border': '1px solid black',
        'margin': '0 auto'  # This centers the table horizontally
    }

    cell_style = {
        'border': '1px solid white',
        'padding': '8px',
        'text-align': 'center',
        'background-color': 'black',
        'color': 'white'  # This changes the text color to white for better visibility
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


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)


def update_graph_callback(top_n, given_tier):
    return update_graph(top_n, given_tier)
