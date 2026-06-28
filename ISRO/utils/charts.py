import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def radiation_chart():

    time = [
        "Now",
        "+15 min",
        "+30 min",
        "+45 min",
        "+1 hr",
        "+2 hr",
        "+4 hr",
        "+6 hr"
    ]

    radiation = [12,15,18,28,22,19,16,13]

    df = pd.DataFrame({
        "Time":time,
        "Radiation":radiation
    })

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Time"],
            y=df["Radiation"],
            mode="lines+markers",
            line=dict(
                color="#00E5FF",
                width=4
            ),
            fill="tozeroy"
        )
    )

    fig.update_layout(

        paper_bgcolor="#050816",

        plot_bgcolor="#101B33",

        font=dict(
            color="white"
        ),

        height=450,

        title="Predicted Electron Flux"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )