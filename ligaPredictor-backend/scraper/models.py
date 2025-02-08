class Game:
    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team = ""
        self.away_team = ""
        self.home_team_id = ""
        self.away_team_id = ""
        self.home_team_state = ""
        self.away_team_state = ""
        self.home_goals = 0
        self.away_goals = 0
        self.home_position = 0
        self.away_position = 0
        self.home_avgRating = 0.0
        self.away_avgRating = 0.0
        self.wins_in_last_5_matches_home = 0
        self.wins_in_last_5_matches_away = 0
        self.headToHead_home_wins = 0
        self.headToHead_away_wins = 0
        self.headToHead_draws = 0
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
