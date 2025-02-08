class GameInfo:
    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team = ""
        self.away_team = ""
        self.home_team_id = ""
        self.away_team_id = ""
        self.home_goals = 0
        self.away_goals = 0
        self.winnerCode = 0
    
    def set_statistic(self, key, home_value, away_value):
        home_attr = f"{key}_home"
        away_attr = f"{key}_away"
        
        # Set the statistic as attributes on the class
        setattr(self, home_attr, home_value)
        setattr(self, away_attr, away_value)
        
    def to_dict(self):
        return self.__dict__