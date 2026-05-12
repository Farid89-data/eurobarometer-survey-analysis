import pandas as pd
import json
from dash import Dash, dcc, html, dash_table, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# -----------------------
# File paths
# -----------------------
excel_file ="dataset\\Eurobarometer_Standard_99_Spring 2023_volume_A.xlsx"
json_file = "dataset\\eurobarometer_analysis_report.json"

# -----------------------------------
# LOAD EXCEL FILE
# -----------------------------------
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

dataframes = {}
for sheet in sheet_names:
    try:
        dataframes[sheet] = pd.read_excel(excel_file, sheet_name=sheet)
    except Exception as e:
        print(f"Could not load {sheet}: {e}")

# -----------------------------------
# LOAD JSON FILE
# -----------------------------------
with open(json_file, "r", encoding="utf-8") as f:
    report = json.load(f)

metadata = report["metadata"]
quality = report["data_quality"]
analysis = report["analysis"]
processed_sheets = report["sheets_processed"]

# -----------------------------------
# PREPARE DATA
# -----------------------------------
age_data = analysis["age_distribution"]

age_df = pd.DataFrame({
    "Age Group": list(age_data.keys()),
    "Value": list(age_data.values())
})

# Keep only numeric values for chart
age_df = age_df[pd.to_numeric(age_df["Value"], errors="coerce").notnull()]
age_df["Value"] = age_df["Value"].astype(float)

# -----------------------------------
# CREATE CHARTS
# -----------------------------------
age_fig = px.bar(
    age_df,
    x="Age Group",
    y="Value",
    title="Age Distribution"
)

quality_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=quality["completeness_percentage"],
    title={"text": "Data Completeness %"},
    gauge={"axis": {"range": [0, 100]}}
))

# -----------------------------------
# STYLES
# -----------------------------------
card_style = {
    "padding": "20px",
    "border": "1px solid #ddd",
    "borderRadius": "10px",
    "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
    "textAlign": "center",
    "backgroundColor": "#f9f9f9"
}

# -----------------------------------
# DASH APP
# -----------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Eurobarometer Dashboard", style={"textAlign": "center"}),

    dcc.Tabs([

        # OVERVIEW TAB
        dcc.Tab(label="Overview", children=[
            html.Br(),

            html.Div([
                html.Div([
                    html.H3("Survey"),
                    html.P(metadata["survey"])
                ], style=card_style),

                html.Div([
                    html.H3("Sample Size"),
                    html.P(str(metadata["sample_size"]))
                ], style=card_style),

                html.Div([
                    html.H3("Countries"),
                    html.P(str(metadata["countries"]))
                ], style=card_style),

                html.Div([
                    html.H3("Total Records"),
                    html.P(str(quality["total_records"]))
                ], style=card_style),
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "20px",
                "margin": "20px"
            }),

            dcc.Graph(figure=quality_fig),
            dcc.Graph(figure=age_fig)
        ]),

        # SHEETS TAB
        dcc.Tab(label="Processed Sheets", children=[
            html.Br(),
            html.H3("Processed Excel Sheets"),

            dcc.Dropdown(
                id="sheet-dropdown",
                options=[{"label": s, "value": s} for s in sheet_names],
                value=sheet_names[0],
                style={"width": "50%"}
            ),

            html.Br(),
            html.Div(id="table-output")
        ])
    ])
])

# -----------------------------------
# CALLBACK
# -----------------------------------
@app.callback(
    Output("table-output", "children"),
    Input("sheet-dropdown", "value")
)
def update_table(selected_sheet):
    df = dataframes[selected_sheet].head(20)

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px"
        }
    )

# -----------------------------------
# RUN APP
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)