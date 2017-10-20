import curses
from random import *
from collections import defaultdict

'''
FiniteStateMachine:
    +--------restart--------- [Win] -----exit------+
    |                           ^                  |
    |                           |                  |
    |                          win                 |
    V                           |                  V
  [Init] <---init,restart---> [Game] ---exit---> [Exit]
    ^                           |                  ^
    |                        gameover              |
    |                           |                  |
    |                           V                  |
    +--------restart------- [Gameover] ---exit-----+
'''

letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actions_dict = dict(zip(letter_codes, actions * 2))

class GameField:
    def __init__(self,width=4,height=4,win=2048):
        self.width=width
        self.height=height
        self.win_score=win
        self.score=0
        self.heighest_score=0
        self.reset()
    
    def reset(self):
        if self.score > self.heighest_score:self.heighest_score=self.score 
        self.score=0
        self.field=[[0 for i in range(self.width)] for i in range(self.height)]
        self.spawn()
        self.spawn()
    
    @staticmethod
    def __invert(field):
        return [row[::-1]for row in field]

    @staticmethod
    def __transpose(field):
        return [list(row) for row in zip(*field)]

    def move(self,direction):
        def move_row_left(row):#only left direction
            def tighten(row):
                new_row=[i for i in row if i>=0]
                new_row+=[0 for i in range(len(row)-len(new_row))]
                return new_row
            def merge(row):
                pair=False
                new_row=[]
                for i in range(row):
                    if pair:
                        new_row.append(2*row[i])
                        self.score+=2*row[i]
                        pair=False
                    else:
                        if i+1<len(row) and row[i]==row[i+1]:
                            pair=True
                            new_row.append(0)
                        else:
                            pair=False
                            new_row.append(row[i])
                # assert len(new_row)==len(row)
                return new_row
            return tighten(merge(tighten(row)))
        moves={}
        moves['left']=lambda field:[move_row_left(row) for row in field]
        moves['right']=lambda field:GameField.__invert(moves['left'](GameField.__invert(field)))
        moves['up']=lambda field:GameField.__transpose(moves['left'](GameField.__transpose(field)))
        moves['down']=lambda field:GameField.__transpose(moves['right'](GameField.__transpose(field)))
        if direction in moves:
            if self.move_is_possible(direction):
                self.field=moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
    
    def spawn(self):
        new_element=4 if randrange(100)>89 else 2
        (i,j)=choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j]==0])
        self.field[i][j]=new_element
    
    def is_win(self):
        return any(any(i >= self.win_score for i in row) for row in self.field)
        # return any(x>=self.win_score for x in row for row in self.field)
    
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self,direction):
        def move_left_is_possible(row):
            def unit_left_is_possible(i):
                if row[i]==0 and row[i+1]!=0:
                    return True
                if row[i]!=0 and row[i]==row[i+1]:
                    return True
                return False
            return any(unit_left_is_possible(i) for i in range(len(row)-1))
        check={}#TODO:deep copy?
        check['Left']=lambda field:any(move_left_is_possible(row) for row in field)
        check['Right']=lambda field:any(check['Left'](GameField.__invert(field)))
        check['Up']=lambda field:any(check['Left'](GameField.__transpose(field)))
        check['Down']=lambda field:any(check['Right'](GameField.__transpose(field)))
        # print(direction)
        if direction in actions:
            return check[direction](self.field)
        else:
            return False

    def draw(self,screen):
        help_string1='(W)Up (S)Down (A)Left (D)Right'    
        help_string2='\t(R)Restart (Q)Exit'
        gameover_string = '\tGAME OVER'
        win_string = '\tYOU WIN!'
        def cast(string):
            screen.addstr(string+'\n')
        def draw_hor_separator():
            line='+'+('+--------'*self.width+'+')[1:]
            separator=defaultdict(lambda:line)#lamda:line is the default_factory
            if not hasattr(draw_hor_separator,"counter"):
                draw_hor_separator.counter=0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter+=1
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')
        screen.clear()
        cast('SCORE: '+str(self.score))
        if 0!=self.heighest_score:
            cast('HIGHSCORE: ' + str(self.highscore))
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

def main(stdscr):
    def init():
        #init state
        game_field.reset()
        return 'Game'
    
    def get_user_action(keyboard):
        char='N'
        while char not in actions_dict:
            char=keyboard.getch()
        return actions_dict[char]

    def not_game(state):
        game_field.draw(stdscr)
        action=get_user_action(stdscr)
        responses=defaultdict(lambda:state)
        responses['Restart'],responses['Exit']='Init','Exit'
        return responses[action]

    def game():
        game_field.draw(stdscr)
        action=get_user_action(stdscr)
        if action=='Restart':
            return 'Init'
        if action=='Exit':
            return 'Exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'
    
    state_actions={
        'Init':init,
        'Win':lambda:not_game('Win'),
        'Game_over':lambda:not_game('Gameover'),
        'Game':game
    }
    curses.use_default_colors()
    game_field=GameField(win=32)

    state='Init'
    while state!='Exit':
        state=state_actions[state]()

curses.wrapper(main)
