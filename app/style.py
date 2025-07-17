import streamlit as st

def set_style():
    st.markdown("""
        <style>
        body {
            background-color: #111;
            color: white;
        }
        .title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .divider {
            border-left: 2px solid #444;
            height: 100%;
        }
        .station-title {
            font-size: 1.5rem;
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .metric-box {
            background: #222;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-box.normal {
            background: #1e7d32; /* Verde */
        }
        .metric-box.alerta {
            background: #b71c1c; /* Vermelho */
        }
        .metric-label {
            font-size: 1rem;
            font-weight: bold;
        }
        .metric-value {
            font-size: 1.3rem;
            margin-top: 4px;
        }
        </style>
    """, unsafe_allow_html=True)
