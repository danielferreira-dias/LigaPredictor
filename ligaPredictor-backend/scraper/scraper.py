import json
import os
import requests
from models import GameInfo
import http.client

def fetchSeasonCurrentRound(season_id):
    url = f"https://www.sofascore.com/api/v1/unique-tournament/238/season/{season_id}/rounds"
    
    try:
        response = requests.get(url)
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

def fetchSeasonRoundsPlayed(season_id):
    gameJSON = []
    conn = http.client.HTTPSConnection("www.sofascore.com")

    for round_num  in range(1, fetchSeasonCurrentRound(season_id)):
        url = f"https://www.sofascore.com/api/v1/unique-tournament/238/season/{season_id}/events/round/{round_num}"

        try:
            conn.request("GET", url)

            response = conn.getresponse()
            if response.status == 200:
                fetched_Data = json.loads(response.read().decode("utf-8"))
                for event  in fetched_Data['events']:
                    if event.get("status", {}).get("type") == "finished":
                        try:
                            game = GameInfo(event["id"])
                            game.home_team = event["homeTeam"]["name"]
                            game.home_goals = event["homeScore"]["display"]
                            game.home_team_id = event["homeTeam"]["id"]
                            game.away_team = event["awayTeam"]["name"]
                            game.away_goals = event["awayScore"]["display"]
                            game.away_team_id = event["awayTeam"]["id"]
                            game.winnerCode = event["winnerCode"]

                            gameJSON.append(game.to_dict())
                        except KeyError as key_err:
                            print(f"Missing key in event data: {key_err}")
                            continue  # Skip this event
            else:
                print(f"Failed to fetch data, status code: {response.status}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except KeyError as key_err:
            print(f"Missing expected key in response: {key_err}")
        except Exception as e:
            print(f"Unexpected Error: ", e)

    return gameJSON

def upload_info_to_json(season):

    data_dir = "./ligaPredictor-data/liga_portugal"
    # Create the directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Define the file path for the season's JSON data
    file_path = os.path.join(data_dir, f"game_data_{season}.json")
    
    try:
        # Fetch season data and write it to the JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            season_data = fetchSeasonRoundsPlayed(season)  # Replace with your actual function call
            json.dump(season_data, f, ensure_ascii=False, indent=4)
        
        print(f"Data for season {season} has been saved successfully at {file_path}.")
    
    except Exception as e:
        print(f"An error occurred while uploading data: {e}")

upload_info_to_json(63670)