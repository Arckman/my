from curses import *
from random import *

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
        self.heighest_score=self.score if self.score>self.heighest_score
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
        self[i][j]=new_element
    
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
        check['left']=lambda field:any(move_left_is_possible(row) for row in field)
        check['right']=lambda field:any(check['left'](GameField.__invert(field)))
        check['up']=lambda field:any(check['left'](GameField.__transpose(field)))
        check['down']=lambda field:any(check['right'](GameField.__transpose(field)))
        if direction in actions:
            return check[direction](self.field)
        else:
            return False
    


            

def main():
    def init():
        #init state
        game_field.