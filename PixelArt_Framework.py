#from time import perf_counter, perf_counter_ns
import framework
from colors import *
from framework import resizeSurface,function,get_screen_size,Dropdown
from pygame.draw import rect as draw_rect
from pygame.draw import line
from pygame import Surface,Rect
from PIL import Image as PIL_Image
class Canvas:
    @classmethod
    def accepts(cls) -> tuple[str]:
        return ('mpos','mb1down','mb1up','mb1','mb2','wheel')
    def __init__(self,pos:tuple,grid_size:tuple,name:str) -> None:
        self.name:str = name
        self.grid_size:tuple = grid_size
        self.grids:list[Grid] = [Grid(grid_size),]
        self.screen_size:int = 1
        self._offSetPos:tuple = (0,0)
        self.pos:tuple = pos
        self._rect:Rect = Rect(pos[0],pos[1],grid_size[0],grid_size[1]) 
        self.grided:bool = True
        self.pmpos:tuple = (0,0)
        self.default_color:tuple = (0,0,0)
        self.tools:list[str] = ['pen','erase','bucket','line','pan']
        self.tool:int = 0
        self.active_grid:int = 0
        self.current_grid:Grid = self.grids[self.active_grid]
        self.current_color:tuple = None
        self.surfaces = [Surface(self.grid_size),]
        self.current_surface:Surface = self.surfaces[self.active_grid]
        self.pixel_rect:Rect = Rect(0,0,1,1)
        self.true_pos:tuple = (self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1])
        self.px,self.py = (0,0)
        self.mpos:tuple = self._pos
        self.screen_surf:Surface = self.current_surface.copy()
        self.update_mask()
        self.PIXEL_RECT:Rect = Rect(0,0,1,1)
        self.MAX_ZOOM_SIZE:int = get_screen_size()[1]*5//max(grid_size) # '5' is how many times the biggest size can go beyond the screen_size[1] if you have performance issues (when zoomed in) then turn 5 down to 3
        self.start_pos:bool|None = None
        self.saved = False
        self.preview_obj = None

    def flatten_info(self) -> list:
        #self._store_screen_surf()
        a_plan_of_plans = [[grid.grid for grid in self.grids],self.active_grid,self.tool,list(self.grid_size)]
        return a_plan_of_plans

    def _set_preview_thingy(self,preview) -> None:
        preview:Previews
        self.preview_obj = preview

    def load(self,grids,active_grid,tool,grid_size) -> None:
        offset = self._offSetPos
        self.__init__(self._pos,grid_size,self.name)
        self.offSetPos = offset
        self.grids = []
        for grid in grids:
            boschlow = Grid(grid_size)
            boschlow.grid = grid
            self.grids.append(boschlow)
        self.active_grid = active_grid
        self.tool = tool
        self.grid_size = grid_size
        self.surfaces = [Surface(grid_size) for _i in range(len(grids))]
        for grid_count,surf in enumerate(self.surfaces):
            for y,color_row in enumerate(self.grids[grid_count].grid):
                for x,color_cell in enumerate(color_row):
                    draw_rect(surf,color_cell[0],(x,y,1,1))
        self._rect = Rect(self._pos[0],self._pos[1],grid_size[0],grid_size[1]) 
        self.current_grid = self.grids[self.active_grid]
        self.current_surface:Surface = self.surfaces[self.active_grid]
        self.screen_surf:Surface = self.current_surface.copy()
        self.saved = True
        

    def _store_screen_surf(self):
        '''Shrinks screen surf and stores it back in the self.surfaces list'''
        self.surfaces[self.active_grid] = resizeSurface(self.screen_surf,self.grid_size)

    def _call_up_grid(self,val):
        '''Brings up a grid from self.surfaces list and resizes to fit the screen_surf'''
        self.screen_surf = resizeSurface(self.surfaces[val],(self.grid_size[0]*self.screen_size,self.grid_size[1]*self.screen_size))

    def get_all_previews(self,size) -> list:
        return [resizeSurface(surf,(size,size)) for surf in self.surfaces]
    
    def move_active_frame_up(self):
        self._store_screen_surf()
        moveItemInListUpByIndex(self.grids,self.active_grid)
        moveItemInListUpByIndex(self.surfaces,self.active_grid)
        self.active_grid -= 1
        self._call_up_grid(self.active_grid)
        self.current_grid = self.grids[self.active_grid]

    def move_active_frame_down(self):
        self._store_screen_surf()
        moveItemInListDownByIndex(self.grids,self.active_grid)
        moveItemInListDownByIndex(self.surfaces,self.active_grid)
        self.active_grid += 1
        self._call_up_grid(self.active_grid)
        self.current_grid = self.grids[self.active_grid]

    def make_active_frame_copy(self):
        self.grids.append(Grid(self.grid_size))
        self.surfaces.append(self.surfaces[self.active_grid].copy())
        self.grids[-1].grid = [[cell[:] for cell in row] for row in self.grids[self.active_grid].grid]


    def delete_active_grid(self):
        del self.grids[self.active_grid]
        del self.surfaces[self.active_grid]
        if self.active_grid == len(self.grids):
            self.active_grid -= 1
        assert len(self.grids) > 0, 'deleted all frames bruh, should not happen'
        self._call_up_grid(self.active_grid)
        self.current_grid = self.grids[self.active_grid]


    def switch_grid(self,grid_num:int):
        assert isinstance(grid_num,int), "we're all doomed"
        assert 0<=grid_num<len(self.grids), 'trying to access a grid that doesnt exist'
        self._store_screen_surf()
        self._call_up_grid(grid_num)
        self.active_grid = grid_num
        self.current_grid = self.grids[grid_num]

    def toggle_grided(self) -> None:
        self.grided = not self.grided

    def set_current_tool(self,tool) -> None:
        if isinstance(tool,int):
            self.tool = tool
        elif isinstance(tool,str):
            self.tool = self.tools.index(tool)
        else:
            raise TypeError('Cannot set',tool,'as a tool')
    
    def set_current_color(self,color):
        self.current_color = color
    
    def update_mask(self):
        surf_width  = self.screen_surf.get_width()
        surf_height = self.screen_surf.get_height()
        self.grid_surf:Surface = Surface((self.grid_size[0]*self.screen_size,self.grid_size[1]*self.screen_size)).convert_alpha()
        self.grid_surf.fill((0,0,0,0))
        for count in range(self.grid_size[1]): #horizontal lines
            line(self.grid_surf,(0,0,0,255),(0,count*self.screen_size),(surf_width,count*self.screen_size),self.screen_size//15)
        for count in range(self.grid_size[0]): #vertical lines
            line(self.grid_surf,(0,0,0,255),(count*self.screen_size,0),(count*self.screen_size,surf_height),self.screen_size//15)
    @property
    def offSetPos(self):
        raise SyntaxError('Use instead, <Canvas>._offSetPos')

    @property
    def pos(self):
        raise SyntaxError('Use instead, <Canvas>._pos')

    @pos.setter
    def pos(self,newVal):
        self._pos = newVal
        self._rect = Rect(self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1],self.grid_size[0]*self.screen_size,self.grid_size[1]*self.screen_size)
        self.true_pos = (self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1])

    @offSetPos.setter
    def offSetPos(self, newVal):
        self._offSetPos = (newVal)
        self._rect = Rect(self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1],self.grid_size[0],self.grid_size[1])
        self.true_pos = (self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1])

    def pen_draw_pixel(self,x,y,color) -> None:
        for x1,y1 in line_list((self.px,self.py),(x,y)):
            self.current_grid.set_color(x1,y1,color)
            draw_rect(self.screen_surf,self.current_color,self.pixel_rect.move(x1*self.screen_size,y1*self.screen_size))
        self.px = x
        self.py = y

    def enlarge_canvas(self,newSize) -> None:
        #newSize will be a relative to the original size of the canvas
        prev_surf_size = self.screen_surf.get_size()
        previous_mousex_percent = (self.mpos[0]-self._pos[0]-self._offSetPos[0])/prev_surf_size[0]
        previous_mousey_percent = (self.mpos[1]-self._pos[1]-self._offSetPos[1])/prev_surf_size[1]
        diff_x = self.grid_size[0]*newSize-prev_surf_size[0]
        diff_y = self.grid_size[1]*newSize-prev_surf_size[1]
        self.pos = (self._pos[0]-diff_x*previous_mousex_percent,self._pos[1]-diff_y*previous_mousey_percent)
        self.screen_surf = resizeSurface(self.screen_surf,(self.grid_size[0]*newSize,self.grid_size[1]*newSize))
        self._rect = Rect(self._pos[0]+self._offSetPos[0],self._pos[1]+self._offSetPos[1],self.grid_size[0]*newSize,self.grid_size[1]*newSize)
        self.pixel_rect = Rect(0,0,self.screen_surf.get_width()//self.grid_size[0],self.screen_surf.get_height()//self.grid_size[1])
        if self.grided: self.update_mask()


    def preview_active_surf(self) -> Surface:
        return resizeSurface(self.current_surface,())
    
    def erase_pixels(self,x,y):
        for x1,y1 in line_list((self.px,self.py),(x,y)):
            self.current_grid.clear_cell(x1,y1)
            draw_rect(self.screen_surf,(0,0,0),self.pixel_rect.move(x1*self.screen_size,y1*self.screen_size))
        self.px = x
        self.py = y

    def create_new_grid(self) -> None:
        self.grids.append(Grid(self.grid_size,self.default_color))
        self.surfaces.append(Surface(self.grid_size))

    def flood_iterative_exact(self,starting_pos,color) -> None:
        for x,y in self.current_grid.flood_exact_list(starting_pos,color):
            draw_rect(self.screen_surf,color,self.pixel_rect.move(x*self.screen_size,y*self.screen_size))
    
    def update(self,things):
        '''mpos,mb1down,mb1up,mb1,mb2,wheel'''
        mpos,mb1down,mb1up,mb1,mb2,wheel= things
        self.mpos = mpos   
        if self._rect.collidepoint(mpos) or self._rect.collidepoint(self.pmpos):
            if wheel:
                self.screen_size -= wheel
                if self.screen_size < 1:
                    self.screen_size = 1
                elif self.screen_size > self.MAX_ZOOM_SIZE:
                    self.screen_size = self.MAX_ZOOM_SIZE
                    self.pmpos = mpos
                    return
                self.enlarge_canvas(self.screen_size)
            elif mb2 or (self.tool == self.tools.index('pan') and mb1):
                self.pos = (self._pos[0]+self.mpos[0]-self.pmpos[0],self._pos[1]+self.mpos[1]-self.pmpos[1])
            elif self.tool == self.tools.index('pen') and mb1 and self.current_color:
                x,y = int((self.mpos[0]-self._pos[0]-self._offSetPos[0])//self.screen_size),int((self.mpos[1]-self._pos[1]-self._offSetPos[1])//self.screen_size)
                if mb1down:
                    self.px,self.py = x,y           
                    self.saved = False         
                self.pen_draw_pixel(x,y,self.current_color)
            elif self.tool == self.tools.index('bucket') and mb1down and self.current_color:
                for x,y in self.current_grid.flood_exact_list((int((self.mpos[0]-self._pos[0]-self._offSetPos[0])//self.screen_size),int((self.mpos[1]-self._pos[1]-self._offSetPos[1])//self.screen_size)),self.current_color):
                    draw_rect(self.screen_surf,self.current_color,self.pixel_rect.move(x*self.screen_size,y*self.screen_size))
                self.saved = False         

            elif self.tool == self.tools.index('line') and self.current_color:
                x,y = int((self.mpos[0]-self._pos[0]-self._offSetPos[0])//self.screen_size),int((self.mpos[1]-self._pos[1]-self._offSetPos[1])//self.screen_size)
                if mb1down:
                    self.start_pos = (x,y)
                elif mb1up and self.start_pos:
                    end_pos = (x,y)
                    self.current_grid.line(self.start_pos,end_pos,self.current_color)
                    for x,y in line_list(self.start_pos,end_pos):
                        self.current_grid.set_color(x,y,self.current_color)
                        draw_rect(self.screen_surf,self.current_color,self.pixel_rect.move(x*self.screen_size,y*self.screen_size)) 
                    self.start_pos = None
                    self.saved = False         
            elif self.tool == self.tools.index('erase') and mb1:
                x,y = int((self.mpos[0]-self._pos[0]-self._offSetPos[0])//self.screen_size),int((self.mpos[1]-self._pos[1]-self._offSetPos[1])//self.screen_size)
                if mb1down:
                    self.px,self.py = x,y                    
                self.erase_pixels(x,y)
                self.saved = False         
        if mb1up:
            self.preview_obj:Previews
            self.preview_obj._update_prev(self.active_grid,resizeSurface(self.screen_surf,(80,80)))
        self.pmpos = self.mpos

    def draw(self) -> None:
        framework.screen.blit(self.screen_surf,self.true_pos)
        if self.grided:framework.screen.blit(self.grid_surf,self.true_pos)
    
def moveItemInListUpByIndex(_list:list,index:int):
    '''move more towards the beginning of list'''
    indexAbove = index-1 if index > 0 else 0
    _list.insert(indexAbove,_list.pop(index))

def moveItemInListDownByIndex(_list:list,index:int):
    '''move more towards the end of list'''
    indexAbove = index+1 if index < len(_list)-1 else len(_list)-1
    _list.insert(indexAbove,_list.pop(index))

class Previews:
    @classmethod
    def accepts(cls) -> tuple:
        return ('mpos','mb1down','mb1up','wheel')
    def __init__(self,pos,size,canvas:Canvas):
        self.canvas = canvas
        self.canvas._set_preview_thingy(self)
        self.pos = pos
        self.size = size
        self.prevs = canvas.get_all_previews(size = 80)
        self.dropdown = Dropdown(pos,(size[0],100),light_dark_grey,light_dark_grey,None,lambda:self.prevs,self.select,size[1],None,(10,10))
        #TODO: optimize self.prevs so that add_frame,delete_frame,move_up,and move_down dont have to reload all frames every time
    
    def add_frame(self):
        self.canvas.create_new_grid()
        self.prevs = self.canvas.get_all_previews(size = 80)
        self.dropdown.recalculate_options()
    
    def delete_frame(self):
        if len(self.canvas.grids) != 1:
            del self.prevs[self.canvas.active_grid]
            self.canvas.delete_active_grid()
            self.prevs = self.canvas.get_all_previews(size = 80)
            self.dropdown.recalculate_options()
    
    def move_up(self):
        if self.canvas.active_grid != 0:
            self.canvas.move_active_frame_up()
            self.prevs = self.canvas.get_all_previews(size = 80)
            self.dropdown.recalculate_options()

    def move_down(self):
        if self.canvas.active_grid != len(self.canvas.grids)-1:
            self.canvas.move_active_frame_down()
            self.prevs = self.canvas.get_all_previews(size = 80)
            self.dropdown.recalculate_options()

    def copy(self):
        self.prevs.append(self.prevs[self.canvas.active_grid].copy())
        self.canvas.make_active_frame_copy()
        self.dropdown.recalculate_options()

    def _update_prev(self,prev_num,new_prev):
        self.prevs[prev_num] = new_prev
        self.dropdown.recalculate_options()

    def select(self,num):
        self.canvas.switch_grid(num)

    @property 
    def offSetPos(self) -> tuple:
        raise SyntaxError('Use instead <Previews>._offSetPos')
    
    @offSetPos.setter
    def offSetPos(self,newVal):
        self._offSetPos = newVal
        self.dropdown.offSetPos = newVal
    
    def update(self,things):
        mpos,mb1down,mb1up,wheel = things
        self.dropdown.update((mpos,mb1down,mb1up,wheel,0))


    def draw(self) -> None:
        self.dropdown.draw()


def line_list(starting_point,ending_point) -> list|tuple:
    if starting_point[0] > ending_point[0]:
        starting_point,ending_point = ending_point,starting_point
    elif starting_point == ending_point:
        return (starting_point,)
    return_list = []
    append = return_list.append
    x1,y1 = starting_point
    x2,y2 = ending_point
    if x1 != x2: # if not a vertical line
        slope = (y2-y1)/(x2-x1)
        if 0<=slope<=1:
            count = 0
            err = 0
            y = 0
            while count <= ending_point[0]-starting_point[0]:
                append((count+x1,y+y1))
                err += slope 
                if err > 0.5:
                    y += 1
                    err -= 1
                count += 1
        elif 1<slope:
            slope = 1/slope
            count = 0
            err = 0
            x = 0
            while count <= ending_point[1]-starting_point[1]:
                append((x+x1,count+y1))
                err += slope
                if err > 0.5:
                    x += 1
                    err -= 1
                count += 1
        elif -1<=slope<=0:
            count = 0
            err = 0
            y = 0
            while count <= ending_point[0]-starting_point[0]:
                append((count+x1,y+y1))
                err += slope
                if err < -0.5:
                    y -= 1
                    err += 1
                count += 1
        elif slope<-1:
            slope = 1/slope
            count = 0
            err = 0
            x = 0
            while count <= starting_point[1]-ending_point[1]:
                append((x+x2,count+y2))
                err += slope
                if err < -0.5:
                    x -= 1
                    err += 1
                count += 1
    else:
        if starting_point[1] > ending_point[1]:
            starting_point,ending_point = ending_point,starting_point
        for y in range(ending_point[1]-starting_point[1]):
            append((x1,y+starting_point[1]))
        append(ending_point)
    return return_list

def is_similar(color1:tuple,color2:tuple,tolerance:int) -> bool:
    (r1,g1,b1) = color1
    (r2,g2,b2) = color2
    if  -tolerance < (r1-r2) < tolerance and -tolerance < (g1-g2) < tolerance and -tolerance < (b1-b2) < tolerance:
        return True
    else:
        return False
def adj(x:int,y:int,width:int,height:int) -> list[tuple[int]]:
    return_list:list[tuple[int]] = []
    if x-1 >= 0:
        return_list.append((x-1,y))
    if x+1 < width:
        return_list.append((x+1,y))
    if y-1 >= 0:
        return_list.append((x,y-1))
    if y+1 < height:
        return_list.append((x,y+1))
    return return_list
def fast_list_maker(len):
    return [None]*len   

def save_as_GIF(grid_list:list[Surface],name:str, path:str = framework.PATH,imageDuration:int = 100,pixelSize:int = 1) -> None:
    imgs = []
    picture_size = (len(grid_list[0][0]),len(grid_list[0]))
    for image in grid_list:
        PNGPixelList:list = []
        for pixelRow in image:
            for _1 in range(pixelSize):
                for pixel in pixelRow:
                    for _2 in range(pixelSize):
                        if pixel[1] != 0:
                            PNGPixelList.append((pixel[0][0],pixel[0][1],pixel[0][2],255))
                        elif pixel[1] == 0:
                            PNGPixelList.append((0,0,0,0))
        img = PIL_Image.new('RGBA',(picture_size[0]*pixelSize,picture_size[1]*pixelSize))
        img.putdata(PNGPixelList)  
        imgs.append(img)  
    first_image:PIL_Image = imgs[0]
    first_image.save(path+'/Exports/'+name+'.gif',
    save_all = True, append_images = imgs[1:], 
    optimize = False, duration = imageDuration,loop = 0)

class Palette:
    @classmethod
    def accepts(cls) -> tuple[str]:
        return ('mpos','mb1down','mb3down')
    color_rect_size = 30

    def __init__(self,pos,size,set_color_func:function = lambda x:x):
        self.active_color_frame:Surface = Surface((self.color_rect_size,self.color_rect_size)).convert_alpha()
        self.active_color_frame.fill((0,0,0,0))
        draw_rect(self.active_color_frame,(255,255,255,255),Rect(0,0,self.color_rect_size,self.color_rect_size),3)
        self.colors:list = []
        self.pos:tuple = pos
        self.selected_color:tuple = None
        self.rects = []
        self._rect = Rect(pos[0],pos[1],size[0],size[1])
        self.max_per_line = size[0]//self.color_rect_size
        self._offSetPos = (0,0)
        self.max = size[1]//self.color_rect_size * self.max_per_line
        self.func = set_color_func
        self.active_color_pos = (-100,-100)
        self.selected_color_index = None

    def get_info(self):
        return (self.colors[:],self.selected_color_index)
    
    def load(self,colors:list,selected_color_index:tuple):
        for color in colors:
            self.add_color(color)
        if selected_color_index == None:
            self.selected_color_index = selected_color_index
            self.selected_color = selected_color_index
        else:
            self.selected_color_index = selected_color_index
            self.selected_color = self.colors[selected_color_index]
            self.active_color_pos = (self.selected_color_index % self.max_per_line * self.color_rect_size + self._offSetPos[0] + self.pos[0], self.selected_color_index//self.max_per_line * self.color_rect_size+ self._offSetPos[1] + self.pos[1])

    @property
    def offSetPos(self) -> tuple[int,int]:
        raise SyntaxError('Use instead <Palette>._offSetPos')
    
    @offSetPos.setter
    def offSetPos(self,newVal) -> None:
        dif_x,dif_y = newVal[0]-self._offSetPos[0],newVal[1]-self._offSetPos[1]
        self._offSetPos = newVal
        self._rect.move_ip(dif_x,dif_y)
        for rect in self.rects:
            rect:Rect
            rect.move_ip(dif_x,dif_y)
        self.active_color_pos = (self.active_color_pos[0]+dif_x,self.active_color_pos[1]+dif_y)

    def update(self,things) -> None:
        mpos,mb1down,mb3down = things
        if self._rect.collidepoint(mpos):
            if mb1down:
                y = (mpos[1]-self.pos[1]-self._offSetPos[1])//self.color_rect_size
                x = (mpos[0]-self.pos[0]-self._offSetPos[0])//self.color_rect_size
                index = y * self.max_per_line + x
                if index >= len(self.colors): pass
                else: # within bounds
                    self.selected_color_index = index
                    self.selected_color = self.colors[index]
                    self.active_color_pos = (x*self.color_rect_size+self.pos[0]+self._offSetPos[0],y*self.color_rect_size+self.pos[1]+self._offSetPos[1])
                    self.func(self.selected_color)
            if mb3down:
                if not self.colors: return
                y = (mpos[1]-self.pos[1]-self._offSetPos[1])//self.color_rect_size
                x = (mpos[0]-self.pos[0]-self._offSetPos[0])//self.color_rect_size
                index = y * self.max_per_line + x
                if index >= len(self.colors): pass
                else: # within bounds
                    self.colors.pop(index)
                    print(index)
                    if self.selected_color_index > len(self.colors)-1:
                        self.selected_color_index = len(self.colors)-1
                        self.active_color_pos = (self.selected_color_index%self.max_per_line*self.color_rect_size+self.pos[0]+self._offSetPos[0],self.selected_color_index//self.max_per_line*self.color_rect_size+self.pos[1]+self._offSetPos[1])
                    if self.selected_color_index == -1 or self.selected_color_index == None:
                        self.selected_color = None
                        self.selected_color_index = None
                    try:
                        self.selected_color = self.colors[self.selected_color_index]
                        self.func(self.selected_color)
                    except:
                        self.selected_color = None
                        self.func(None)

    def draw(self) -> None:
        draw_rect(framework.screen,(30,30,40),self._rect)
        for color,rect in zip(self.colors,self.rects):
            draw_rect(framework.screen,color,rect)
        if self.selected_color: framework.screen.blit(self.active_color_frame,self.active_color_pos)

    def add_color(self,color:tuple):
        if color == None: raise TypeError('Cannot add color "None" to Palette')
        elif isinstance(color,(int,float,str,bytes,bool)): raise TypeError(f'Type {type(color)} cannot be a color')
        if color not in self.colors and len(self.colors)-1 < self.max:

            self.colors.append(tuple(color))
            self.rects.append(Rect((len(self.colors)-1) % self.max_per_line *self.color_rect_size+self._offSetPos[0]+self.pos[0],(len(self.colors)-1) // self.max_per_line* self.color_rect_size+self._offSetPos[1]+self.pos[1],self.color_rect_size,self.color_rect_size))
        else:
            # could not add color, either the palette was full or color already in palette
            pass

    def select_color(self,color:tuple):
        if color in self.colors:
            self.selected_color = color
            self.func(color)
            return True
        else:
            raise ValueError(f"Color {color} not in palette!")

    def has_color(self,color) -> bool:
        return (color in self.colors)

class Grid:
    '''A grid of size (x,y), each cell holding a color value'''
    @classmethod
    def accepts(cls) -> tuple:
        return('mpos','mb2')
    def __init__(self,grid_size:tuple[int],background_color = (0,0,0)):
        self.background_color = tuple(background_color)
        self.grid = [[[self.background_color,0] for x in fast_list_maker(grid_size[0])] for y in fast_list_maker(grid_size[1])]
        self.grid_size = grid_size

    def clear(self):
        self.grid = [[[self.background_color,0] for x in fast_list_maker(self.grid_size[0])] for y in fast_list_maker(self.grid_size[1])]

    def set_row(self,y,color:tuple):
        if y < 0: return
        elif y > self.grid_size[1]-1: return 
        else: self.grid[y] = [[color,1] for x in fast_list_maker(self.grid_size[0])]
    
    def set_column(self,x,color):
        if x < 0: return
        elif x > self.grid_size[0]-1: return 
        for y in range(self.grid_size[1]):
            self.grid[y][x] = [color,1]

    
    def set_color(self,x,y,color):
        if x < 0 or y < 0: return
        elif x > self.grid_size[0]-1 or y > self.grid_size[1]-1: return 
        elif color != self.grid[y][x][0]: self.grid[y][x] = [color,1]; return 1
        return 

    def clear_cell(self,x,y):
        if x < 0 or y < 0: return
        elif x > self.grid_size[0]-1 or y > self.grid_size[1]-1: return 
        else: self.grid[y][x] = [(0,0,0),0]

    def adj(self,x:int,y:int):
        return_list:list[tuple[int]] = []
        if x-1 >= 0:
            return_list.append((x-1,y))
        if x+1 < self.size[0]:
            return_list.append((x+1,y))
        if y-1 >= 0:
            return_list.append((x,y-1))
        if y+1 < self.size[1]:
            return_list.append((x,y+1))
        return return_list

    def __str__(self):
        string = ''
        for row in self.grid:
            for grid in row:
                if grid[1] == 0:
                    string += '0 '
                else:
                    string += '1 '
            string += '\n'
        return string

    def flood_recursive(self,starting_point,color):
        width = self.grid_size[0]
        height = self.grid_size[1]
        matrix = self.grid
        try:
            def fill(x,y,start_color,color_to_update):
                #if the square is not the same color as the starting point
                if matrix[y][x][0] != start_color:
                    return
                #if the square is not the new color
                elif matrix[y][x][0] == color_to_update:
                    return
                else:
                    #update the color of the current square to the replacement color
                    matrix[y][x][0] = color_to_update
                    for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                        if 0 <= n[0] <= width-1 and 0 <= n[1] <= height-1:
                            fill(n[0],n[1],start_color,color_to_update)

            start_color = self.grid[starting_point[1]][starting_point[0]]
            fill(starting_point[0],starting_point[1],start_color,color)
        except RecursionError:
            print('Could not handle the smoke')
        self.grid = matrix

    def flood_exact_list(self,starting_point:tuple,color:tuple) -> list[tuple[int,int],]:
        width = self.grid_size[0]
        height = self.grid_size[1]  
        x,y = starting_point[0],starting_point[1]
        starting_color = self.grid[y][x]
        if starting_color[0] == color: return []
        pcells = []
        cells_filled = []
        next_gen = set([1])
        add,clear,append = next_gen.add,next_gen.clear,pcells.append
        fill = cells_filled.append
        #start the mayhem
        append((x,y))
        if x and self.grid[y][x-1] == starting_color:
            append((x-1,y))
        if y and self.grid[y-1][x] == starting_color:
            append((x,y-1))
        if y < height-1 and self.grid[y+1][x] == starting_color:
            append((x,y+1))
        if x < width-1 and self.grid[y][x+1] == starting_color:
            append((x+1,y))
        #continue the process
        while next_gen:
            clear()     #wipe next_gen
            for x,y in pcells:      #iterate over all the cells in this generation 
                self.grid[y][x] = [color,1]
                fill((x,y))
                if x and self.grid[y][x-1] == starting_color:
                    add((x-1,y))
                if y and self.grid[y-1][x] == starting_color:
                    add((x,y-1))
                if y < height-1 and self.grid[y+1][x] == starting_color:
                    add((x,y+1))
                if x < width-1 and self.grid[y][x+1] == starting_color:
                    add((x+1,y))
            pcells = iter(tuple(next_gen)) #make the next generation the current one
        return cells_filled
    def flood_iterative_exact(self,starting_point,color:tuple):
        width = self.grid_size[0]
        height = self.grid_size[1]  
        x,y = starting_point[0],starting_point[1]
        starting_color = self.grid[y][x]
        if starting_color[0] == color: return
        self.grid[y][x] = [color,1]
        pcells = []
        next_gen = set([1])
        add = next_gen.add
        append = pcells.append
        clear = next_gen.clear
        #start the mayhem
        if x and self.grid[y][x-1] == starting_color:
            append((x-1,y))
        if y and self.grid[y-1][x] == starting_color:
            append((x,y-1))
        if y < height-1 and self.grid[y+1][x] == starting_color:
            append((x,y+1))
        if x < width-1 and self.grid[y][x+1] == starting_color:
            append((x+1,y))
        #continue the process
        while next_gen:
            clear()     #wipe next_gen
            for x,y in pcells:      #iterate over all the cells in this generation 
                self.grid[y][x] = [color,1]
                if x and self.grid[y][x-1] == starting_color:
                    add((x-1,y))
                if y and self.grid[y-1][x] == starting_color:
                    add((x,y-1))
                if y < height-1 and self.grid[y+1][x] == starting_color:
                    add((x,y+1))
                if x < width-1 and self.grid[y][x+1] == starting_color:
                    add((x+1,y))
            pcells = iter(tuple(next_gen)) #make the next generation the current one
    def flood_iterative_similar(self,starting_point,color,tolerance):
        width = self.grid_size[0]
        height = self.grid_size[1]  
        x,y = starting_point[0],starting_point[1]
        starting_color = self.grid[y][x]
        if starting_color[0] == color: return
        pcells = []
        next_gen = set()
        add =next_gen.add
        #start the mayhem
        for x,y in adj(x,y,width,height):
            if is_similar(tuple(self.grid[y][x]), tuple(starting_color),tolerance):
                pcells.append((x,y))
        #continue the process
        while next_gen:
            next_gen.clear()
            for x,y in pcells: #iterate over all the cells in this generation
                self.grid[y][x] = color
                for x1,y1 in adj(x,y,width,height): # for each adj cell of the current generations
                    if is_similar(tuple(self.grid[y1][x1]), tuple(starting_color),tolerance) and self.grid[y1][x1] != color:
                        add((x1,y1))
  
            pcells = tuple(next_gen) #make the next generation the current one

    def line(self,starting_point:tuple[int,int],ending_point:tuple[int,int],color:tuple[int,int,int]):
        if starting_point[0] > ending_point[0]:
            starting_point,ending_point = ending_point,starting_point
        elif starting_point == ending_point:
            starting_point = color
            return
        
        x1,y1 = starting_point
        x2,y2 = ending_point
        if x1 != x2: # if not a vertical line
            slope = (y2-y1)/(x2-x1)
            if 0<=slope<=1:
                count = 0
                err = 0
                y = 0
                while count <= ending_point[0]-starting_point[0]:
                    self.grid[y+y1][count+x1] = color
                    err += slope 
                    if err > 0.5:
                        y += 1
                        err -= 1
                    count += 1
            elif 1<slope:
                slope = 1/slope
                count = 0
                err = 0
                x = 0
                while count < ending_point[1]-starting_point[1]:
                    self.grid[count+y1][x+x1] = color
                    err += slope
                    if err > 0.5:
                        x += 1
                        err -= 1
                    count += 1
                self.grid[y2][x2] = color
            elif -1<=slope<=0:
                count = 0
                err = 0
                y = 0
                while count <= ending_point[0]-starting_point[0]:
                    self.grid[y+y1][count+x1] = color
                    err += slope
                    if err < -0.5:
                        y -= 1
                        err += 1
                    count += 1
            elif slope<-1:
                slope = 1/slope
                count = 0
                err = 0
                x = 0
                while count <= ending_point[1]-starting_point[1]:
                    self.grid[count+y1][x+x1] = color
                    err += slope
                    if err < -0.5:
                        x += 1
                        err -= 1
                    count += 1
        else:
            if starting_point[1] > ending_point[1]:
                starting_point,ending_point = ending_point,starting_point
            for y in range(ending_point[1]-starting_point[1]):
                self.grid[y][x1] = color
                
