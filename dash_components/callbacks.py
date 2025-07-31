from dash import Input, Output, State, dcc, html, callback_context
from db.insights import top_unmatched_issns  # adjust import path if needed

import plotly.express as px
from db.db import load_data_from_db, get_engine, get_table_name
import pandas as pd
from sqlalchemy import text


def register_callbacks(app):
    # main update callback triggered by any update or filterchange
    @app.callback(
        [Output("cost-bar-chart", "figure"),
         Output("data-table", "data"),
         Output("manual-feedback", "children"),
         Output("match-pie-chart", "figure"),
         Output("filter-summary", "children")],
        Output("top-journals-chart", "figure"),
        [Input("submit-manual", "n_clicks"),
         Input("year-filter", "value"),
         Input("country-filter", "value"),
         Input("journal-filter", "value")],
        [State("manual-doi", "value"),
         State("manual-issn", "value"),
         State("manual-price", "value")]
    )
    def update_all(n_clicks, selected_years, selected_countries, selected_journals, doi, issn, price):
        #determine what caused the callback
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

        feedback = ""
        df = load_data_from_db()

        #for handeling manual eingabe based on issn or doi
        if triggered_id == "submit-manual" and price:
            doi = str(doi).strip().lower() if doi else ""
            issn = str(issn).strip().lower() if issn else ""

            match = pd.Series([False] * len(df))
            if doi:
                match |= df["doi"] == doi
            elif issn:
                match |= df["issn"] == issn

            updated = match.sum()
            if updated:
                to_update = match
                #update direct to database
                if to_update.any():
                    updated_rows = 0
                    engine = get_engine()
                    with engine.begin() as conn:
                        for i, row in df[to_update].iterrows():
                            if row["doi"]:
                                conn.execute(text(f"""
                                    UPDATE {get_table_name()}
                                    SET cost_price_eur = :price,
                                        total_price_eur = :price,
                                        match_source = 'manual'
                                    WHERE doi = :doi
                                """), {"price": price, "doi": row["doi"]})
                            elif row["issn"]:
                                conn.execute(text(f"""
                                    UPDATE {get_table_name()}
                                    SET cost_price_eur = :price,
                                        total_price_eur = :price,
                                        match_source = 'manual'
                                    WHERE issn = :issn
                                """), {"price": price, "issn": row["issn"]})
                            updated_rows += 1

                    feedback = f"{updated_rows} Eintrag(e) in der Datenbank aktualisiert."
                else:
                    feedback = "Eintrag(e) bereits manuell gesetzt."
            else:
                feedback = " Kein Treffer gefunden."

        # Reload
        df = load_data_from_db()

        # apply filter
        filtered_df = df.copy()
        if selected_years:
            filtered_df = filtered_df[filtered_df["year"].isin(selected_years)]
        if selected_countries:
            filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]
        if selected_journals:
            filtered_df = filtered_df[filtered_df["journal"].isin(selected_journals)]

        # for bar chart
        bar_data = filtered_df[filtered_df["total_price_eur"].notna()]
        bar_fig = px.bar(
            bar_data.groupby("year")["total_price_eur"].mean().reset_index(),
            x="year", y="total_price_eur",
            title="Durchschnittliche Publikationskosten pro Jahr",
            labels={"total_price_eur": "Kosten (EUR)"}
        )

        #for pie chart based on match
        pie_data = df["match_source"].fillna("Unmatched").value_counts().reset_index()
        pie_data.columns = ["source", "count"]
        pie_fig = px.pie(pie_data, names="source", values="count", title="Matching Coverage inklusive Manuell")

        #for bar chart, top 10 journals by total publication cost
        top_journals_data = filtered_df[filtered_df["total_price_eur"].notna()]
        top_journals = (top_journals_data
                        .groupby("journal")["total_price_eur"]
                        .sum()
                        .sort_values(ascending=False)
                        .head(10)
                        .reset_index()
                        )

        top_journals_fig = px.bar(
            top_journals,
            x="journal",
            y="total_price_eur",
            title="Top 10 Journale nach Gesamtpublikationskosten",
            labels={"journal": "Journal", "total_price_eur": "Kosten (EUR)"},
        )
        top_journals_fig.update_layout(xaxis_tickangle=-45)

        summary_parts = []
        price_data = filtered_df["total_price_eur"]
        with_price = price_data.notna().sum()
        without_price = price_data.isna().sum()
        total = price_data.dropna().sum()
        avg = price_data.dropna().mean()

        #conditional formatting based on filter combination
        if selected_countries and selected_journals and selected_years:
            summary_parts.append(
                f"In {', '.join(selected_countries)} für {', '.join(selected_journals)} im Jahr {', '.join(map(str, selected_years))}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR pro Publikation, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_countries and selected_journals:
            summary_parts.append(
                f"In {', '.join(selected_countries)} für {', '.join(selected_journals)}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_countries and selected_years:
            summary_parts.append(
                f"In {', '.join(selected_countries)} im Jahr {', '.join(map(str, selected_years))}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_journals and selected_years:
            summary_parts.append(
                f"Für {', '.join(selected_journals)} im Jahr {', '.join(map(str, selected_years))}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_countries:
            summary_parts.append(
                f"In {', '.join(selected_countries)}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_journals:
            summary_parts.append(
                f"Für {', '.join(selected_journals)}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        elif selected_years:
            summary_parts.append(
                f"Im Jahr {', '.join(map(str, selected_years))}: Gesamtkosten {total:,.2f} EUR (∅ {avg:,.2f} EUR, {with_price} mit Preis, {without_price} ohne Preis)"
            )
        else:
            summary_parts.append(
                f"Gesamtkosten: {total:,.2f} EUR (∅ {avg:,.2f} EUR pro Publikation, {with_price} mit Preis, {without_price} ohne Preis)"
            )

        summary_text = html.Ul([html.Li(part) for part in summary_parts])

        return bar_fig, filtered_df.to_dict("records"), feedback, pie_fig, summary_text, top_journals_fig

    #callback : show/hid unmatched issn table
    @app.callback(
        [Output("unmatched-issn-container", "style"),
         Output("unmatched-issn-table", "data")],
        [Input("toggle-issn-btn", "n_clicks")]
    )
    def toggle_unmatched_issns(n_clicks):
        if n_clicks and n_clicks % 2 == 1:
            df = top_unmatched_issns()
            return {"display": "block"}, df.to_dict("records")
        return {"display": "none"}, []

    #callback for csv downloading
    @app.callback(
        Output("csv-download", "data"),
        Input("download-button", "n_clicks"),
        prevent_initial_call=True
    )
    def download_csv(n_clicks):
        df = load_data_from_db()
        df.to_csv("pubmed_update_manual_entry.csv", index=False)
        return dcc.send_file("pubmed_update_manual_entry.csv")
