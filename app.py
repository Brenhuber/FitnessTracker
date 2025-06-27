import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import requests
import datetime

stats_history = []
stats_history.clear()

PRIMARY = '#1a355b'
SECONDARY = '#3a6ea5'
ACCENT = '#e67e22'
BG = '#f7f9fb'
CARD = '#f2f4f8'
DARK = '#16213e'
LIGHT = '#e9eef6'
GRADIENT = 'linear-gradient(135deg, #f7f9fb 0%, #e9eef6 100%)'

app_styles = {
    'fontFamily': 'Inter, Segoe UI, Arial, sans-serif',
    'background': GRADIENT,
    'minHeight': '100vh',
    'color': DARK,
    'transition': 'background 0.7s',
    'position': 'relative',
    'paddingBottom': '80px',
}
nav_styles = {
    'background': f'linear-gradient(90deg, {SECONDARY} 0%, {PRIMARY} 100%)',
    'padding': '1.4rem 2rem',
    'borderRadius': '0 0 1.2rem 1.2rem',
    'color': 'white',
    'fontWeight': 'bold',
    'fontSize': '1.35rem',
    'boxShadow': '0 6px 24px rgba(26,53,91,0.18), 0 1.5px 0 #e67e22',
    'marginBottom': '2.5rem',
    'display': 'flex',
    'gap': '2.2rem',
    'justifyContent': 'center',
    'fontFamily': 'Inter, Segoe UI, Arial, sans-serif',
    'letterSpacing': '0.04em',
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'width': '100vw',
    'zIndex': 1000,
    'transition': 'box-shadow 0.2s, background 0.2s',
    'borderBottom': f'4px solid {ACCENT}',
    'opacity': 0.98,
    'backdropFilter': 'blur(2px)',
}
nav_link = lambda active: {
    'color': '#fff' if not active else PRIMARY,
    'background': ACCENT if active else SECONDARY,
    'padding': '0.85rem 1.7rem',
    'borderRadius': '0.8rem',
    'textDecoration': 'none',
    'transition': 'all 0.18s',
    'boxShadow': '0 2px 12px rgba(26,53,91,0.13)' if active else '0 1px 4px rgba(58,110,165,0.10)',
    'fontWeight': 800,
    'fontFamily': 'Inter, Segoe UI, Arial, sans-serif',
    'fontSize': '1.13rem',
    'letterSpacing': '0.01em',
    'border': f'2.5px solid {ACCENT}' if active else f'2.5px solid {SECONDARY}',
    'outline': 'none',
    'cursor': 'pointer',
    'opacity': 1,
    'boxSizing': 'border-box',
    'margin': '0 0.1rem',
    'textShadow': '0 1px 4px rgba(26,53,91,0.10)',
}
card_style = {
    'background': CARD,
    'borderRadius': '1.3rem',
    'padding': '2.5rem',
    'marginBottom': '2.5rem',
    'boxShadow': '0 8px 32px rgba(0,119,182,0.10)',
    'border': f'2px solid {SECONDARY}',
    'fontFamily': 'Inter, Segoe UI, Arial, sans-serif',
    'transition': 'box-shadow 0.2s, transform 0.2s',
}
footer_style = {
    'position': 'fixed',
    'bottom': 0,
    'left': 0,
    'width': '100vw',
    'background': f'linear-gradient(90deg, {PRIMARY} 0%, {SECONDARY} 100%)',
    'color': 'white',
    'textAlign': 'center',
    'padding': '1.1rem 0 0.7rem 0',
    'fontSize': '1.05rem',
    'fontWeight': 500,
    'letterSpacing': '0.02em',
    'boxShadow': '0 -2px 8px rgba(0,0,0,0.07)',
    'zIndex': 1001,
    'fontFamily': 'Inter, Segoe UI, Arial, sans-serif',
}

def get_openfoodfacts_nutrition(food_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food_name}&search_simple=1&action=process&json=1&page_size=1"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if not data.get('products'):
        return None
    product = data['products'][0]
    nutriments = product.get('nutriments', {})
    return {
        'calories': nutriments.get('energy-kcal_100g', 0),
        'protein': nutriments.get('proteins_100g', 0),
        'fat': nutriments.get('fat_100g', 0),
        'carbs': nutriments.get('carbohydrates_100g', 0)
    }

