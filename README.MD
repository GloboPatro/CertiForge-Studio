CertiForge Studio — Full Documentation

1. Overview
CertiForge Studio is a fully integrated certificate‑creation system.  
It combines:

- a Python backend that loads templates, validates data, and renders certificates  
- a browser‑based frontend that provides the UI for browsing templates, editing layouts, importing data, and generating outputs  

When you start the app, the backend launches automatically and opens the frontend in your browser.  
Everything works together as one unified application.

---

2. Project Structure

`
CertiForge-Studio/
├── backend/
│   ├── app.py
│   ├── config.json
│   ├── remote_templates.json
│   │
│   ├── fonts/
│   ├── templates_store/
│   │
│   └── generator/
│       ├── init.py
│       ├── data_loader.py
│       ├── font_loader.py
│       ├── generate.py
│       ├── importer_utils.py
│       ├── layout_loader.py
│       ├── metadata_loader.py
│       ├── path_utils.py
│       ├── remote_template.py
│       ├── render.py
│       ├── template_loader.py
│       └── validator.py
│
├── frontend/
│   ├── generator.css
│   ├── generator.html
│   ├── generator.js
│   ├── importer.css
│   ├── importer.html
│   ├── importer.js
│   ├── index.html
│   ├── layout_editor.css
│   ├── layout_editor.html
│   ├── layout_editor.js
│   ├── template_browser.css
│   ├── template_browser.html
│   └── template_browser.js
│
├── LICENSE
├── requirements.txt
├── run_app.bat
└── run_app.sh
`

Backend Templates
`
backend/templates/
├── classic/
├── classic_blue/
├── simple/
└── wallhaven-rdqmyq/
`

---

3. How the System Works

Backend → Frontend Integration
When you run the app:

1. The backend starts (app.py)
2. It loads templates, fonts, metadata, and configuration
3. It launches a local server
4. It automatically opens your browser
5. The frontend loads and communicates with the backend

The frontend does not run standalone — it depends on backend endpoints and loaders.

---

4. Backend (Python)

Purpose
The backend handles:

- template loading  
- metadata loading  
- layout loading  
- data importing  
- validation  
- rendering certificates  
- serving the frontend  

Key Components

app.py
Main entrypoint.  
Starts the backend and launches the frontend in the browser.

config.json
Backend configuration (paths, defaults, settings).

remote_templates.json
Definitions for templates that may be fetched or stored externally.

generator/ package
Handles all certificate‑generation logic:

- data_loader.py — loads CSV/JSON data  
- font_loader.py — loads fonts  
- generate.py — orchestrates generation  
- layout_loader.py — loads layout JSON  
- metadata_loader.py — loads template metadata  
- render.py — draws text onto templates  
- template_loader.py — loads template assets  
- validator.py — validates data and layout  
- path_utils.py — centralizes filesystem paths  
- importer_utils.py — helpers for importer  
- remote_template.py — handles remote template definitions  

Templates
Stored in:

`
backend/templates/
`

Each folder contains assets for one template.

---

5. Frontend (Browser UI)

The frontend is served automatically by the backend.

5.1 Index
index.html  
Entry point that links to all modules.

---

5.2 Template Browser
Files:
- template_browser.html
- template_browser.css
- template_browser.js

Purpose:
- Display available templates  
- Load metadata from backend  
- Show previews  
- Select a template  
- Redirect to layout editor:

`
layout_editor.html?template=<id>
`

---

5.3 Layout Editor
Files:
- layout_editor.html
- layout_editor.css
- layout_editor.js

Purpose:
- Load template background  
- Add and move text fields  
- Change font size, color, alignment  
- Rename fields  
- Snap‑grid for clean alignment  
- Live preview  
- Export layout configuration (JSON)  
- Send layout to backend for validation  

---

5.4 Importer
Files:
- importer.html
- importer.css
- importer.js

Purpose:
- Import CSV/JSON data  
- Clean and validate data  
- Prepare dataset for generator  
- Uses backend importer utilities  

---

5.5 Generator
Files:
- generator.html
- generator.css
- generator.js

Purpose:
- Load template + layout + data  
- Send generation request to backend  
- Backend renders certificates  
- Frontend displays previews  
- Download final outputs  

---

6. Installation
Requirements
- Python 3  
- Browser  
- Dependencies from requirements.txt

Install backend dependencies:

`
pip install -r requirements.txt
`

---

7. Running the App

Windows
`
run_app.bat
`

Linux / macOS
`
bash run_app.sh
`

What happens
- Backend starts  
- Backend opens your browser  
- Frontend loads automatically  
- Everything is connected and ready  

You do not manually open HTML files.

---

8. Usage Flow

1. Start the app
Backend launches → browser opens → Template Browser appears.

2. Choose a template
Select one from the list.

3. Edit layout
Adjust fields, colors, sizes, positions.

4. Import data
Load names or other values.

5. Generate certificates
Backend renders them.  
Frontend shows previews and download options.

---

9. Adding New Templates

1. Create a folder inside:

`
backend/templates/
`

2. Add template image(s)
3. Add metadata (via backend loaders or JSON)
4. Restart the app  
5. Template appears in the browser automatically

---

10. Current Limitations

- No user accounts  
- No cloud storage  
- No remote template syncing yet  
- Importer still evolving  
- Layout saving/loading may expand later  

---

11. Future Expansion

- Full backend API  
- Remote template hosting  
- PDF export  
- Cloud project storage  
- Multi‑language UI  
- Advanced importer  
- Template maInstallation
