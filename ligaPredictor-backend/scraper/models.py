class GameInfo:
    def __init__(self, match_id):
        self.match_id = match_id
        self.schedule = ""
        self.home_team = ""
        self.away_team = ""
        self.home_goals = 0
        self.away_goals = 0
        self.xg_home = 0.0
        self.xg_away = 0.0
        self.possession_home = "0%"
        self.possession_away = "0%"
        self.goal_attempts_home = 0
        self.goal_attempts_away = 0
        self.shots_on_goal_home = 0
        self.shots_on_goal_away = 0
        self.shots_off_goal_home = 0
        self.shots_off_goal_away = 0
        self.shots_blocked_home = 0
        self.shots_blocked_away = 0
        self.great_opportunities_home = 0
        self.great_opportunities_away = 0
        self.corners_home = 0
        self.corners_away = 0
        self.shots_inside_area_home = 0
        self.shots_inside_area_away = 0
        self.shots_outside_area_home = 0
        self.shots_outside_area_away = 0
        self.shots_on_post_home = 0
        self.shots_on_post_away = 0
        self.goalkeeper_defenses_home = 0
        self.goalkeeper_defenses_away = 0
        self.freekicks_home = 0
        self.freekicks_away = 0
        self.offsides_home = 0
        self.offsides_away = 0
        self.fouls_home = 0
        self.fouls_away = 0
        self.yellow_cards_home = 0
        self.yellow_cards_away = 0
        self.red_cards_home = 0
        self.red_cards_away = 0
        self.throws_home = 0
        self.throws_away = 0
        self.passes_home = "0% (0/0)"
        self.passes_away = "0% (0/0)"
        self.passes_last_third_home = "0% (0/0)"
        self.passes_last_third_away = "0% (0/0)"
        self.crosses_home = "0% (0/0)"
        self.crosses_away = "0% (0/0)"
        self.effective_tackles_home = "0% (0/0)"
        self.effective_tackles_away = "0% (0/0)"
        self.tackles_home = 0
        self.tackles_away = 0
        self.interceptions_home = 0
        self.interceptions_away = 0
        self.win = ""
        self.result = ""
    

    def set_result(self):
        if self.home_goals > self.away_goals:
            self.win = self.home_team
            self.result = "Home"
        elif self.home_goals < self.away_goals:
            self.win = self.away_team
            self.result = "Away"
        else:
            self.win = "Draw"
            self.result = "Draw"

    def to_dict(self):
        return self.__dict__