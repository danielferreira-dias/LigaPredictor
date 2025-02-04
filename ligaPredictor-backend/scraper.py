from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
import os

# Configurar Selenium
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver_details = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Check Liga Portuguesa Goals
url = "https://www.flashscore.pt/futebol/portugal/liga-portugal/resultados/"
driver.get(url)
time.sleep(5) 

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

GameInfoTemplate = {
    "Game Id": 0,
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

numberGames = 180

def close_cookie_banner():
    try:
        cookie_banner = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))
        )

        cookie_banner.click() 
        # print("Cookies Closed")

        time.sleep(2) 
    except Exception as e:
        print(f"Erro ao tentar fechar o banner de cookies: {e}")

def load_more_games():
    try:
        close_cookie_banner()

        show_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='event__more event__more--static']"))
        )
        
        driver.execute_script("arguments[0].click();", show_more_button)
        # print("Show more")
        
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao tentar carregar mais jogos: {e}")

def getGames():
    gamesJSON = []  

    load_more_games()

    games = driver.find_elements(By.CLASS_NAME, "event__match")  # May have to adjust Class if Flashscore changes it
    for game in games[:numberGames]:
        GameInfo = getGameDetails(game)
        gamesJSON.append(GameInfo)

    return gamesJSON

def getGameDetails(specificGame):
    GameDetails = specificGame.text.split("\n") 
    GameInfo = GameInfoTemplate.copy()
    
    if len(GameDetails) >= 5:  
        GameInfo["Schedule"] = GameDetails[0]
        GameInfo["Home Team"] = GameDetails[1]
        GameInfo["Away Team"] = GameDetails[2]
        GameInfo["Home Goals"] = int(GameDetails[3])
        GameInfo["Away Goals"] = int(GameDetails[4])

        if int(GameDetails[3]) > int(GameDetails[4]): 
            GameInfo["Win"] = GameDetails[1]
            GameInfo["Result"] = "Home"
        elif int(GameDetails[4]) > int(GameDetails[3]):  
            GameInfo["Win"] = GameDetails[2]
            GameInfo["Result"] = "Away"
        else:  # Caso de empate
            GameInfo["Win"] = "Draw"
            GameInfo["Result"] = "Draw"
    
    game_stats_link = specificGame.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
    game_id = game_stats_link.split('/')[4]  

    GameInfo["Game Id"] = game_id

    # url_game_details = f"https://www.flashscore.pt/jogo/{game_id}/#/sumario-do-jogo/sumario-do-jogo"
    # driver_details.get(url_game_details)
    # stats_row = driver_details.find_elements(By.CLASS_NAME, "wcl-row_OFViZ") 

    # Enviar a request
    url_game_details = f"https://global.flashscore.ninja/20/x/feed/df_st_1_{game_id}"

    headers = {
        "x-fsign": "SW9D1eZo"
    }

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
                
                # Verificar se a coleta deve começar
                if obj.get("SE") == "Jogo":
                    collect = True
                elif obj.get("SE") == "1ª Parte":  # Parar a coleta antes de "1ª Parte"
                    break

                # Verificar se o valor de SD está no dicionário de mapeamento
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
                    
                    GameInfo[f"{stat_name} - Home"] = home_value
                    GameInfo[f"{stat_name} - Away"] = away_value

                if collect:
                    result.append(obj)
    else:
        print(f"Erro ao obter os dados. Status code: {response.status_code}")

    return GameInfo 

def createData(GameList):

    data_dir = "LigaPredictor/ligaPredictor-data/liga_portugal"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, "game_data_2024-2025.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(GameList, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {file_path}")


# Save Json File
gamesList = getGames()
createData(gamesList)