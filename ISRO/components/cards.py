import streamlit as st


def status_card(title, value, subtitle, icon):
    st.markdown(
        f"""
        <div style="
            background:#101B33;
            padding:20px;
            border-radius:18px;
            text-align:center;
            border:1px solid #1E90FF;
            box-shadow:0px 0px 10px rgba(0,229,255,0.15);
        ">
            <h4>{icon} {title}</h4>
            <h2 style="color:#00E5FF;">{value}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )