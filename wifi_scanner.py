import time
import subprocess
import re
import numpy as np
import pandas as pd
import pywifi

history = {}  # ssid -> list of real signal values (max 30)

def get_interface():
    """
    Acquires the Wi-Fi interface using pywifi.
    Raises RuntimeError if no Wi-Fi interface is found.
    """
    wifi = pywifi.PyWiFi()
    interfaces = wifi.interfaces()
    if not interfaces:
        raise RuntimeError("No Wi-Fi interface found. Please ensure Wi-Fi is turned on.")
    return interfaces[0]

def _fallback_netsh_scan():
    """
    Fallback scanner for Windows using the netsh command in case pywifi
    returns empty results or encounters driver permission issues.
    """
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        return []

    networks = []
    current_ssid = None
    lines = output.splitlines()

    for line in lines:
        line_clean = line.strip()
        ssid_match = re.match(r"^SSID\s+\d+\s*:\s*(.*)$", line_clean)
        if ssid_match:
            current_ssid = ssid_match.group(1).strip()
            continue

        signal_match = re.search(r"Signal\s*:\s*(\d+)%", line_clean)
        channel_match = re.search(r"Channel\s*:\s*(\d+)", line_clean)

        if current_ssid and signal_match:
            pct = int(signal_match.group(1))
            dbm = int((pct / 2.0) - 100)
            channel = int(channel_match.group(1)) if channel_match else 1
            freq = 2407 + (channel * 5) if channel <= 14 else 5000 + (channel * 5)

            networks.append({
                "SSID": current_ssid,
                "Signal (dBm)": dbm,
                "Frequency (MHz)": freq,
                "Channel": channel
            })

    return networks

def scan_networks(iface=None):
    """
    Scans for visible Wi-Fi networks and returns a pandas DataFrame.
    """
    data = []
    results = []

    if iface is not None:
        try:
            iface.scan()
            time.sleep(2.5)
            results = iface.scan_results()
        except Exception:
            results = []

    if results:
        results = sorted(results, key=lambda r: getattr(r, "signal", -100), reverse=True)
        seen = set()
        for r in results:
            ssid = r.ssid.strip()
            if not ssid or ssid in seen:
                continue
            seen.add(ssid)

            freq = r.freq
            if freq > 100000:
                freq = freq // 1000

            if freq < 5000:
                channel = max(1, (freq - 2407) // 5)
            else:
                channel = max(36, (freq - 5000) // 5)

            data.append({
                "SSID": ssid,
                "Signal (dBm)": int(r.signal),
                "Frequency (MHz)": int(freq),
                "Channel": int(channel),
            })

    if not data:
        fallback_data = _fallback_netsh_scan()
        if fallback_data:
            seen = set()
            for item in sorted(fallback_data, key=lambda x: x["Signal (dBm)"], reverse=True):
                if item["SSID"] not in seen:
                    seen.add(item["SSID"])
                    data.append(item)

    return pd.DataFrame(data)

def update_history(df):
    """
    Maintains a rolling window of the last 30 signal readings per SSID.
    """
    for _, row in df.iterrows():
        ssid = row["SSID"]
        history.setdefault(ssid, []).append(row["Signal (dBm)"])
        if len(history[ssid]) > 30:
            history[ssid].pop(0)

def analyze(df):
    """
    Analyzes scanned networks: best network, channel congestion, and signal stability.
    """
    if df.empty:
        return {}, {}, {}
    best = df.loc[df["Signal (dBm)"].idxmax()].to_dict()
    stability = {ssid: round(float(np.std(vals)), 2) for ssid, vals in history.items() if len(vals) > 1}
    congestion = {int(k): int(v) for k, v in df.groupby("Channel").size().to_dict().items()}
    return best, stability, congestion

def signal_quality(dbm):
    """
    Classifies signal strength in dBm into descriptive quality ratings without emojis.
    """
    if dbm >= -50: return "Excellent"
    if dbm >= -60: return "Good"
    if dbm >= -70: return "Fair"
    return "Weak"
