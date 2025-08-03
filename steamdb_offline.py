"""
SteamDBOffline
--------------
Author: Khaled Developer
GitHub: https://github.com/khaled-dev-loper/steamdb-offline

A lightweight Python tool to enumerate installed Steam games **offline** (no API key or Steam login needed).
This script parses local Steam files (appmanifest, libraryfolders.vdf) to get information about installed games, including Steam ID, name, install location, and banners.

License:
--------
MIT License

Copyright (c) 2025 Khaled Developer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import os
import json
import glob
import re

class SteamDBOffline:
    """
    SteamDBOffline is a Python class for reading installed Steam games
    information from local files (`appmanifest_*.acf`, `libraryfolders.vdf`),
    without using Steam's online API.

    Main features:
        - Works fully offline.
        - Detects all your Steam libraries automatically.
        - Extracts game name, Steam ID, install path, banners, etc.
        - Outputs as a list of dictionaries for further processing.

    Args:
        main_steamapps_path (str): Path to the main 'steamapps' directory. Default is Windows' default Steam location.

    Example:
        steamdb = SteamDBOffline()
        games = steamdb.get_games()
        for g in games:
            print(g["name"], g["install_path"])

    Author: Khaled Developer
    GitHub: https://github.com/khaled-dev-loper/steamdb-offline
    License: MIT
    """
    VERSION = "1.0.0"
    def __init__(self, main_steamapps_path = r"C:\Program Files (x86)\Steam\steamapps"):
        """
        Initializes the SteamDBOffline instance.

        Args:
            main_steamapps_path (str): Path to main steamapps directory.
        """
        self.main_steamapps_path = main_steamapps_path

    def __get_library_paths(self, steamapps_path):
        """
        Finds all Steam library folders where games may be installed.

        Args:
            steamapps_path (str): Path to a steamapps folder to start from.

        Returns:
            list[str]: A list of library 'steamapps' folder paths.
        """
        lib_paths = [steamapps_path]
        vdf_file = os.path.join(steamapps_path, 'libraryfolders.vdf')
        if not os.path.exists(vdf_file):
            return lib_paths

        with open(vdf_file, encoding="utf-8") as f:
            data = f.read()
        # New and old Steam library VDF formats supported
        re_path_new = re.findall(r'"path"\s+"(.*?)"', data)
        re_path_old = re.findall(r'"\d+"\s+"(.*?)"', data)
        for path in re_path_new + re_path_old:
            path = path.replace('\\\\', '\\').strip()
            app_folder = os.path.join(path, 'steamapps')
            if os.path.exists(app_folder) and app_folder not in lib_paths:
                lib_paths.append(app_folder)
        lib_paths = list(set(lib_paths))
        return lib_paths

    def __parse_acf(self, acf_path):
        """
        Parses a single appmanifest_*.acf file to extract game information.

        Args:
            acf_path (str): Path to the ACF file.

        Returns:
            dict: Information about the game (steam_id, name, installdir, etc.)
        """
        info = {}

        if not os.path.exists(acf_path):
            return info
        
        with open(acf_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith('"appid"'):
                    info["steam_id"] = line.split('"')[3]
                elif line.startswith('"name"'):
                    info["name"] = line.split('"')[3]
                elif line.startswith('"installdir"'):
                    info["installdir"] = line.split('"')[3]
                elif line.startswith('"LastUpdated"'):
                    info["last_updated"] = line.split('"')[3]
                elif line.startswith('"StateFlags"'):
                    info["stateflags"] = line.split('"')[3]
                elif line.startswith('"SizeOnDisk"'):
                    info["size_on_disk"] = line.split('"')[3]
        return info

    def get_games(self):
        """
        Enumerates all installed Steam games by scanning all library folders.

        Returns:
            list[dict]: A list of dictionaries, each containing game information:
                - steam_id (str): Steam App ID
                - name (str): Game name
                - logo (str): URL to logo image
                - installdir (str): Folder name
                - install_path (str): Full install path
                - launch_url (str): Steam protocol URL (e.g., steam://run/730)
                - banner (str): URL to game header image
                - big_banner (str): URL to large hero banner
                - vertical_banner (str): URL to vertical banner
                - horizontal_banner (str): URL to horizontal banner
                - info_banner (str): URL to info banner
                - last_updated (str): Last updated timestamp (if present)
                - stateflags (str): Install state flags (if present)
                - size_on_disk (str): Size in bytes (if present)
        """
        library_paths = self.__get_library_paths(self.main_steamapps_path)
        games = []
        for steamapps_path in library_paths:
            for acf_file in glob.glob(os.path.join(steamapps_path, "appmanifest_*.acf")):
                info = self.__parse_acf(acf_file)
                if not info: 
                    continue
                # Filter out Steamworks Redistributables
                if info.get("name", "").lower().startswith("steamworks"):
                    continue

                info["install_path"]         = os.path.join(steamapps_path, "common", info.get("installdir", ""))
                info["launch_url"]           = f"steam://run/{info['steam_id']}"
                info["logo"]                 = f"https://cdn.steamstatic.com/steam/apps/{info['steam_id']}/logo.png"
                info["banner"]               = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{info['steam_id']}/header.jpg"
                info["big_banner"]           = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{info['steam_id']}/library_hero.jpg"
                info["vertical_banner"]      = f"https://cdn.steamstatic.com/steam/apps/{info['steam_id']}/library_600x900.jpg"
                info["horizontal_banner"]    = f"https://cdn.steamstatic.com/steam/apps/{info['steam_id']}/capsule_231x87.jpg"
                info["info_banner"]          = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{info['steam_id']}/page_bg_generated_v6b.jpg"
                games.append(info)
        return games

# Example usage:
if __name__ == "__main__":
    steamdb = SteamDBOffline()
    games = steamdb.get_games()
    filename = "my_steam_local_games_full.json"
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(games, outfile, ensure_ascii=False, indent=4)
        print(f"File '{filename}' Created.")
    print(f"{len(games)} Games found!\n")
    for i, g in enumerate(games):
        print(f"{i+1}. {g['name']}")
