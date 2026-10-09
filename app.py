import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wifi_scanner import get_interface, scan_networks, update_history, analyze, signal_quality, history

st.set_page_config(page_title="WiFi Analyzer", layout="wide")

# --- Session state initialization ---
if "running" not in st.session_state:
    st.session_state.running = False
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0
if "iface" not in st.session_state:
    try:
        st.session_state.iface = get_interface()
        st.session_state.iface_error = None
        st.session_state.iface_name = getattr(st.session_state.iface, "name", lambda: "Wi-Fi Adapter")()
    except Exception as e:
        st.session_state.iface = None
        st.session_state.iface_error = str(e)
        st.session_state.iface_name = "Unavailable"

# --- Sidebar Controls ---
st.sidebar.title("Controls")

if st.session_state.iface_name != "Unavailable":
    st.sidebar.success(f"Adapter: {st.session_state.iface_name}")
else:
    st.sidebar.warning("Adapter: Not detected")

refresh_interval = st.sidebar.slider("Refresh every (seconds)", 3, 15, 5)

col_start, col_stop = st.sidebar.columns(2)
if col_start.button("Start", use_container_width=True):
    st.session_state.running = True
if col_stop.button("Stop", use_container_width=True):
    st.session_state.running = False

manual_scan = st.sidebar.button("Scan Once", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.metric("Total Scans", st.session_state.scan_count)

# --- Title Header ---
st.title("WiFi Network Analyzer")
status = st.empty()

# --- Interface error check ---
if st.session_state.iface_error and not manual_scan:
    st.error(f"Could not access Wi-Fi adapter: {st.session_state.iface_error}\n\nMake sure Wi-Fi is enabled in Windows settings.")
    st.stop()

if not st.session_state.running and not manual_scan and st.session_state.scan_count == 0:
    status.info("Click 'Start' in the sidebar to begin live continuous scanning, or 'Scan Once' for a single snapshot.")
    st.stop()

# --- Scan networks ---
status.warning(f"Scanning networks... (scan #{st.session_state.scan_count + 1})")

try:
    df = scan_networks(st.session_state.iface)
except Exception as e:
    st.error(f"Scan failed: {e}")
    st.stop()

if df.empty:
    status.error("No networks found. Make sure Wi-Fi is switched on.")
    if st.session_state.running:
        time.sleep(refresh_interval)
        st.rerun()
    st.stop()

update_history(df)
best, stability, congestion = analyze(df)
st.session_state.scan_count += 1

df["Quality"] = df["Signal (dBm)"].apply(signal_quality)
df_display = df.sort_values("Signal (dBm)", ascending=False).reset_index(drop=True)

status.success(f"Scan #{st.session_state.scan_count} complete — {len(df)} networks detected")

# --- Best Network Highlight Card ---
if best:
    st.subheader("Best Network")
    best_quality = signal_quality(int(best['Signal (dBm)']))
    st.success(
        f"{best['SSID']} | {best['Signal (dBm)']} dBm | Channel {best['Channel']} ({best.get('Frequency (MHz)', 'N/A')} MHz) | Quality: {best_quality}"
    )

# --- Network Table ---
st.subheader("Detected Networks")
st.dataframe(df_display, width="stretch")

st.markdown("---")
col1, col2 = st.columns(2)

# --- Bar Chart: Signal Strength ---
with col1:
    st.subheader("Signal Strength (dBm)")
    colors = []
    for s in df_display["Signal (dBm)"]:
        if s >= -50: colors.append("#2ecc71")
        elif s >= -60: colors.append("#f1c40f")
        elif s >= -70: colors.append("#e67e22")
        else: colors.append("#e74c3c")

    fig, ax = plt.subplots(figsize=(6, max(3.5, len(df_display) * 0.45)))
    widths = [s - (-100) for s in df_display["Signal (dBm)"]]
    bars = ax.barh(df_display["SSID"], widths, left=-100, color=colors)
    ax.set_xlabel("Signal Strength (dBm)")
    ax.set_xlim(-100, -20)
    ax.invert_yaxis()
    ax.axvline(-50, color="#2ecc71", linestyle="--", linewidth=1, alpha=0.7, label="Excellent (-50)")
    ax.axvline(-70, color="#e74c3c", linestyle="--", linewidth=1, alpha=0.7, label="Weak (-70)")

    for bar, val in zip(bars, df_display["Signal (dBm)"]):
        ax.text(
            val + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{val} dBm",
            va="center",
            fontsize=8,
            color="#333333"
        )

    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# --- Channel Congestion ---
with col2:
    st.subheader("Channel Congestion")
    if congestion:
        fig2, ax2 = plt.subplots(figsize=(6, max(3.5, len(congestion) * 0.45)))
        ch_labels = [f"Ch {k}" for k in congestion.keys()]
        ch_vals = list(congestion.values())
        max_val = max(ch_vals) if ch_vals else 1
        bar_colors = ["#e74c3c" if v > 1 else "#3498db" for v in ch_vals]
        ax2.bar(ch_labels, ch_vals, color=bar_colors)
        ax2.set_xlabel("Channel")
        ax2.set_ylabel("Number of Networks")
        ax2.set_yticks(range(0, max_val + 2))
        ax2.grid(axis="y", linestyle=":", alpha=0.6)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("No channel data available.")

st.markdown("---")
col3, col4 = st.columns(2)

# --- Signal History Line Chart ---
with col3:
    st.subheader("Signal History (Live)")
    tracked = {s: v for s, v in history.items() if len(v) > 1}
    if tracked:
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        for ssid, vals in tracked.items():
            ax3.plot(vals, marker="o", markersize=3, label=ssid, linewidth=1.5)
        ax3.set_xlabel("Scan Index")
        ax3.set_ylabel("Signal (dBm)")
        ax3.set_ylim(-100, -20)
        ax3.legend(fontsize=7, loc="lower right")
        ax3.grid(True, linestyle=":", alpha=0.5)
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
    else:
        st.info("Signal history builds after 2 or more scans.")

# --- Stability Table ---
with col4:
    st.subheader("Signal Stability")
    if stability:
        stab_df = pd.DataFrame(stability.items(), columns=["SSID", "Std Dev (dBm)"]).sort_values("Std Dev (dBm)")
        stab_df["Verdict"] = stab_df["Std Dev (dBm)"].apply(
            lambda x: "Stable" if x < 3 else ("Moderate" if x < 5 else "Unstable")
        )
        st.dataframe(stab_df.reset_index(drop=True), width="stretch")
    else:
        st.info("Stability analysis builds after 2 or more scans.")

# --- Auto-refresh if running ---
if st.session_state.running:
    time.sleep(refresh_interval)
    st.rerun()
