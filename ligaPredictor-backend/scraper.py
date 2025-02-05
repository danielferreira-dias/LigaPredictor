from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import requests
import os


# Configurar Selenium
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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

# Function to convert the match date and time to the desired format
def convert_match_time(match_time_str):
    # Assuming the match time is in the format "03.02. 20:45"
    match_time = datetime.strptime(match_time_str, "%d.%m. %H:%M")
    
    # If the month is July (07) or earlier, set the year to 2025
    if match_time.month <= 7:
        match_time = match_time.replace(year=2025)
    else:
        match_time = match_time.replace(year=2024)  # Default to 2024 if after July
    
    return match_time.isoformat()

def loadInitialGames():
    gamesJSON = []  
    # url = "https://www.flashscore.pt/futebol/portugal/liga-portugal/resultados/"
    # url = "https://www.flashscore.pt/futebol/portugal/liga-portugal-betclic-2023-2024/resultados/"
    url = "https://www.flashscore.pt/futebol/portugal/liga-portugal-betclic-2022-2023/resultados/"
    driver.get(url)

    Matches = driver.find_elements(By.CLASS_NAME, "event__match")
    for Match in Matches:
        Match_ID_Stats = Match.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
        Match_ID = Match_ID_Stats.split('/')[4]  

        # Split the match text into a list
        Match_Text = Match.text.split('\n')  # Split by new lines
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

        GameInfoTemplate["Match Id"] = Match_ID
        GameInfoTemplate["Schedule"] = convert_match_time(Match_Text[0])
        GameInfoTemplate["Home Team"] = Match_Text[1]
        GameInfoTemplate["Away Team"] = Match_Text[2]
        GameInfoTemplate["Home Goals"] = int(Match_Text[3])
        GameInfoTemplate["Away Goals"] = int(Match_Text[4])

        if int(Match_Text[3]) > int(Match_Text[4]): 
            GameInfoTemplate["Win"] = Match_Text[1]
            GameInfoTemplate["Result"] = "Home"
        elif int(Match_Text[4]) > int(Match_Text[3]):  
            GameInfoTemplate["Win"] = Match_Text[2]
            GameInfoTemplate["Result"] = "Away"
        else:  # Caso de empate
            GameInfoTemplate["Win"] = "Draw"
            GameInfoTemplate["Result"] = "Draw"

        getGameDetails(Match_ID, GameInfoTemplate)

        gamesJSON.append(GameInfoTemplate.copy())
    
    return gamesJSON

def getGames():
    gamesJSON = []  
    # url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_184_1_0_pt_1"
    # url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_183_1_0_pt_1" 
    url = "https://global.flashscore.ninja/20/x/feed/tr_1_155_UmMRoGzp_182_1_0_pt_1" 
    
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
    
    initialGames = loadInitialGames()

    finalGames = getGames()

    all_games = initialGames + finalGames

    createData(all_games)

loadAllGames()
# loadInitialGames()