# streamlit_financial_forecast
# 📈 Financial Forecasting App (Snowflake + Streamlit)

This is a simple web application that demonstrates a financial forecasting proof of concept (POC).

## What it Does
*   Connects securely to a Snowflake database to retrieve historical revenue data.
*   Uses the Prophet library to create a time-series forecast.
*   Visualizes the historical data, the forecast, and the confidence interval in an interactive chart.
*   Displays the forecast data in a table and provides a CSV download option.

## Technologies Used
- **Cloud Database:** Snowflake
- **Forecasting Model:** Prophet (by Meta)
- **Web App Framework:** Streamlit
- **Plotting Library:** Plotly

## How to Deploy
This application is designed to be deployed on the Streamlit Community Cloud.
1. Fork this repository.
2. Connect your GitHub account to Streamlit Community Cloud.
3. Deploy the repository and add your Snowflake credentials to the Streamlit Secrets management.
