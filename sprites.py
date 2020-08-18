import pygame as pg
import random as r
import os
from settings import *

class bg(pg.sprite.Sprite):#drawn under the pieces. just a white line for now
    def __init__(self,game):
        self.image = pg.Surface((WIDTH,HEIGHT))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pg.draw.line(self.image,ALMOSTWHITE,[WIDTH-TILESIZE*1.75,0],[WIDTH-TILESIZE*1.75,HEIGHT],10)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

class piece(pg.sprite.Sprite):
    def __init__(self, game,x,y,type):
        self.sides = [] #list of 4 that describes what the sides are. 1-4 for operations, None for none, False for in side, 5 for the start piece
        self.holding = False
        self.shadow_height = SHADOWHEIGHT
        self.game = game
        self.quarter_pos = [[IMGSIZE/2,(IMGSIZE-TILESIZE)/2],[(IMGSIZE-TILESIZE)/2,0],[0,(IMGSIZE-TILESIZE)/2],[(IMGSIZE-TILESIZE)/2,IMGSIZE/2]]
        self.text_quarter_pos = [[IMGSIZE-OFFSET,IMGSIZE/2],[IMGSIZE/2,OFFSET],[OFFSET,IMGSIZE/2],[IMGSIZE/2,IMGSIZE-OFFSET]]
        self.in_quarter_pos = [[IMGSIZE-OFFSET2,IMGSIZE/2],[IMGSIZE/2,OFFSET2],[OFFSET2,IMGSIZE/2],[IMGSIZE/2,IMGSIZE-OFFSET2]]
        self.type = type #0 = normal, 1 = start, 2 = end
        self.connected_to = [] #OUTGOING connections. 4*5, 4's connected to is 5
        self.connected_from = None #INGOING connections. only necessary for final piece
        self.replaced_op = None #the operation type that is replaced by = when connected to end piece (so it is saved when removed from end piece)
        if self.type == 0:
            self.num = 1+r.randrange(9)
        elif self.type == 1:
            self.num = 'start'
        else:
            self.num = 10 + r.randrange(40)
        self.on_board = False
        'makes sides of the pieces based on type'
        if type == 0: #normal piece. rerolls sides until they're not all in or all out.
            found = False
            while not found:
                self.sides = [1+r.randrange(4)]
                for i in range(3):
                    if r.randrange(2) % 2 == 0:
                        self.sides.append(1+r.randrange(4))
                    else:
                        self.sides.append(False)
                found = self.check_sides()
        elif type == 1:
            self.sides = [5,None,None,None]
        elif type == 2:
            self.sides = [None,None,False,None]
        self.rectx = x
        self.recty = y
        self.make_image()

    def check_sides(self):
        for side in self.sides:
            if side == False:
                return True
        return False

    def make_image(self):
        'CALL TO REFRESH IMAGE. its a mess, ill decipher it later'
        self.image = pg.Surface((IMGSIZE+self.shadow_height,IMGSIZE+self.shadow_height))
        self.image.set_colorkey(BLACK)
        if self.type == 0:
            in_img = self.game.in_img
            out_img = self.game.out_img
            for i in range(4):
                if self.sides[i] == False:
                    self.image.blit(in_img,self.quarter_pos[i])
                else:
                    self.image.blit(out_img,self.quarter_pos[i])
                    if self.sides[i] == 1:
                        self.draw_text(self.image,'+',self.text_quarter_pos[i][0],self.text_quarter_pos[i][1],ALMOSTWHITE,40)
                    elif self.sides[i] == 2:
                        self.draw_text(self.image,'/',self.text_quarter_pos[i][0],self.text_quarter_pos[i][1],ALMOSTWHITE,20)
                    elif self.sides[i] == 3:
                        self.draw_text(self.image,'-',self.text_quarter_pos[i][0],self.text_quarter_pos[i][1],ALMOSTWHITE,40)
                    elif self.sides[i] == 4:
                        self.draw_text(self.image,'*',self.text_quarter_pos[i][0],self.text_quarter_pos[i][1]+10,ALMOSTWHITE,40)
                    elif self.sides[i] == 6:
                        self.draw_text(self.image,'=',self.text_quarter_pos[i][0],self.text_quarter_pos[i][1],ALMOSTWHITE,40)
                in_img = pg.transform.rotate(in_img,90)
                out_img = pg.transform.rotate(out_img,90)
            self.draw_text(self.image,str(self.num),IMGSIZE/2,IMGSIZE/2,ALMOSTWHITE,60)
        else:
            none_img = self.game.none_img
            if self.type == 1:
                out_img = self.game.out_img
                for i in range(4):
                    if self.sides[i] == 5:
                        self.image.blit(out_img,self.quarter_pos[i])
                    else:
                        self.image.blit(none_img,self.quarter_pos[i])
                    none_img = pg.transform.rotate(none_img,90)
                    out_img = pg.transform.rotate(out_img,90)
            elif self.type == 2:
                in_img = self.game.in_img
                for i in range(4):
                    if self.sides[i] == False:
                        self.image.blit(in_img,self.quarter_pos[i])
                    else:
                        self.image.blit(none_img,self.quarter_pos[i])
                    none_img = pg.transform.rotate(none_img,90)
                    in_img = pg.transform.rotate(in_img,90)
                self.draw_text(self.image,str(self.num),IMGSIZE/2,IMGSIZE/2+30,ALMOSTWHITE,60)
        self.get_outline(VERYDARKGRAY)
        self.mask = pg.mask.from_surface(self.image)
        if self.holding:
            self.draw_shadow()
        self.rect = self.image.get_rect()
        self.rect.x = self.rectx
        self.rect.y = self.recty
        if self.type == 1:
            self.draw_text(self.image,'START',IMGSIZE/2,IMGSIZE/2,ALMOSTWHITE,40)
        elif self.type == 2:
            self.draw_text(self.image,'END',IMGSIZE/2,IMGSIZE/2-10,ALMOSTWHITE,30)
        self.draw_text(self.image,str(self.connected_to),IMGSIZE/2,IMGSIZE/2+20,ALMOSTWHITE,20)
        if self.rect.x < WIDTH-TILESIZE*2.5:
            self.on_board = True
        else:
            self.on_board = False

    def rotate(self,dir):
        #rotates by changign index of sides
        if dir == 'q':
            self.sides = self.sides[-1:]+self.sides[:-1]
        if dir == 'e':
            self.sides = self.sides[1:]+self.sides[:1]
        self.make_image()

    def draw_shadow(self):
        #black magic. not sure how it works
        self.mask.invert()
        to_surface = self.mask.to_surface()
        to_surface.set_colorkey((255,255,255))
        to_surface.fill(VERYDARKGRAY, special_flags=pg.BLEND_ADD)
        to_surface.scroll(int(self.shadow_height/2),int(self.shadow_height/2))
        to_surface.blit(self.image,[0,0])
        self.image = to_surface.copy()
        self.image.set_colorkey(BLACK)

    def draw_text(self,surface,text,x,y,color,size):
        my_file = os.path.join(self.game.game_folder, 'calibri.ttf')
        font = pg.font.Font(my_file,size)
        text_surface = font.render(text,True,color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        surface.blit(text_surface,text_rect)

    def check_click(self,mouse_pos,click_dir):
        if self.rect.collidepoint(mouse_pos):
            if self.type == 2 and self.connected_from != None:#if end piece, put replaced operation back
                for i in range(4):
                    if self.connected_from.sides[i] == 6:
                        self.connected_from.sides[i] = self.connected_from.replaced_op
            #mask collision
            pos_in_mask = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y
            if self.mask.get_at(pos_in_mask) == 1:#if picked up, remove all connections
                self.holding = True
                self.connected_to = []
                self.connected_from = None
                self.make_image()
                return True

    def get_outline(self,color=(0,0,0)):
        rect = self.image.get_rect()
        mask = pg.mask.from_surface(self.image)
        outline = mask.outline()
        outline_image = pg.Surface(rect.size).convert_alpha()
        outline_image.fill((0,0,0,0))
        for point in outline:
            outline_image.set_at(point,color)

        merged = self.image.copy()
        merged.blit(outline_image, (0, 0))
        self.image = merged

    def find_connection(self,pieces):
        #when piece is put down, looks around for pieces to connect to
        min_dist = MIN_DIST #min distance for snapping
        other_piece = None
        other_side = None
        in_side = None
        for i in range(4): #checks each side
            if self.sides[i] == False:#in side
                in_point = [self.in_quarter_pos[i][0]+self.rect.x,self.in_quarter_pos[i][1]+self.rect.y]
                for piece in pieces:#looks through all pieces for a piece that is rotated the right way, the opposite operation, and close enough
                    if piece.rect.center != self.rect.center and piece.on_board:
                        for j in range(4):
                            if piece.sides[j] != None and piece.sides[j] != False:#if side is an operation
                                if (i-j)%2==0:
                                    out_point = [piece.text_quarter_pos[j][0]+piece.rect.x,piece.text_quarter_pos[j][1]+piece.rect.y]
                                    dist = ((in_point[0]-out_point[0])**2+(in_point[1]-out_point[1])**2)**.5
                                    if dist < min_dist:
                                        other_piece = piece
                                        other_side = j
                                        in_side = i
            elif self.sides[i] != None:#out side
                if self.sides[i] != False and self.sides[i] != None:
                    in_point = [self.text_quarter_pos[i][0]+self.rect.x,self.text_quarter_pos[i][1]+self.rect.y]
                    for piece in pieces:
                        if piece.rect.center != self.rect.center and piece.on_board:
                            for j in range(4):
                                if piece.sides[j] == False:#if other piece's side is an in
                                    if (i-j)%2==0:
                                        out_point = [piece.in_quarter_pos[j][0]+piece.rect.x,piece.in_quarter_pos[j][1]+piece.rect.y]
                                        dist = ((in_point[0]-out_point[0])**2+(in_point[1]-out_point[1])**2)**.5
                                        if dist < min_dist:
                                            other_piece = piece
                                            other_side = j
                                            in_side = i
        if other_piece != None:#if found another piece, snap it based on the side
            self.snap(other_piece,in_side)
            return [other_piece.type,other_side,in_side]
        else:
            return None

    def snap(self,target,own_side):#snaps based on which side the connection is
        anchor_point = target.rect.center
        if own_side == 0:
            self.rect.center = [anchor_point[0]-TILESIZE,anchor_point[1]]
            target_side = 2
        elif own_side == 1:
            self.rect.center = [anchor_point[0],anchor_point[1]+TILESIZE]
            target_side = 3
        elif own_side == 2:
            self.rect.center = [anchor_point[0]+TILESIZE,anchor_point[1]]
            target_side = 0
        else:
            self.rect.center = [anchor_point[0],anchor_point[1]-TILESIZE]
            target_side = 1
        if not self.exists(target): #only adds to connected_to if it doesnt exist already
            target.connected_to.append([self,target.sides[target_side]])
        if self.type == 2:#if connecting to end node
            target.replaced_op = target.sides[target_side]
            target.sides[target_side] = 6
            self.connected_from = target
        self.rectx = self.rect.x#set new positions
        self.recty = self.rect.y

    def exists(self,target):
        for connection in target.connected_to:
            if connection[0]==self:
                return True
        return False

    def __str__(self):
        return str(self.num)
    def __repr__(self):
        return str(self.num)

    def reroll(self):
        self.num = 1+r.randrange(9)
        found = False
        while not found:
            self.sides = [1+r.randrange(4)]
            for i in range(3):
                if r.randrange(2) % 2 == 0:
                    self.sides.append(1+r.randrange(4))
                else:
                    self.sides.append(False)
            found = self.check_sides()
        self.make_image()

    def update(self):
        for connection in self.connected_to:#if one of connected pieces is pieced up, remove it from connected_to
            if connection[0].holding:
                self.connected_to.pop(self.connected_to.index(connection))
        if self.rect.x < WIDTH-TILESIZE*2.5:
            self.on_board = True
        else:
            self.on_board = False
        if self.holding:
            self.rect.center = self.game.mouse_pos#if being held, keep the image on the mouse
            self.rectx = self.rect.x
            self.recty = self.rect.y
