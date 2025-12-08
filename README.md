Camera Repair Dashboard - Full Deployable Project
-------------------------------------------------
Features:
- Login (SQLite users) with Admin / Viewer roles
- SQLite backend stored at data/devices.db
- Overview, Records, Import, Admin pages
- Import Excel (handles column names like your upload), Export Excel
- Filters, search, pagination, edit, delete (admin)
- KPI dashboard (cards + pie chart)
Run locally:
  pip install -r requirements.txt
  streamlit run app.py
Default demo accounts:
  admin / adminpass
  viewer / viewpass
