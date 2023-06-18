import random


def pass_line_bet(amount):
    odds = 244/251 # from here: https://www.gambling.com/ca/online-casinos/strategy/craps-odds-explained-3312200
    prob_win = odds / (odds + 1)
    win = random.random() < prob_win
    payout = 1 * amount
    if win:
        return payout
    else:
        return -payout

def dont_pass_bet(amount):
    odds = 949 / 976 # from here: https://www.gambling.com/ca/online-casinos/strategy/craps-odds-explained-3312200
    prob_win = odds / (odds + 1)
    win = random.random() < prob_win
    payout = 1 * amount
    if win:
        return payout
    else:
        return -payout

def free_odds_bet(amount):
    # TODO: implement the free odds bet using come / don't come -> https://www.mypokercoaching.com/craps-strategy/
    pass

class CrapsSimulator():

    def __init__(self, bet_type, bet_amount, stop_loss, stop_win, max_rolls_per_game, games_to_sim):
        if not bet_type in ['Pass Line Bet', 'Don\'t Pass Bet', 'Free Odds Bet']:
            raise Exception('Invalid Bet Type')
        self.bet_type = bet_type
        self.bet_amount = bet_amount
        self.stop_loss = stop_loss
        self.stop_win = stop_win
        self.max_rolls_per_game = max_rolls_per_game
        self.games_to_sim = games_to_sim
    
    def play_game(self):
        game_result = {
            'rolls': [],
            'result': 0,
            'stop_loss': self.stop_loss,
            'stop_win': self.stop_win,
            'max_rolls_per_game': self.max_rolls_per_game
        }
        for roll in range(self.max_rolls_per_game):
            roll_result = self._play_roll()
            game_result['rolls'].append(roll_result)
            game_result['result'] += roll_result
            if game_result['result'] <= game_result['stop_loss']:
                break
            if game_result['result'] >= game_result['stop_win']:
                break
        return game_result

    def _play_roll(self):
        if self.bet_type == 'Pass Line Bet':
            return pass_line_bet(self.bet_amount)
        elif self.bet_type == 'Don\'t Pass Bet':
            return dont_pass_bet(self.bet_amount)
        elif self.bet_type == 'Free Odds Bet':
            return free_odds_bet(self.bet_amount)
        else:
            raise Exception('Invalid Bet Type')
    