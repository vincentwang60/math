import pygame as pg
import sys
import random as r
import os
from os import path
from settings import *
from sprites import *
import time

class Game:
    def __init__(self):
        pg.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0) #full screen
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.load_data()
        self.connection_info = '' #connections of the held piece: held.find_connection()
        self.all_sprites = pg.sprite.Group()
        self.bg = bg(self) #only draws the white line for now :/
        self.pieces = [] #list of pieces
        self.num_output = 0 #the result of the equations
        self.won = False
        self.time_taken = 0
        #creates pieces
        for i in range(10):
            self.pieces.append(piece(self,WIDTH-IMGSIZE-SHADOWHEIGHT/2,i*(IMGSIZE+5),0))
        self.start = piece(self,100,100,1)
        self.end = piece(self,100,500,2)
        self.pieces.append(self.start)
        self.pieces.append(self.end)
        self.start_time = time.time()

    def load_data(self):
        self.game_folder = path.dirname(__file__)
        img_folder = path.join(self.game_folder,"resource")
        self.in_img = pg.image.load(path.join(img_folder,"in.png")).convert_alpha()
        self.out_img = pg.image.load(path.join(img_folder,"out.png")).convert_alpha()
        self.none_img = pg.image.load(path.join(img_folder,"none.png")).convert_alpha()

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.mouse_pos = pg.mouse.get_pos()
        #find held piece
        held = None
        for piece in self.pieces:
            if piece.holding:
                held = piece
            piece.update()
        if held != None: #moves held pieces to top of the layers, so it doesnt show up under another piece
            self.pieces.append(self.pieces.pop(self.pieces.index(held)))
        #calculates num output by following the operations from start
        self.num_output = None
        if len(self.start.connected_to)>0:
            self.num_output = self.start.connected_to[0][0].num
            connected = True #tracks whether current piece has a piece after it
            current_piece = self.start
            while connected:
                if current_piece.connected_to[0][0].type != 2:#if not connected to end piece
                    if current_piece.connected_to[0][1] == 1:
                        self.num_output += current_piece.connected_to[0][0].num
                    elif current_piece.connected_to[0][1] == 2:
                        self.num_output = int(self.num_output/current_piece.connected_to[0][0].num)
                    elif current_piece.connected_to[0][1] == 3:
                        self.num_output -= current_piece.connected_to[0][0].num
                    elif current_piece.connected_to[0][1]==4:
                        self.num_output = self.num_output*current_piece.connected_to[0][0].num
                    current_piece = current_piece.connected_to[0][0]
                    if len(current_piece.connected_to)==0:
                        connected = False
                else:#if connected to end piece, end chain
                    connected = False
        #checks if game is over
        if self.num_output == self.end.num and self.end.connected_from != None:
            self.won = True
        if not self.won:
            self.current_time = time.time()
            self.time_taken = int(self.current_time-self.start_time)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.screen.blit(self.bg.image,[0,0])
        for piece in self.pieces:
            self.screen.blit(piece.image,[piece.rect.x,piece.rect.y])
        self.draw_text(self.screen,str(self.num_output)+', '+str(self.won),200,100,VERYDARKGRAY,30)
        self.draw_text(self.screen,str(self.time_taken),200,200,VERYDARKGRAY,30)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_q:
                    for piece in self.pieces:
                        if piece.holding:
                            piece.rotate('q')
                if event.key == pg.K_e:
                    for piece in self.pieces:
                        if piece.holding:
                            piece.rotate('e')
                if event.key == pg.K_SPACE:#rest
                    for piece in self.pieces:
                        piece.make_image()
                if event.key == pg.K_r:
                    for piece in self.pieces:
                        if piece.holding:
                            self.time_taken += 10
                            piece.reroll()
            if event.type == pg.MOUSEBUTTONDOWN:
                #checks if user clicks on a piece. stops when top piece is found
                found = False
                pieces = self.pieces.copy()
                pieces.reverse()#reverses order of pieces so that the first item in the list is on the top
                for piece in pieces:
                    if not found:
                        if piece.check_click(pg.mouse.get_pos(),True):
                            found = True
            if event.type == pg.MOUSEBUTTONUP:
                #when user drops piece, tries to connect it
                for piece in self.pieces:
                    if piece.holding:
                        held = piece
                        self.connection_info = held.find_connection(self.pieces)
                for piece in self.pieces:
                    piece.holding = False
                    piece.make_image()

    def draw_text(self,surface,text,x,y,color,size):
        my_file = os.path.join(self.game_folder, 'calibri.ttf')
        font = pg.font.Font(my_file,size)
        text_surface = font.render(text,True,color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        surface.blit(text_surface,text_rect)
# create the game object
g = Game()
while True:
    g.new()
    g.run()
