<h1 align="center">🏋️‍♂️ Fitlytics</h1>
<p align="center"><em>Your personal fitness dashboard — powered by Dash, driven by data</em></p>

---

### 🚀 Overview

**Fitlytics** is a sleek Dash-based fitness app designed to track your daily **calorie intake**, **calories burned**, and **nutrition/exercise stats** — all in-memory, with a modern interactive UI and no database setup required.

---

### ✨ Features
- Set and update **daily goals** for calorie intake and burn  
- Log **nutrition data**: calories, protein, fat, carbs  
- Track **exercise sessions** and calories burned  
- Lookup foods via the **Open Food Facts API** or enter manually  
- **All data handled in-memory** using pandas DataFrames  
- **Clean UI** with custom color palette and top-bar navigation  
- **Interactive dashboards** powered by Plotly  
- No authentication required — quick and easy to use  

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Dash](https://img.shields.io/badge/Dash-Plotly-blueviolet?logo=plotly)
![pandas](https://img.shields.io/badge/pandas-DataFrames-purple?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-Graphing-black?logo=plotly)
![API](https://img.shields.io/badge/Open%20Food%20Facts-API-green?logo=fastapi)

---

### ⚙️ Setup Instructions
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python app.py
   ```

## 🎨 Customization
- To use a different nutrition API, update the API logic in `app.py`.
- All data is session-based and will reset when the app restarts.

## 📝 Notes
- For persistent storage, consider exporting/importing data or integrating a database.
- For best experience, use a modern browser.
