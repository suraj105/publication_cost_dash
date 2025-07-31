from dash import html, dcc, dash_table
def create_layout(df):
    return html.Div([
        html.Div([
            html.H1("Analyse der Publikationskosten im wissenschaftlichen Verlagswesen:", className="main-title"),
            html.P("Datenbasierte Visualisierung mit Python, Dash und Chart.js")
        ], className="hero"),

        html.Div([
            html.Div([
                html.Label("Jahr"),
                dcc.Dropdown(
                    id="year-filter",
                    options=[{"label": str(y), "value": y} for y in sorted(df["year"].dropna().unique())],
                    multi=True
                )
            ], className="col-md-4"),

            html.Div([
                html.Label("Land"),
                dcc.Dropdown(
                    id="country-filter",
                    options=[{"label": c, "value": c} for c in sorted(df["country"].unique())],
                    multi=True
                )
            ], className="col-md-4"),

            html.Div([
                html.Label("Journal"),
                dcc.Dropdown(
                    id="journal-filter",
                    options=[
                        {
                            "label": html.Span(
                                j,
                                title=j,
                                style={
                                    "display": "inline-block",
                                    "maxWidth": "400px",
                                    "overflow": "hidden",
                                    "textOverflow": "ellipsis",
                                    "whiteSpace": "nowrap"
                                }
                            ),
                            "value": j
                        }
                        for j in sorted(df["journal"].unique())
                    ],
                    multi=True,
                    style={"width": "100%"}
                )
            ], className="col-md-4"),
        ], className="row container"),

        html.Div(id="filter-summary", className="container", style={"marginTop": "20px", "fontWeight": "500", "fontSize": "1.1em"}),

        html.Br(),

        html.Div([
            dcc.Graph(id="cost-bar-chart")
        ], className="container"),

        html.Div([
            html.H4("Manuelle Preis-Eintragung"),
            html.Div([
                dcc.Input(id="manual-doi", type="text", placeholder="DOI", style={"marginRight": "10px"}),
                dcc.Input(id="manual-issn", type="text", placeholder="ISSN", style={"marginRight": "10px"}),
                dcc.Input(id="manual-price", type="number", placeholder="Preis (EUR)", style={"marginRight": "10px"}),
                html.Button("Speichern", id="submit-manual", n_clicks=0, className="btn btn-primary")
            ], style={"marginBottom": "20px"}),
            html.Div(id="manual-feedback"),
            html.Br(),
        ], className="container"),

        html.Div([
            html.H4("Publikationsdaten"),
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'minWidth': '150px',
                    'maxWidth': '500px',
                    'whiteSpace': 'nowrap',
                    'overflowX': 'auto',
                    'textOverflow': 'initial'
                },
                style_header={
                    'backgroundColor': '#667eea',
                    'color': 'white',
                    'fontWeight': 'bold'
                }
            ),
            html.Br(),
            html.Button("CSV herunterladen", id="download-button", className="btn btn-success"),
            dcc.Download(id="csv-download")
        ], className="container"),

        html.Div([
            html.H4("Top 10 häufige, nicht gematchte ISSNs"),
            html.Button("Anzeigen / Verstecken", id="toggle-issn-btn", n_clicks=0, className="btn btn-success"),
            html.Div(
                id="unmatched-issn-container",
                children=[
                    dash_table.DataTable(
                        id="unmatched-issn-table",
                        columns=[{"name": "issn", "id": "issn"}, {"name": "count", "id": "count"}],
                        data=[],  # Filled dynamically
                        page_size=10,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '5px',
                            'minWidth': '150px',
                            'maxWidth': '500px',
                            'whiteSpace': 'nowrap',
                            'overflowX': 'auto',
                            'textOverflow': 'initial'
                        },
                        style_header={
                            'backgroundColor': '#667eea',
                            'color': 'white',
                            'fontWeight': 'bold'
                        }
                    )
                ],
                style={"display": "none"}  # Hidden by default
            )
        ], className="container"),

        html.Div([
            html.H4("Match-Quellen"),
            dcc.Graph(id="match-pie-chart")
        ], className="container"),

        html.Div([
            html.H4("Top 10 Journale nach Publikationskosten"),
            dcc.Graph(id="top-journals-chart")
        ], className="container"),

    ]),




