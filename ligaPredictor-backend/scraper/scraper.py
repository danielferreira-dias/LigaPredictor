from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from models import GameInfo
import requests
import json
import os

# Global Variables
MapStatistics = {
    "432": {"name": "xG", "type": float},
    "12": {"name": "Possession", "type": str},
    "34": {"name": "Goal Attempts", "type": int},
    "13": {"name": "Shots on Goal", "type": int},
    "14": {"name": "Shots off Goal", "type": int},
    "158": {"name": "Shots Blocked", "type": int},
    "459": {"name": "Great Opportunities", "type": int},
    "16": {"name": "Corners", "type": int},
    "461": {"name": "Shots inside the area", "type": int},
    "463": {"name": "Shots outside the area", "type": int},
    "457": {"name": "Shots on the Post", "type": int},
    "19": {"name": "Goalkeeper Defenses", "type": int},
    "15": {"name": "Freekicks", "type": int},
    "17": {"name": "Offsides", "type": int},
    "21": {"name": "Fouls", "type": int},
    "23": {"name": "Yellow Cards", "type": int},
    "22": {"name": "Red Cards", "type": int},
    "18": {"name": "Throws", "type": int},
    "342": {"name": "Passes", "type": float},
    "467": {"name": "Passes in the last third", "type": float},
    "433": {"name": "Crosses", "type": float},
    "475": {"name": "Effective Tackles", "type": float},
    "479": {"name": "Tackles", "type": int},
    "434": {"name": "Interceptions", "type": int}
}

headers = {
    "x-fsign": "SW9D1eZo"
}

def fetchGameURL():
    urls_2024_2025 = [
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_0_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_1_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_2_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_3_0_pt_1",
    ]
    urls_2023_2024 = [
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_0_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_1_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_2_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_3_0_pt_1",
    ]
    urls_2022_2023 = [
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_0_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_1_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_2_0_pt_1",
        "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_3_0_pt_1",
    ]

    season_url_map = {
        "urls_2024_2025": urls_2024_2025,
        "urls_2023_2024": urls_2023_2024,
        "urls_2022_2023": urls_2022_2023,
    }

    all_merged_results = []

    for season in season_url_map:
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(getGames, season_url_map[season]))

        merged_results = [item for sublist in results for item in sublist]
        # createData(merged_results, season)
        print(f"{len(merged_results)} from {season}")
        all_merged_results.append((merged_results))
    
    all_merged_results_final = [item for sublist in all_merged_results for item in sublist]
    print(len(all_merged_results_final))
    createData(all_merged_results_final, "all_games")

def getGames(url):
    gamesJSON = []  
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = response.text.split("~AA÷")[1:]  
        for match_section in matches:
            parts = match_section.split("¬")
            match_id = match_section.split("¬")[0]

             # Create a new GameInfo instance for this match
            Game = GameInfo(match_id)
            
            for part in parts:
                if "÷" in part:
                    key, value = part.split("÷", 1)
                    if key == "AD":  
                        Game.schedule = datetime.fromtimestamp(int(value)).isoformat()
                    elif key == "CX":
                        Game.home_team = value
                    elif key == "AF":
                        Game.away_team = value
                    elif key == "AG":
                        Game.home_goals = int(value)
                    elif key == "AH":
                        Game.away_goals = int(value)
            
            # Determine the winner
            Game.set_result()

            ## Request for Details
            url_game_details = f"https://global.flashscore.ninja/20/x/feed/df_st_1_{match_id}"
            response = requests.get(url_game_details, headers=headers)

            # Verificar o status da resposta
            if response.status_code == 200:
                
                data = response.text
                # Substituir delimitadores
                data = data.replace("¬", ",").replace("÷", ":").replace("~", "\n")
                # Dividir o texto em seções
                sections = data.split("\n")

                result = []
                for section in sections:
                    if section:
                        items = section.split(",")
                        obj = {}
                        for item in items:
                            key_value = item.split(":")
                            if len(key_value) == 2:
                                key, value = key_value
                                obj[key] = value
                        
                        if obj.get("SE") == "Jogo":
                            collect = True
                        elif obj.get("SE") == "1ª Parte":  
                            break

                        sd_value = obj.get("SD")

                        if sd_value in MapStatistics:
                            stat_info = MapStatistics[sd_value]
                            stat_name = stat_info["name"]
                            stat_type = stat_info["type"]


                            try:
                                sh_value = obj.get("SH", 0)
                                si_value = obj.get("SI", 0)

                                if "%" in str(sh_value):
                                    home_value_text = str(sh_value).split("%")
                                    home_value = float(home_value_text[0]) 
                                else:
                                    home_value = stat_type(sh_value)

                                if "%" in str(si_value):
                                    away_value_text = str(si_value).split("%")
                                    away_value = float(away_value_text[0]) 
                                else:
                                    away_value = stat_type(si_value)

                            except (ValueError, TypeError) as e:
                                print(f"Error processing values for {stat_name}: {e}")
                                home_value = None
                                away_value = None

                            # Update the corresponding attributes in the Game object
                            attr_home = f"{stat_name.lower().replace(' ', '_')}_home"
                            attr_away = f"{stat_name.lower().replace(' ', '_')}_away"
                            
                            if hasattr(Game, attr_home) and hasattr(Game, attr_away):
                                setattr(Game, attr_home, home_value)
                                setattr(Game, attr_away, away_value)

                        if collect:
                            result.append(obj)
            else:
                print(f"Erro ao obter os dados. Status code: {response.status_code}")

            # Add the updated GameInfoTemplate to the games list
            gamesJSON.append(Game.to_dict())
    else:
        print(f"Erro ao obter os dados. Status code: {response.status_code}")
    return gamesJSON

def createData(GameList, season):
    data_dir = "LigaPredictor/ligaPredictor-data/liga_portugal"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # file_path = os.path.join(data_dir, f"game_data_{season}.json")
    file_path = os.path.join(data_dir, f"game_data_{season}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(GameList, f, ensure_ascii=False, indent=4)
    print(f"Dados armazenados - game_data_{season}.json")


fetchGameURL()