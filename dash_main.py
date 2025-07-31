from dash import Dash
from dash_components.layout import create_layout
from dash_components.callbacks import register_callbacks
from db.db import load_data_from_db

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
]

# runs dash and loads template ,layouts
def run_dash():
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    app.title = "Publikationskosten Dashboard"
    app.server = app.server

    with open("templates/index_string.html", "r", encoding="utf-8") as f:
        app.index_string = f.read()

    df = load_data_from_db()
    app.layout = create_layout(df)

    # Register  callbacks
    register_callbacks(app)

    app.run(debug=True, use_reloader=False)
