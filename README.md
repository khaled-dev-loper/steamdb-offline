# SteamDB-Offline for python

> **Offline Steam Games Scanner – No API Key Needed**
---

## Overview

SteamDB-Offline is a lightweight Python tool that scans your Steam library **OFFLINE** and lists all installed games by parsing local Steam files.  
It works without any Steam API key or login – everything is done locally on your PC!

- **Detects all your Steam Library folders**
- **Finds installed games and extracts useful info**
- **Returns details like name, Steam ID, install path, banner links and more**
- 100% open-source

---

## Features

- 📴 **Offline operation:** No Internet required
- 🔍 **Automatic detection** of all Steam library locations (multi-drive supported)
- 📄 **Outputs game list as JSON** for integration or backup purposes
- 🔗 **Includes launch URLs** and artwork/banner links

---

## Requirements

- Python 3.6+
- You must know your **Steam `steamapps` folder location**
    - Default on Windows:  
      `C:\Program Files (x86)\Steam\steamapps`

---
## Limitations
- Only lists installed games (not your entire Steam library/account)
- Tested on Windows. For Linux paths, you must edit the main steamapps path.
---
## API / Code Example
You can import and use this in your own Python code:
```python
from steamdb_offline import SteamDBOffline
steamdb = SteamDBOffline(r"C:\Program Files (x86)\Steam\steamapps")
games = steamdb.get_games()
for g in games:
    print(g["name"], g["install_path"])
```
---
## Installation

Just **download** or **clone this repository**:

```bash
git clone https://github.com/khaled-dev-loper/steamdb-offline.git
```