def make_dashboard(df, goal_intake, goal_burned):
    fig_intake = px.line(df, x='date', y='calories_intake', markers=True, title='Calories Intake vs. Goal',
                         labels={'calories_intake': 'Calories', 'date': 'Date'},
                         color_discrete_sequence=['#0077b6'])
    fig_intake.add_hline(y=goal_intake, line_dash="dash", line_color="#ff8800", annotation_text="Goal Intake")
    fig_burned = px.line(df, x='date', y='calories_burned', markers=True, title='Calories Burned vs. Goal',
                         labels={'calories_burned': 'Calories', 'date': 'Date'},
                         color_discrete_sequence=['#00b4d8'])
    fig_burned.add_hline(y=goal_burned, line_dash="dash", line_color="#ff8800", annotation_text="Goal Burned")
    fig_macros = px.line(df, x='date', y=['protein', 'fat', 'carbs'], markers=True, title='Macros Over Time',
                         labels={'value': 'Grams', 'date': 'Date', 'variable': 'Macro'},
                         color_discrete_map={'protein': '#0077b6', 'fat': '#ff8800', 'carbs': '#00b4d8'})
    return fig_intake, fig_burned, fig_macros

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Fitlytics – Modern Fitness Tracker'

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div([
        html.Span([
            html.Img(src='https://img.icons8.com/ios-filled/50/1a355b/dumbbell.png', style={'height': '2.1rem', 'verticalAlign': 'middle', 'marginRight': '0.7rem', 'marginTop': '-0.1rem'}),
            html.Span('Fitlytics', style={'fontWeight': 900, 'fontSize': '2.1rem', 'letterSpacing': '0.04em', 'fontFamily': 'Inter, Segoe UI, Arial, sans-serif', 'verticalAlign': 'middle', 'color': PRIMARY, 'textShadow': '0 2px 8px #e9eef6'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], style={**nav_styles, 'background': f'linear-gradient(90deg, {SECONDARY} 0%, {PRIMARY} 100%)', 'color': 'white', 'justifyContent': 'flex-start', 'gap': '0.5rem', 'marginBottom': 0, 'boxShadow': '0 4px 16px rgba(0,0,0,0.09)'}),
    html.Div(id='navbar', style={'marginTop': '4.5rem'}),
    html.Div(id='page-content', style={'padding': '2rem', 'maxWidth': '950px', 'margin': 'auto', 'marginTop': '1.5rem'}),
    html.Footer('© 2025 Fitlytics. All rights reserved.', style=footer_style)
], style=app_styles)

@app.callback(Output('navbar', 'children'), Input('url', 'pathname'))
def update_navbar(pathname):
    return html.Div([
        dcc.Link('Dashboard', href='/', style=nav_link(pathname == '/')),
        dcc.Link('Tracker', href='/tracker', style=nav_link(pathname == '/tracker')),
        dcc.Link('About', href='/about', style=nav_link(pathname == '/about')),
        dcc.Link('Contact', href='/contact', style=nav_link(pathname == '/contact')),
    ], style={**nav_styles, 'background': 'transparent', 'boxShadow': 'none', 'position': 'static', 'marginBottom': '1.5rem', 'justifyContent': 'center', 'color': PRIMARY})

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/tracker':
        return tracker_layout()
    elif pathname == '/about':
        return about_layout()
    elif pathname == '/contact':
        return contact_layout()
    else:
        return dashboard_layout()

def dashboard_layout():
    if not stats_history:
        return html.Div([
            html.Div([
                html.H2('Dashboard', style={'color': PRIMARY, 'marginBottom': '0.5rem', 'fontWeight': 900, 'fontFamily': 'Inter, Segoe UI, Arial, sans-serif', 'fontSize': '2.2rem', 'letterSpacing': '0.03em'}),
                html.Hr(style={'border': f'1.5px solid {ACCENT}', 'margin': '1.2rem 0'}),
                html.P('No stats to display yet. Add nutrition and exercise data!', style={'color': ACCENT, 'fontWeight': 'bold', 'fontSize': '1.15rem'})
            ], style=card_style)
        ])
    df = pd.DataFrame(stats_history)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    goal_intake = df['goal_intake'].iloc[-1] if 'goal_intake' in df and not df.empty else 2500
    goal_burned = df['goal_burned'].iloc[-1] if 'goal_burned' in df and not df.empty else 500
    import plotly.express as px
    fig_intake = px.bar(
        df, x='date', y='calories_intake',
        color_discrete_sequence=[PRIMARY],
        title='Calories Intake',
        labels={'calories_intake': 'Calories', 'date': 'Date'}
    )
    fig_intake.add_hline(y=goal_intake, line_dash="dash", line_color=ACCENT, annotation_text="Goal Intake", annotation_position="top left")
    fig_intake.update_layout(
        yaxis_range=[0, max(df['calories_intake'].max(), goal_intake, 1)*1.2],
        plot_bgcolor=BG,
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
        autosize=True,
    )
    fig_burned = px.bar(
        df, x='date', y='calories_burned',
        color_discrete_sequence=[SECONDARY],
        title='Calories Burned',
        labels={'calories_burned': 'Calories', 'date': 'Date'}
    )
    fig_burned.add_hline(y=goal_burned, line_dash="dash", line_color=ACCENT, annotation_text="Goal Burned", annotation_position="top left")
    fig_burned.update_layout(
        yaxis_range=[0, max(df['calories_burned'].max(), goal_burned, 1)*1.2],
        plot_bgcolor=BG,
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
        autosize=True,
    )
    fig_macros = px.line(
        df, x='date', y=['protein', 'fat', 'carbs'],
        markers=True,
        title='Macros Over Time',
        labels={'value': 'Grams', 'date': 'Date', 'variable': 'Macro'},
        color_discrete_map={'protein': PRIMARY, 'fat': ACCENT, 'carbs': SECONDARY}
    )
    fig_macros.update_layout(
        yaxis_range=[0, max(df[['protein','fat','carbs']].max().max(), 1)*1.2],
        plot_bgcolor=BG,
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
        autosize=True,
    )
    latest = df.iloc[-1] if not df.empty else None
    if latest is not None and (latest['protein'] or latest['fat'] or latest['carbs']):
        fig_pie = px.pie(
            names=['Protein', 'Fat', 'Carbs'],
            values=[latest['protein'], latest['fat'], latest['carbs']],
            color_discrete_sequence=[PRIMARY, ACCENT, SECONDARY],
            title='Latest Macro Distribution'
        )
        fig_pie.update_layout(height=320, margin=dict(l=30, r=30, t=50, b=30), autosize=True)
    else:
        fig_pie = px.pie(title='Latest Macro Distribution')
        fig_pie.update_layout(height=320, margin=dict(l=30, r=30, t=50, b=30), autosize=True)
    graph_card = lambda title, fig: html.Div([
        html.H4(title, style={'color': DARK, 'fontWeight': 700, 'marginBottom': '0.7rem', 'fontFamily': 'Inter, Segoe UI, Arial, sans-serif', 'fontSize': '1.18rem', 'letterSpacing': '0.01em'}),
        dcc.Graph(figure=fig, config={'displayModeBar': False, 'responsive': True}, style={'background': CARD, 'borderRadius': '1rem', 'padding': '1rem', 'boxShadow': '0 2px 8px rgba(0,119,182,0.07)', 'height': '370px', 'transition': 'box-shadow 0.2s, transform 0.2s'})
    ], style={**card_style, 'marginBottom': '1.5rem', 'transition': 'box-shadow 0.2s, transform 0.2s'})
    return html.Div([
        html.Div([
            html.H2('Dashboard', style={'color': PRIMARY, 'marginBottom': '0.5rem', 'fontWeight': 900, 'fontFamily': 'Inter, Segoe UI, Arial, sans-serif', 'fontSize': '2.2rem', 'letterSpacing': '0.03em'}),
            html.Hr(style={'border': f'1.5px solid {ACCENT}', 'margin': '1.2rem 0'}),
            html.Div([
                html.Div([
                    html.Div('Goal Intake', style={'color': PRIMARY, 'fontWeight': 'bold', 'fontSize': '1.1rem'}),
                    html.Div(f"{goal_intake} kcal", style={'color': ACCENT, 'fontSize': '1.2rem', 'fontWeight': 700})
                ], style={'flex': 1, 'textAlign': 'center'}),
                html.Div([
                    html.Div('Goal Burned', style={'color': PRIMARY, 'fontWeight': 'bold', 'fontSize': '1.1rem'}),
                    html.Div(f"{goal_burned} kcal", style={'color': ACCENT, 'fontSize': '1.2rem', 'fontWeight': 700})
                ], style={'flex': 1, 'textAlign': 'center'}),
            ], style={'display': 'flex', 'gap': '2rem', 'marginBottom': '1.5rem', 'justifyContent': 'center'}),
            html.Div([
                graph_card('Calories Intake', fig_intake),
                graph_card('Calories Burned', fig_burned),
                graph_card('Macros Over Time', fig_macros),
                graph_card('Latest Macro Distribution', fig_pie),
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '2rem', 'alignItems': 'stretch', 'marginTop': '1.5rem', 'marginBottom': '1.5rem', 'width': '100%', 'maxWidth': '100vw', 'overflowX': 'auto', 'gridTemplateRows': 'auto'}),
        ], style=card_style)
    ])

def tracker_layout():
    today = datetime.date.today()
    return html.Div([
        html.Div([
            html.H2('Tracker', style={'color': PRIMARY, 'marginBottom': '0.5rem'}),
            html.Div([
                html.H4('Add Food', style={'color': ACCENT, 'marginBottom': '0.7rem'}),
                html.Label('Food Name (include size if desired, e.g. "Apple 100g")', style={'color': PRIMARY, 'fontWeight': 'bold', 'marginRight': '0.5rem'}),
                dcc.Input(id='food-input', type='text', value='', style={'marginRight': '1rem', 'marginLeft': '0.4rem', 'width': '250px', 'borderRadius': '0.5rem', 'border': f'2px solid {ACCENT}', 'padding': '0.5rem', 'background': '#fffbe6'}),
                dcc.Loading(
                    html.Button('Look up macros using API', id='api-btn', n_clicks=0, style={'background': ACCENT, 'color': 'white', 'border': 'none', 'borderRadius': '0.5rem', 'padding': '0.5rem 1rem', 'fontWeight': 'bold', 'boxShadow': '0 2px 8px rgba(255,136,0,0.15)'}),
                    type='circle', color=ACCENT
                ),
                html.Div(id='api-result', style={'marginTop': '0.5rem', 'color': ACCENT, 'fontWeight': 'bold'}),
                html.Div([
                    html.Label('Calories', style={'color': PRIMARY, 'marginRight': '0.5rem'}),
                    dcc.Input(id='calories-input', type='number', value=0, style={'width': '90px', 'marginRight': '1rem', 'marginLeft': '0.4rem', 'background': '#e3f2fd', 'border': f'2px solid {PRIMARY}'}),
                    html.Label('Protein (g)', style={'color': PRIMARY, 'marginLeft': '1rem', 'marginRight': '0.5rem'}),
                    dcc.Input(id='protein-input', type='number', value=0, style={'width': '90px', 'marginRight': '1rem', 'marginLeft': '0.4rem', 'background': '#e3f2fd', 'border': f'2px solid {PRIMARY}'}),
                    html.Label('Fat (g)', style={'color': PRIMARY, 'marginLeft': '1rem', 'marginRight': '0.5rem'}),
                    dcc.Input(id='fat-input', type='number', value=0, style={'width': '90px', 'marginRight': '1rem', 'marginLeft': '0.4rem', 'background': '#e3f2fd', 'border': f'2px solid {PRIMARY}'}),
                    html.Label('Carbs (g)', style={'color': PRIMARY, 'marginLeft': '1rem', 'marginRight': '0.5rem'}),
                    dcc.Input(id='carbs-input', type='number', value=0, style={'width': '90px', 'marginLeft': '0.4rem', 'background': '#e3f2fd', 'border': f'2px solid {PRIMARY}'}),
                ], style={'marginBottom': '1.2rem', 'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center', 'marginTop': '0.7rem'}),
            ], style={'marginBottom': '2rem', 'padding': '1.2rem', 'background': '#fffbe6', 'borderRadius': '1rem', 'boxShadow': '0 2px 8px rgba(255,136,0,0.07)', 'border': f'2px solid {ACCENT}'}),
            html.Div([
                html.H4('Add Exercise', style={'color': SECONDARY, 'marginBottom': '0.7rem'}),
                html.Label('Exercise Name', style={'color': PRIMARY, 'marginRight': '0.5rem'}),
                dcc.Input(id='exercise-input', type='text', value='', style={'marginRight': '1rem', 'marginLeft': '0.4rem', 'width': '200px', 'borderRadius': '0.5rem', 'border': f'2px solid {SECONDARY}', 'padding': '0.5rem', 'background': '#e0f7fa'}),
                html.Label('Calories Burned', style={'color': PRIMARY, 'marginLeft': '1rem', 'marginRight': '0.5rem'}),
                dcc.Input(id='burned-input', type='number', value=0, style={'width': '90px', 'marginLeft': '0.4rem', 'background': '#e0f7fa', 'border': f'2px solid {SECONDARY}'}),
            ], style={'marginBottom': '2rem', 'padding': '1.2rem', 'background': '#e0f7fa', 'borderRadius': '1rem', 'boxShadow': '0 2px 8px rgba(0,180,216,0.07)', 'border': f'2px solid {SECONDARY}'}),
            html.Div([
                html.Label('Goal Calories Intake', style={'color': PRIMARY, 'marginRight': '0.5rem'}),
                dcc.Input(id='goal-intake-input', type='number', value=2500, style={'width': '110px', 'marginRight': '1rem', 'marginLeft': '0.4rem', 'background': '#f1f8ff', 'border': f'2px solid {PRIMARY}'}),
                html.Label('Goal Calories Burned', style={'color': PRIMARY, 'marginLeft': '1rem', 'marginRight': '0.5rem'}),
                dcc.Input(id='goal-burned-input', type='number', value=500, style={'width': '110px', 'marginLeft': '0.4rem', 'background': '#f1f8ff', 'border': f'2px solid {PRIMARY}'}),
            ], style={'marginBottom': '1.2rem', 'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center'}),
            html.Button('Add Entry', id='add-entry-btn', n_clicks=0, style={'background': PRIMARY, 'color': 'white', 'border': 'none', 'borderRadius': '0.5rem', 'padding': '0.7rem 1.5rem', 'fontWeight': 'bold', 'fontSize': '1.1rem', 'marginTop': '0.5rem', 'boxShadow': '0 2px 8px rgba(0,119,182,0.15)'}),
            html.Div(id='tracker-msg', style={'marginTop': '1rem', 'color': SECONDARY, 'fontWeight': 'bold'}),
            html.H3("Today's Stats", style={'color': ACCENT, 'marginTop': '2rem', 'marginBottom': '1rem', 'textShadow': '0 2px 8px #fffbe6'}),
            html.Div(id='today-stats', style={'width': '100%', 'overflowX': 'auto', 'padding': 0, 'margin': 0}),
        ], style=card_style)
    ])

@app.callback(
    Output('api-result', 'children'),
    [Input('api-btn', 'n_clicks')],
    [State('food-input', 'value')],
    prevent_initial_call=True
)
def lookup_api(n_clicks, food):
    if n_clicks and food:
        try:
            result = get_openfoodfacts_nutrition(food)
            if result:
                return f"Found: {result['calories']} kcal, {result['protein']}g protein, {result['fat']}g fat, {result['carbs']}g carbs"
            else:
                return 'No nutrition info found. Please enter manually.'
        except Exception as e:
            return f'API error: {e}'
    return ''

@app.callback(
    [Output('tracker-msg', 'children'), Output('today-stats', 'children')],
    [Input('add-entry-btn', 'n_clicks')],
    [State('food-input', 'value'), State('calories-input', 'value'), State('protein-input', 'value'),
     State('fat-input', 'value'), State('carbs-input', 'value'), State('exercise-input', 'value'),
     State('burned-input', 'value'), State('goal-intake-input', 'value'), State('goal-burned-input', 'value')]
)
def add_entry(n_clicks, food, calories, protein, fat, carbs, exercise, burned, goal_intake, goal_burned):
    today = datetime.date.today()
    if n_clicks:
        if food and (not calories or not protein or not fat or not carbs):
            result = get_openfoodfacts_nutrition(food)
            if result:
                calories = calories or result['calories']
                protein = protein or result['protein']
                fat = fat or result['fat']
                carbs = carbs or result['carbs']
        stats_history.append({
            'date': today,
            'food': food,
            'calories_intake': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
            'exercise': exercise,
            'calories_burned': burned,
            'goal_intake': goal_intake,
            'goal_burned': goal_burned
        })
        msg = 'Entry added!'
    else:
        msg = ''
    today_stats = [s for s in stats_history if s['date'] == today]
    if today_stats:
        df = pd.DataFrame(today_stats)
        table_header = [
            html.Thead(html.Tr([
                html.Th(col, style={'background': ACCENT, 'color': 'white', 'padding': '0.7rem', 'fontWeight': 'bold', 'fontSize': '1.08rem', 'borderRadius': '0.4rem', 'boxShadow': '0 2px 8px rgba(255,136,0,0.09)'})
                for col in df.columns
            ]))
        ]
        table_body = [
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col], style={'padding': '0.7rem', 'background': '#fffbe6' if i % 2 == 0 else '#e0f7fa', 'borderRadius': '0.3rem', 'fontWeight': 500, 'fontSize': '1.05rem'})
                    for col in df.columns
                ]) for i in range(len(df))
            ])
        ]
        table = html.Table(table_header + table_body, style={'width': '100%', 'borderCollapse': 'separate', 'borderSpacing': '0', 'marginTop': '0.5rem', 'boxShadow': '0 4px 16px rgba(0,119,182,0.10)', 'fontFamily': 'Segoe UI, Arial, sans-serif', 'fontSize': '1.08rem', 'borderRadius': '1rem', 'overflow': 'hidden'})
        return msg, table
    else:
        return msg, ''

