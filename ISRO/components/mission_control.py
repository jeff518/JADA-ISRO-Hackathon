import streamlit as st


def show_mission_control():

    st.divider()

    st.header("🛰 Mission Control")

    left, center, right = st.columns(3)

    # =========================
    # Satellite Status
    # =========================
    with left:

        st.markdown("### 🛰 Satellite Status")

        satellites = [
            ("GSAT-10", "🟢 Operational"),
            ("GSAT-18", "🟢 Operational"),
            ("INSAT-3D", "🟡 Warning"),
            ("GSAT-30", "🔴 High Risk")
        ]

        for name, status in satellites:

            st.markdown(
                f"""
                <div style="
                    background:#101B33;
                    padding:15px;
                    margin-bottom:10px;
                    border-radius:12px;
                    border-left:5px solid #00E5FF;
                ">
                    <b>{name}</b><br>
                    {status}
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # AI Prediction
    # =========================
    with center:

        st.markdown("### 🤖 AI Prediction")

        st.metric("Risk Level", "HIGH", "+18%")
        st.metric("Confidence", "97.8%", "+0.5%")
        st.metric("Forecast Window", "45 Minutes")

    # =========================
    # Alerts
    # =========================
    with right:

        st.markdown("### 🚨 Live Alerts")

        alerts = [
            "⚠ Solar flare detected",
            "⚠ Electron flux increasing",
            "⚠ Magnetic disturbance expected",
            "✅ AI model updated successfully"
        ]

        for alert in alerts:
            st.warning(alert)