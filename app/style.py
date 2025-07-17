import streamlit as st

def set_style():
    st.markdown("""
        <style>
        body {
            background-color: #121212;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            padding: 2rem;
        }
        .title {
            font-size: 42px;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-bottom: 40px;
        }
        .station-title {
            font-size: 26px;
            font-weight: 700;
            color: white;
            margin: 20px 0 15px;
            text-align: center;
        }
        .metric-box {
            border-radius: 8px;
            padding: 6px 14px;
            margin-bottom: 6px;
            box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-box.normal {
            background-color: #28a745;
        }
        .metric-box.alerta {
            background-color: #ff0000;
            animation: pulse 1s infinite;
        }
        .metric-label {
            font-weight: bold;
            font-size: 17px;
            color: white;
        }
        .metric-value {
            font-size: 26px;
            color: white;
        }
        .divider {
            border-left: 2px solid rgba(255, 255, 255, 0.1);
            height: 100%;
            margin: 0 10px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        </style>
    """, unsafe_allow_html=True)
