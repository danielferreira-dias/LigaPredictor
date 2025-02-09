import json
import os
import time
import numpy
import requests
from models import Game, seasons
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
    standings = {}

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

                            # Get Pre-game Form
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
                            game.headToHead_home_wins, game.headToHead_away_wins, game.headToHead_draws  = fetchLastHeadToHead(event["id"], session, game)

                            # Simulate result (replace with real match result logic)
                            sorted_standings_home = sort_standings(standings, "home_points")
                            sorted_standings_away = sort_standings(standings, "away_points")

                            game.home_team_homeClassification= find_team_rank(sorted_standings_home, game.home_team_id)
                            game.away_team_homeClassification= find_team_rank(sorted_standings_home, game.away_team_id)
                            game.home_team_awayClassification= find_team_rank(sorted_standings_away, game.home_team_id)
                            game.away_team_awayClassification= find_team_rank(sorted_standings_away, game.away_team_id)

                            game.match_Referee = fetchGameReferee(event["id"], session)

                            game.bestAvg_homePlayer, game.bestAvg_homePlayer_Rating, game.bestAvg_awayPlayer, game.bestAvg_awayPlayer_Rating  = fetchBestPlayers(event["id"], session)

                            update_standings(standings, game.home_team_id, game.away_team_id, game.home_goals , game.away_goals, game )

                            game.setFinalResult()
                            
                            gameJSON.append(game.to_dict())
                        except KeyError as key_err:
                            print(f"Missing key in event data: {key_err}")
                            continue  # Skip this event
            else:
                print(f"Failed to fetch data, status code: {response.status_code} - FetchSeasons - {season_id}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - FetchSeasons - {season_id}")
        except KeyError as key_err:
            print(f"Missing expected key in response: {key_err} - FetchSeasons - {season_id}")
        except Exception as e:
            print(f"Unexpected Error: - FetchSeasons - {season_id} ", e)

    return gameJSON

def sort_standings(standings, type_Standings: str):
    # Convert standings dictionary to a list of tuples (team_id, team_data)
    standings_list = [
        (team_id, data) for team_id, data in standings.items()
    ]

    # Sort by points (descending), then goal difference (descending), then goals scored (descending)
    standings_list.sort(
        key=lambda x: (
            x[1][type_Standings],
            x[1]["goals_scored"] - x[1]["goals_conceded"],  # Goal difference
            x[1]["goals_scored"]
        ),
        reverse=True  # Sort in descending order
    )

    return standings_list

def update_standings(standings, home_team_id: int, away_team_id: int, home_goals: int, away_goals: int, game):
    if home_team_id not in standings:
        standings[home_team_id] = {"home_points": 0, "away_points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_scored": 0, "goals_conceded": 0, "games_played": 0, "avg_goals_scored": 0, "avg_goals_conceded": 0}
    if away_team_id not in standings:
        standings[away_team_id] = {"home_points": 0, "away_points": 0, "wins": 0, "draws": 0, "losses": 0, "goals_scored": 0, "goals_conceded": 0, "games_played": 0, "avg_goals_scored": 0, "avg_goals_conceded": 0}

    if standings[home_team_id]["games_played"] > 0:
        game.home_team_avgGoalsScored = standings[home_team_id]["goals_scored"] / standings[home_team_id]["games_played"]
        game.home_team_avgGoalsConceded = standings[home_team_id]["goals_conceded"] / standings[home_team_id]["games_played"]

    if standings[away_team_id]["games_played"] > 0:
        game.away_team_avgGoalsScored = standings[away_team_id]["goals_scored"] / standings[away_team_id]["games_played"]
        game.away_team_avgGoalsConceded  = standings[away_team_id]["goals_conceded"] / standings[away_team_id]["games_played"]

    standings[home_team_id]["goals_scored"] += home_goals
    standings[home_team_id]["goals_conceded"] += away_goals
    standings[away_team_id]["goals_scored"] += away_goals
    standings[away_team_id]["goals_conceded"] += home_goals

    # Update game counts
    standings[home_team_id]["games_played"] += 1
    standings[away_team_id]["games_played"] += 1

    if home_goals > away_goals:
        standings[home_team_id]["wins"] += 1
        standings[away_team_id]["losses"] += 1
        standings[home_team_id]["home_points"] += 3
    elif home_goals < away_goals:
        standings[away_team_id]["wins"] += 1
        standings[home_team_id]["losses"] += 1
        standings[away_team_id]["away_points"] += 3
    else:
        standings[home_team_id]["home_points"] += 1
        standings[away_team_id]["away_points"] += 1
        standings[home_team_id]["draws"] += 1
        standings[away_team_id]["draws"] += 1

