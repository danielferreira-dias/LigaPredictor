class Game:
    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team = ""
        self.away_team = ""
        self.home_team_id = ""
        self.away_team_id = ""
        self.home_team_state = 0
        self.away_team_state = 0
        self.home_goals = 0
        self.away_goals = 0
        self.home_team_currentClassification = 0
        self.away_team_currentClassification = 0
        self.home_team_avgGoalsScored = 0.0
        self.away_team_avgGoalsScored = 0.0
        self.home_team_avgGoalsConceded = 0.0
        self.away_team_avgGoalsConceded = 0.0
        self.home_avgRating = 0.0
        self.away_avgRating = 0.0
        self.wins_in_last_5_matches_home = 0
        self.wins_in_last_5_matches_away = 0
        self.headToHead_home_wins = 0
        self.headToHead_away_wins = 0
        self.headToHead_draws = 0
        self.home_team_homeClassification = 0
        self.home_team_awayClassification = 0
        self.away_team_homeClassification = 0
        self.away_team_awayClassification = 0
        self.bestAvg_homePlayer = ""
        self.bestAvg_homePlayer_Rating = 0.0
        self.bestAvg_awayPlayer = ""
        self.bestAvg_awayPlayer_Rating = 0.0
        self.match_Referee = ""
        self.winnerCode = 0
        self.result = ""

    def setFinalResult(self):
        if self.winnerCode == 3:
            self.result = "Draw"
        elif self.winnerCode == 1:
            self.result = self.home_team
        else:
            self.result = self.away_team
    
    def to_dict(self):
        return self.__dict__
    
class Player:
    def __init__(self):
        self.name = ""
        self.id = 0
        self.team = ""
        self.team_id = 0
        self.ranking = 0.0
        self.position = ""
    

    def to_dict(self):
        return self.__dict__

seasons = {
    "Liga Portugal": [
        { "name": "Liga Portugal 24/25", "year": "24/25", "id": 63670 },
        { "name": "Liga Portugal 23/24", "year": "23/24", "id": 52769 },
        { "name": "Primeira Liga 22/23", "year": "22/23", "id": 42655 },
        { "name": "Primeira Liga 21/22", "year": "21/22", "id": 37358 },
        { "name": "Primeira Liga 20/21", "year": "20/21", "id": 32456 },
        { "name": "Primeira Liga 19/20", "year": "19/20", "id": 24150 },
        { "name": "Primeira Liga 18/19", "year": "18/19", "id": 17714 },
        { "name": "Primeira Liga 17/18", "year": "17/18", "id": 13539 },
        { "name": "Primeira Liga 16/17", "year": "16/17", "id": 11924 }
    ],
    "UEFA Champions League": [
        { "name": "UEFA Champions League 24/25", "year": "24/25", "id": 61644 },
        { "name": "UEFA Champions League 23/24", "year": "23/24", "id": 52162 },
        { "name": "UEFA Champions League 22/23", "year": "22/23", "id": 41897 },
        { "name": "UEFA Champions League 21/22", "year": "21/22", "id": 36886 },
        { "name": "UEFA Champions League 19/20", "year": "19/20", "id": 23766 },
        { "name": "UEFA Champions League 18/19", "year": "18/19", "id": 17351 },
        { "name": "UEFA Champions League 17/18", "year": "17/18", "id": 13415 },
        { "name": "UEFA Champions League 16/17", "year": "16/17", "id": 11773 },
        { "name": "UEFA Champions League 15/16", "year": "15/16", "id": 10390 },
        { "name": "Champions League 14/15", "year": "14/15", "id": 8226 },
        { "name": "Champions League 13/14", "year": "13/14", "id": 6359 },
        { "name": "UEFA Champions League 12/13", "year": "12/13", "id": 4788 },
        { "name": "Champions League 11/12", "year": "11/12", "id": 3402 },
        { "name": "Champions League 10/11", "year": "10/11", "id": 2764 },
        { "name": "Champions League 07/08", "year": "07/08", "id": 603 },
        { "name": "Champions League 06/07", "year": "06/07", "id": 15 },
        { "name": "Champions League 05/06", "year": "05/06", "id": 14 }
    ]
}
