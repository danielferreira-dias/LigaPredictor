import json
import os
import time
import numpy
import requests
from models import Game
from curl_cffi import requests as cureq

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def new_session():
    session = cureq.Session( impersonate="chrome" )
    return session

def fetchSeasonCurrentRound(season_id):
    url = f"https://www.sofascore.com/api/v1/unique-tournament/238/season/{season_id}/rounds"
    
    try:
        response = cureq.get(url, headers=headers, impersonate="chrome")
        response.raise_for_status()

        fetched_Data = response.json()
        lastround = fetched_Data['rounds'][-1]['round']
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err}")
    except Exception as e:
        print(f"Unexpected Error: ", e)

    return lastround

def fetchSeasonRoundsPlayed(season_id: int, session: cureq.Session):
    gameJSON = []

    for round_num  in range(1, fetchSeasonCurrentRound(season_id)):
        url = f"https://www.sofascore.com/api/v1/unique-tournament/238/season/{season_id}/events/round/{round_num}"
        time.sleep( 1.0 +  numpy.random.uniform(0,1) )

        try:
            response = session.get(url, headers=headers, impersonate="chrome")
            if response.status_code  == 200:
                fetched_Data = response.json()
                for event  in fetched_Data['events']:
                    if event.get("status", {}).get("type") == "finished":
                        try:
                            game = Game(event["id"])
                            game.home_team = event["homeTeam"]["name"]
                            game.home_goals = event["homeScore"]["display"]
                            game.home_team_id = event["homeTeam"]["id"]
                            game.away_team = event["awayTeam"]["name"]
                            game.away_goals = event["awayScore"]["display"]
                            game.away_team_id = event["awayTeam"]["id"]
                            game.winnerCode = event["winnerCode"]

                            ## Get Pre-game Form
                            if round_num >= 2:
                                getPreGameform(event["id"], game, session)
                            else:
                                game.home_position = 0
                                game.home_avgRating = 0.0

                                game.away_position = 0
                                game.away_avgRating = 0.0

                            ## Check if Team was Promoted
                            fetchPromotedClubs(season_id, session, game)

                            ## Check Last 10 Matches Between Teams
                            fetchLastHeadToHead(event["id"], session, game)

                            # name, age, city, _ = get_user_info()
                            game.home_team_home_position = fetchStandings(season_id, session, game.home_team_id, "home")
                            game.home_team_away_position = fetchStandings(season_id, session, game.home_team_id, "away")
                            game.away_team_home_position = fetchStandings(season_id, session, game.away_team_id, "home")
                            game.away_team_away_position = fetchStandings(season_id, session, game.away_team_id, "away")
                            
                            game.setFinalResult()
                            gameJSON.append(game.to_dict())
                        except KeyError as key_err:
                            print(f"Missing key in event data: {key_err}")
                            continue  # Skip this event
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except KeyError as key_err:
            print(f"Missing expected key in response: {key_err}")
        except Exception as e:
            print(f"Unexpected Error: ", e)

    return gameJSON

def getPreGameform(match_id: int, game, session: cureq.Session ):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/pregame-form"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")

        if response.status_code  == 200:
            fetched_Data = response.json()

            game.home_position = fetched_Data['homeTeam']['position']
            game.home_avgRating = fetched_Data['homeTeam']['avgRating']
            
            game.away_position = fetched_Data['awayTeam']['position']
            game.away_avgRating = fetched_Data['awayTeam']['avgRating']

            for wins in fetched_Data['homeTeam']['form']:
                if wins == "W":
                    game.wins_in_last_5_matches_home += 1

            for wins in fetched_Data['awayTeam']['form']:
                if wins == "W":
                    game.wins_in_last_5_matches_away += 1

        else:
            print(f"Failed to fetch data, status code: {response.status_code}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err}")
    except Exception as e:
        print(f"Unexpected Error: ", e)

def fetchPromotedClubs(season_id: int, session: cureq.Session, game):
    url = f"https://www.sofascore.com/api/v1/unique-tournament/238/season/{season_id}/info"
    try: 
        response = session.get(url, headers=headers, impersonate="chrome")
        if response.status_code  == 200:
            fetched_Data = response.json()
            for club in fetched_Data['info']['newcomersLowerDivision']:
                if game.home_team_id == club['id']:
                    game.home_team_state = "Promoted"
                elif game.away_team_id == club['id']:
                    game.away_team_state = "Promoted"
                else:
                    game.home_team_state = "Stable"
                    game.away_team_state = "Stable"
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err}")
    except Exception as e:
        print(f"Unexpected Error: ", e)

def fetchLastHeadToHead(match_id: int, session: cureq.Session, game):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/h2h"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")

        if response.status_code  == 200:
            fetched_Data = response.json()
            game.headToHead_home_wins = fetched_Data['teamDuel']['homeWins']
            game.headToHead_away_wins = fetched_Data['teamDuel']['awayWins']
            game.headToHead_draws = fetched_Data['teamDuel']['draws']
        else:   
            print(f"Failed to fetch data, status code: {response.status_code}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err}")
    except Exception as e:
        print(f"Unexpected Error: ", e)

def fetchStandings(season: int, session: cureq.Session, club_id: int, type_standings: str):
    url = f"https://www.sofascore.com/api/v1/tournament/52/season/{season}/standings/{type_standings}"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")

        if response.status_code  == 200:
            fetched_Data = response.json()
            
            for position in fetched_Data['standings']:
                for row in range(0, len(position['rows'])):
                    if club_id == position['rows'][row]['team']['id']:
                        return (position['rows'][row]['position'])
        else:   
            print(f"Failed to fetch data, status code: {response.status_code}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err}")
    except Exception as e:
        print(f"Unexpected Error: ", e)

def upload_info_to_json(season: int, session: cureq.Session):

    data_dir = "./ligaPredictor-data/liga_portugal"
    # Create the directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Define the file path for the season's JSON data
    file_path = os.path.join(data_dir, f"game_data_{season}.json")
    
    try:

        # Fetch season data and write it to the JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            season_data = fetchSeasonRoundsPlayed(season, session) 
            json.dump(season_data, f, ensure_ascii=False, indent=4)
        
        print(f"Data for season {season} has been saved successfully at {file_path}.")
    
    except Exception as e:
        print(f"An error occurred while uploading data: {e}")

def main():
    session = new_session()
    upload_info_to_json(63670, session)
    


main()

