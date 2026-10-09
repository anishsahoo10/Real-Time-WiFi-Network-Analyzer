#OUTPUT
<img width="500" height="250" alt="Screenshot 2026-10-09 214026" src="https://github.com/user-attachments/assets/b4bdc160-16b2-42fa-abe6-9d1566c60968" />
<img width="500" height="250" alt="Screenshot 2026-10-09 214046" src="https://github.com/user-attachments/assets/846bc1ac-ead1-4063-baf4-9c7e40db25f2" />


# WiFi Network Analyzer

A lightweight Python dashboard to scan local Wi-Fi networks in real time, inspect signal strengths, and identify congested channels. Built with Streamlit, PyWiFi, Pandas, and Matplotlib.

## What it does

- Scans available 2.4 GHz and 5 GHz Wi-Fi networks using your local wireless card.
- Plots signal strength (dBm) on an inverted bar chart with standard thresholds (-50 dBm excellent, -70 dBm weak).
- Shows channel congestion to help pick less crowded router channels.
- Tracks rolling signal fluctuations over time (last 30 scans) to measure connection stability.
- Includes a netsh fallback on Windows so scanning still works even if the PyWiFi driver interface runs into permission limits.

## Project Structure

- `wifi_scanner.py`: Core scanner and metrics logic. Handles driver calls, frequency-to-channel conversion, deduplication, and rolling history.
- `app.py`: Streamlit frontend with charts, live refresh loop, and controls.
- `requirements.txt`: Python package dependencies.
- `run.bat`: Batch script to auto-setup `.venv` and start the app on Windows.
- `run.ps1`: PowerShell runner script.

## Setup and Running

### Quickest way (Windows)

Double-click `run.bat` or run it from a terminal. If your Wi-Fi adapter requires administrator rights for raw scanning, right-click and select "Run as administrator".

The batch file creates a virtual environment, installs the dependencies, and launches the web interface.

### Running manually from Command Prompt (cmd)

If you are using standard Command Prompt:

```cmd
cd /d "d:\all\wifi analyzer"
.\.venv\Scripts\activate.bat
streamlit run app.py
```

Or run directly without activating:

```cmd
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Running manually from PowerShell

```powershell
cd "d:\all\wifi analyzer"
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Once running, the dashboard opens in your browser at `http://localhost:8501`.

## Controls

- Start: Begins continuous live scanning at your chosen interval.
- Stop: Pauses the auto-refresh loop so you can inspect current data.
- Scan Once: Captures a single scan snapshot without looping.
- Refresh Slider: Adjusts the delay between scans (default is 5 seconds).

## Notes & Technical Details

- Signal metrics: Signal is reported in dBm. Closer to 0 is stronger (-30 dBm is very strong, -80 dBm is weak).
- Dual-band networks: Routers often broadcast the same SSID on both 2.4 GHz and 5 GHz. The scanner sorts by signal strength and keeps the strongest entry per SSID.
- Windows driver quirks: On some Windows installs, native Wi-Fi drivers can be slow to return results via COM. If PyWiFi returns empty results, the scanner automatically falls back to Windows `netsh wlan show networks mode=bssid` so the UI does not hang or show empty results.
=======
# Real-Time-WiFi-Network-Analyzer
>>>>>>> acce9de5fd2ea1e62cc7d46d857550373cdc5d49
