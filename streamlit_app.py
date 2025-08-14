# app.py
import streamlit as st
import pandas as pd
from prophet import Prophet
import snowflake.connector
import plotly.graph_objects as go

# Set the page configuration
st.set_page_config(page_title="Financial Forecasting App", page_icon="📈")

# === Function to connect to Snowflake from the OUTSIDE === #
@st.cache_data
def get_snowflake_data():
    """ Connects to Snowflake using credentials from st.secrets """
    conn = snowflake.connector.connect(**st.secrets["snowflake"])
    query = "SELECT ds, y FROM financial_data ORDER BY ds;"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Ensure column names are lowercase for consistency
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# === Main Application UI === #
st.title("Financial Forecasting App (Snowflake + Prophet)")
st.markdown("This app retrieves financial data from Snowflake and forecasts future revenue using Prophet:")

st.markdown("---")
st.header("Historical Data")
st.markdown("**Select number of days to forecast:**")
forecast_days = st.slider("Days to forecast", 30, 1000, 90, label_visibility="collapsed")
st.write(f"Forecasting for the next **{forecast_days}** days.")

# Load data and handle potential errors
try:
    with st.spinner("Connecting to Snowflake and fetching data..."):
        df = get_snowflake_data()
except Exception as e:
    st.error(f"Could not connect to Snowflake. Please ensure your credentials in Streamlit Cloud Secrets are correct. Error: {e}")
    st.stop()

# --- Visualization Section (to match your image exactly) ---
st.markdown("---")
st.header("Forecast Revenue")

# Model Training and Prediction
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=forecast_days)
forecast = model.predict(future)

# Create the plot
fig = go.Figure()

# Add historical data line
fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Historical'))

# Add the shaded confidence interval
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', line=dict(width=0), showlegend=False
))
fig.add_trace(go.Scatter(
    x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', line=dict(width=0),
    fillcolor='rgba(68, 68, 68, 0.15)', fill='tonexty', showlegend=False
))

# Add the forecast line
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='deepskyblue')))

st.plotly_chart(fig, use_container_width=True)


# --- Forecast Table Section ---
st.markdown("---")
st.header("🧾 Forecast Table")
forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days).rename(
    columns={"ds": "Date", "yhat": "Predicted Revenue", "yhat_lower": "Lower Bound", "yhat_upper": "Upper Bound"}
)
st.dataframe(forecast_table)

# Download Button
csv = forecast_table.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Forecast CSV", csv, "forecast.csv", "text/csv")