def about_layout():
    return html.Div([
        html.Div([
            html.H2('About Fitlytics', style={'color': PRIMARY, 'marginBottom': '0.5rem'}),
            html.P('Fitlytics is a modern fitness tracking app designed to help you take control of your health journey. Log your daily nutrition and exercise, visualize your progress, and stay motivated with clear, interactive dashboards.', style={'fontSize': '1.1rem', 'color': '#333'}),
            html.Ul([
                html.Li('No login required – jump right in and start tracking!'),
                html.Li('Nutrition Lookup – search foods using the free Open Food Facts API.'),
                html.Li('Exercise Tracking – log calories burned and see your trends.'),
                html.Li('Dashboard Visualizations – view calories, macros, and goals over time.'),
                html.Li('Goal Setting – set daily calorie and burn targets to stay on track.'),
            ], style={'fontSize': '1.05rem', 'color': PRIMARY}),
            html.P('Track. Visualize. Succeed.', style={'fontWeight': 'bold', 'color': ACCENT, 'fontSize': '1.1rem'})
        ], style=card_style)
    ])

def contact_layout():
    return html.Div([
        html.Div([
            html.H2('Contact', style={'color': PRIMARY, 'marginBottom': '0.5rem'}),
            html.P('Bren Huber', style={'fontWeight': 'bold', 'fontSize': '1.1rem', 'color': PRIMARY}),
            html.P('Connect With Me!', style={'fontSize': '1.05rem', 'color': '#333'}),
            html.Ul([
                html.Li(['Email: ', html.A('brenhuberbusiness@gmail.com', href='mailto:brenhuberbusiness@gmail.com', style={'color': SECONDARY, 'fontWeight': 'bold'})]),
                html.Li(['LinkedIn: ', html.A('linkedin.com/in/brenhuber', href='https://www.linkedin.com/in/brenhuber/', target='_blank', style={'color': SECONDARY, 'fontWeight': 'bold'})]),
            ], style={'fontSize': '1.05rem', 'color': PRIMARY}),
            html.P('I look forward to hearing from you!', style={'fontSize': '1.1rem', 'color': ACCENT})
        ], style=card_style)
    ])

if __name__ == '__main__':
    app.run(debug=True)
