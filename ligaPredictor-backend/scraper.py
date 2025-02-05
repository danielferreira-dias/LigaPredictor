from datetime import datetime
import json
import requests
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
    "342": {"name": "Passes", "type": str},
    "467": {"name": "Passes in the last third", "type": str},
    "433": {"name": "Crosses", "type": str},
    "475": {"name": "Effective Tackles", "type": str},
    "479": {"name": "Tackles", "type": str},
    "434": {"name": "Interceptions", "type": int}
}

headers = {
    "x-fsign": "SW9D1eZo"
}

def getGames():
    gamesJSON = []  
    ### INITIAL GAMES
    # url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_1_0_pt_1"
    # UmMRoGzp_0_url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_0_0_pt_1" 
    UmMRoGzp_0_url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_0_0_pt_1" 

    ##### NEXT GAMES
    # url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_1_0_pt_1"
    # UmMRoGzp_1_url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_1_0_pt_1" 
    UmMRoGzp_1_url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_176_1_0_pt_1" 

    for url in [UmMRoGzp_0_url, UmMRoGzp_1_url]:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            matches = response.text.split("~AA÷")[1:]  
            for match_section in matches:
                parts = match_section.split("¬")
                match_id = match_section.split("¬")[0]
                GameInfoTemplate = {
                    "Match Id": 0,
                    "Schedule": "",
                    "Home Team": "",
                    "Away Team": "",
                    "Home Goals": 0,
                    "Away Goals": 0,
                    "xG - Home": 0.0,
                    "xG - Away": 0.0,
                    "Possession - Home": "0%",
                    "Possession - Away": "0%",
                    "Goal Attempts - Home": 0,
                    "Goal Attempts - Away": 0,
                    "Shots on Goal - Home": 0,
                    "Shots on Goal - Away": 0,
                    "Shots off Goal - Home": 0,
                    "Shots off Goal - Away": 0,
                    "Shots Blocked - Home": 0,
                    "Shots Blocked - Away": 0,
                    "Great Opportunities - Home": 0,
                    "Great Opportunities - Away": 0,
                    "Corners - Home": 0,
                    "Corners - Away": 0,
                    "Shots inside the area - Home": 0,
                    "Shots inside the area - Away": 0,
                    "Shots outside the area - Home": 0,
                    "Shots outside the area - Away": 0,
                    "Shots on the Post - Home": 0,
                    "Shots on the Post - Away": 0,
                    "Goalkeeper Defenses - Home": 0,
                    "Goalkeeper Defenses - Away": 0,
                    "Freekicks - Home": 0,
                    "Freekicks - Away": 0,
                    "Offsides - Home": 0,
                    "Offsides - Away": 0,
                    "Fouls - Home": 0,
                    "Fouls - Away": 0,
                    "Yellow Cards - Home": 0,
                    "Yellow Cards - Away": 0,
                    "Red Cards - Home": 0,
                    "Red Cards - Away": 0,
                    "Throws - Home": 0,
                    "Throws - Away": 0,
                    "Passes - Home": "0% (0/0)",
                    "Passes - Away": "0% (0/0)",
                    "Passes in the last third - Home": "0% (0/0)",
                    "Passes in the last third - Away": "0% (0/0)",
                    "Crosses - Home": "0% (0/0)",
                    "Crosses - Away": "0% (0/0)",
                    "Effective Tackles - Home": "0% (0/0)",
                    "Effective Tackles - Away": "0% (0/0)",
                    "Tackles - Home": 0,
                    "Tackles - Away": 0,
                    "Interceptions - Home": 0,
                    "Interceptions - Away": 0,
                    "Win": "",
                    "Result": "",
                }
                GameInfoTemplate["Match Id"] = match_id
                
                for part in parts:
                    if "÷" in part:
                        key, value = part.split("÷", 1)
                        if key == "AD":  
                            GameInfoTemplate["Schedule"] = datetime.fromtimestamp(int(value)).isoformat()
                        elif key == "CX":  # Home team name
                            GameInfoTemplate["Home Team"] = value
                        elif key == "AF":  # Away team name
                            GameInfoTemplate["Away Team"] = value
                        elif key == "AG":  # Home score
                            GameInfoTemplate["Home Goals"] = int(value)
                        elif key == "AH":  # Away score
                            GameInfoTemplate["Away Goals"]= int(value)
                    if GameInfoTemplate["Home Goals"] > GameInfoTemplate["Away Goals"] :
                        GameInfoTemplate["Win"]= GameInfoTemplate["Home Team"]
                        GameInfoTemplate["Result"] = "Home"
                    elif GameInfoTemplate["Home Goals"] < GameInfoTemplate["Away Goals"] :
                        GameInfoTemplate["Win"]= GameInfoTemplate["Away Team"]
                        GameInfoTemplate["Result"] = "Away"
                    else:
                        GameInfoTemplate["Win"]= "Draw"
                        GameInfoTemplate["Result"] = "Draw"

                getGameDetails(match_id, GameInfoTemplate)

                # Add the updated GameInfoTemplate to the games list
                gamesJSON.append(GameInfoTemplate.copy())
        else:
            print(f"Erro ao obter os dados. Status code: {response.status_code}")

    return gamesJSON

def getGameDetails(gameId, GameInfoTemplate):
    # Enviar a request
    url_game_details = f"https://global.flashscore.ninja/20/x/feed/df_st_1_{gameId}"

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
                        home_value = stat_type(obj.get("SH", 0))
                        away_value = stat_type(obj.get("SI", 0))
                    except ValueError:
                        home_value = None
                        away_value = None
                    
                    GameInfoTemplate[f"{stat_name} - Home"] = home_value
                    GameInfoTemplate[f"{stat_name} - Away"] = away_value
                

                if collect:
                    result.append(obj)
    else:
        print(f"Erro ao obter os dados. Status code: {response.status_code}")

def createData(GameList):
    data_dir = "LigaPredictor/ligaPredictor-data/liga_portugal"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # file_path = os.path.join(data_dir, "game_data_2024-2025.json")
    # file_path = os.path.join(data_dir, "game_data_2023-2024.json")
    file_path = os.path.join(data_dir, "game_data_2022-2023.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(GameList, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {file_path}")

def loadAllGames():
    Games = getGames()
    createData(Games)

loadAllGames()