def find_team_rank(sorted_standings, team_id):
    for rank, (tid, _) in enumerate(sorted_standings, start=1):
        if tid == team_id:
            return rank
    return 0

def getPreGameform(match_id: int, game, session: cureq.Session ):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/pregame-form"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")

        if response.status_code  == 200:
            fetched_Data = response.json()

            game.home_team_currentClassification = fetched_Data['homeTeam']['position']
            game.home_avgRating = float(fetched_Data['homeTeam']['avgRating'])
            
            game.away_team_currentClassification = fetched_Data['awayTeam']['position']
            game.away_avgRating = float(fetched_Data['awayTeam']['avgRating'])

            for wins in fetched_Data['homeTeam']['form']:
                if wins == "W":
                    game.wins_in_last_5_matches_home += 1

            for wins in fetched_Data['awayTeam']['form']:
                if wins == "W":
                    game.wins_in_last_5_matches_away += 1

        else:
            print(f"Failed to fetch data, status code: {response.status_code} - Pre game form - {match_id}")  

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
                    game.home_team_state = 1
                elif game.away_team_id == club['id']:
                    game.away_team_state = 1
                else:
                    game.home_team_state = 0
                    game.away_team_state = 0
        else:
            print(f"Failed to fetch data, status code: {response.status_code} - Promoted Clubs - {season_id}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - fetchPromotedClubs - {season_id}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err} - fetchPromotedClubs - {season_id}")
    except Exception as e:
        print(f"Unexpected Error: - fetchPromotedClubs - {season_id}", e)

def fetchLastHeadToHead(match_id: int, session: cureq.Session, game):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/h2h"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")
        if response.status_code  == 200:
            fetched_Data = response.json()
            return fetched_Data['teamDuel']['homeWins'], fetched_Data['teamDuel']['awayWins'], fetched_Data['teamDuel']['draws']
        else:   
            print(f"Failed to fetch data, status code: {response.status_code} - Head to Head - {match_id}")  

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Head to Head - {match_id}" )
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err} - Head to Head - {match_id} ")
    except Exception as e:
        print(f"Unexpected Error: - Head to Head - {match_id} ", e)

def fetchGameReferee(match_id: int, session: cureq.Session):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")
        response.raise_for_status() 
        fetched_data = response.json()

        return fetched_data['event']['referee']['name']
    except requests.exceptions.RequestException as err:
        print(f"Error occurred while fetching data: {err} - {match_id}")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err} - {match_id}")

    return "Referee not assigned"

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
        print(f"An error occurred while uploading data: {e} - JSON Upload")

def fetchBestPlayers(match_id: int, session: cureq.Session):
    url = f"https://www.sofascore.com/api/v1/event/{match_id}/best-players/summary"

    try:
        response = session.get(url, headers=headers, impersonate="chrome")
        if response.status_code == 200:
            fetched_Data = response.json()
            return fetched_Data['bestHomeTeamPlayers'][0]['player']['name'], float(fetched_Data['bestHomeTeamPlayers'][0]['value']), fetched_Data['bestAwayTeamPlayers'][0]['player']['name'], float(fetched_Data['bestAwayTeamPlayers'][0]['value'])
        else:
            print(f"Failed to fetch data, status code: {response.status_code} - {match_id} in fetchBestPlayers")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {match_id} in fetchBestPlayers")
    except KeyError as key_err:
        print(f"Missing expected key in response: {key_err} - {match_id} in fetchBestPlayers")
    except Exception as e:
        print(f"Unexpected Error: - {match_id} in fetchBestPlayers ", e )

def main():
    session = new_session()
    upload_info_to_json(63670, session)
    time.sleep(10)
    upload_info_to_json(52769, session)


main()

