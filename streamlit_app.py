# # app.py
# import streamlit as st
# import pandas as pd
# from prophet import Prophet
# import snowflake.connector
# import plotly.graph_objects as go

# # Set the page configuration
# st.set_page_config(page_title="Financial Forecasting App", page_icon="📈")

# # === Function to connect to Snowflake from the OUTSIDE === #
# @st.cache_data
# def get_snowflake_data():
#     """ Connects to Snowflake using credentials from st.secrets """
#     conn = snowflake.connector.connect(**st.secrets["snowflake"])
#     query = "SELECT ds, y FROM financial_data ORDER BY ds;"
#     df = pd.read_sql(query, conn)
#     conn.close()
    
#     # Ensure column names are lowercase for consistency
#     df.columns = ['ds', 'y']
#     df['ds'] = pd.to_datetime(df['ds'])
#     return df

# # === Main Application UI === #
# st.title("Financial Forecasting App")
# st.markdown("This app retrieves financial data from Snowflake and forecasts future revenue using Prophet:")

# st.markdown("---")
# st.header("Historical Data")
# st.markdown("**Select number of days to forecast:**")
# forecast_days = st.slider("Days to forecast", 30, 1000, 90, label_visibility="collapsed")
# st.write(f"Forecasting for the next **{forecast_days}** days.")

# # Load data and handle potential errors
# try:
#     with st.spinner("Connecting to Snowflake and fetching data..."):
#         df = get_snowflake_data()
# except Exception as e:
#     st.error(f"Could not connect to Snowflake. Please ensure your credentials in Streamlit Cloud Secrets are correct. Error: {e}")
#     st.stop()

# # --- Visualization Section (to match your image exactly) ---
# st.markdown("---")
# st.header("Forecast Revenue")

# # Model Training and Prediction
# model = Prophet()
# model.fit(df)
# future = model.make_future_dataframe(periods=forecast_days)
# forecast = model.predict(future)

# # Create the plot
# fig = go.Figure()

# # Add historical data line
# fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Historical'))

# # Add the shaded confidence interval
# fig.add_trace(go.Scatter(
#     x=forecast['ds'], y=forecast['yhat_upper'], mode='lines', line=dict(width=0), showlegend=False
# ))
# fig.add_trace(go.Scatter(
#     x=forecast['ds'], y=forecast['yhat_lower'], mode='lines', line=dict(width=0),
#     fillcolor='rgba(68, 68, 68, 0.15)', fill='tonexty', showlegend=False
# ))

# # Add the forecast line
# fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='deepskyblue')))

# st.plotly_chart(fig, use_container_width=True)


# # --- Forecast Table Section ---
# st.markdown("---")
# st.header("🧾 Forecast Table")
# forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days).rename(
#     columns={"ds": "Date", "yhat": "Predicted Revenue", "yhat_lower": "Lower Bound", "yhat_upper": "Upper Bound"}
# )
# st.dataframe(forecast_table)

# # Download Button
# csv = forecast_table.to_csv(index=False).encode('utf-8')

# st.download_button("⬇️ Download Forecast CSV", csv, "forecast.csv", "text/csv")

import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import snowflake.connector

# Set the page title and icon
st.set_page_config(page_title="Financial Forecasting App", page_icon="📅")

# === Function to connect and fetch data using Streamlit's Secrets === #
@st.cache_data
def get_snowflake_data():
    """
    Connects to Snowflake using credentials from st.secrets and fetches financial data.
    """
    # Establish connection using credentials from Streamlit's secrets
    conn = snowflake.connector.connect(
        **st.secrets["snowflake"]
    )
    
    # Define the SQL query
    query = """
        SELECT ds, y
        FROM financial_data
        WHERE ds >= '2020-01-01'
        ORDER BY ds;
    """
    
    # Execute the query and fetch data into a Pandas DataFrame
    cursor = conn.cursor()
    cursor.execute(query)
    df = cursor.fetch_pandas_all()
    
    # Close the connection
    cursor.close()
    conn.close()
    
    # Convert column names to lowercase to match what Prophet expects
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# === Streamlit App UI === #
st.title("Financial Forecasting App")
st.markdown("This app retrieves historical financial data from Snowflake and generates a monthly forecast.")

# --- Section: Historical Data & Inputs ---
st.markdown("---")

# Create a slider for the user to select the number of MONTHS
st.header("Select Forecast Period")
months_to_forecast = st.slider(
    "Select number of months to forecast:", 
    min_value=1, 
    max_value=48,
    value=36,
    help="Move the slider to choose how many months into the future you'd like to forecast."
)

# Convert selected months to days for the Prophet model
# Using 30.44 as the average number of days in a month (365.25 / 12)
forecast_days = int(months_to_forecast * 30.44)

st.info(f"Forecasting for the next **{months_to_forecast}** months (approximately {forecast_days} days).")


# Load data from Snowflake
try:
    with st.spinner("Connecting to Snowflake and fetching data..."):
        df_historical = get_snowflake_data()
except Exception as e:
    st.error(f"Error connecting to Snowflake or fetching data. Please check your credentials and ensure the 'financial_data' table exists. Error: {e}")
    st.stop()


# --- Section: Forecast Revenue ---
st.markdown("---")
st.header(f"{months_to_forecast}-Month Revenue Forecast")

# Prepare and fit the Prophet model
model = Prophet()
model.fit(df_historical)

# Create future dataframe and make predictions using the calculated number of days
future = model.make_future_dataframe(periods=forecast_days)
forecast = model.predict(future)

# --- Visualization of the Forecast ---
fig = go.Figure()

# 1. Add historical data
fig.add_trace(go.Scatter(
    x=df_historical['ds'], 
    y=df_historical['y'],
    mode='lines',
    name='Historical Revenue',
    line=dict(color='royalblue', width=2)
))

# 2. Add forecast line
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat'],
    mode='lines',
    name='Forecast',
    line=dict(color='deepskyblue', width=2)
))

# 3. Add shaded confidence interval
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat_upper'],
    mode='lines', name='Upper Bound',
    line=dict(width=0),
    showlegend=False
))
fig.add_trace(go.Scatter(
    x=forecast['ds'],
    y=forecast['yhat_lower'],
    mode='lines', name='Lower Bound',
    line=dict(width=0),
    fillcolor='rgba(135, 206, 250, 0.3)',
    fill='tonexty',
    showlegend=False
))

# Update layout for a clean look
fig.update_layout(
    title=f"Revenue Forecast ({months_to_forecast} Months) with Confidence Interval",
    xaxis_title="Date",
    yaxis_title="Revenue",
    legend=dict(x=0.01, y=0.98)
)
st.plotly_chart(fig, use_container_width=True)


# --- Section: Forecast Table ---
st.markdown("---")
st.header("Forecast Data Table")

# Display the forecast data in a table
forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days).rename(
    columns={
        "ds": "Date",
        "yhat": "Predicted Revenue",
        "yhat_lower": "Lower Bound",
        "yhat_upper": "Upper Bound"
    }
)
# Format the date column for better readability
forecast_table['Date'] = forecast_table['Date'].dt.strftime('%b %d, %Y')
st.dataframe(forecast_table)

# Add a download button for the forecast data
csv = forecast_table.to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"Download {months_to_forecast}-Month Forecast CSV",
    data=csv,
    file_name=f"{months_to_forecast}_month_revenue_forecast.csv",
    mime="text/csv",
)
