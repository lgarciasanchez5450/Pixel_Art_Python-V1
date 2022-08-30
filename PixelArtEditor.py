from typing import Text
from framework import *
from colors import *
from PixelArt_Framework import *
import framework
import colorsys
import pickle
canvas:Canvas
save_as_png_name = ''
save_AS_GIF_name = ''
GIF_fps = 30
GIF_pixel_size = 1
h,s,v = (0,0,0)
name_alert_time = 0.0
canvas_width = 64
canvas_height = 64
saved_project_names = findAllFiles('.bin','/__Projects/')
def set_GIF_fps(newVal) -> None:
  global GIF_fps
  GIF_fps = newVal
  window_space.miniWindow('Export As GIF').gif_fps_text.setText(str(newVal))

def set_GIF_name(newVal):
  global save_AS_GIF_name
  save_AS_GIF_name = newVal

def make_gif():
  global save_AS_GIF_name
  milliseconds_per_frame = 1000/GIF_fps
  save_as_GIF([grid.grid for grid in canvas.grids],save_AS_GIF_name,PATH,milliseconds_per_frame,GIF_pixel_size)

def set_GIF_pixel_size(newVal) -> None:
  global GIF_pixel_size
  GIF_pixel_size = newVal + 1
  window_space.miniWindow('Export As GIF').pixel_size_text.setText(str(newVal+ 1))

def make_png(color_grid:list[list[list[tuple[int,int,int],bool]]],pixel_size:int,name:str):
  from PIL import Image
  PNGPixelList:list = []
  for pixelRow in color_grid:
    for _1 in range(pixel_size):
      for pixel in pixelRow:
        for _2 in range(pixel_size):
          if pixel[1] != 0:
            PNGPixelList.append((pixel[0][0],pixel[0][1],pixel[0][2],255))
          elif pixel[1] == 0:
            PNGPixelList.append((0,0,0,0))
  img = Image.new('RGBA',(canvas.grid_size[0]*pixel_size,canvas.grid_size[1]*pixel_size))
  img.putdata(PNGPixelList)    
  if name:
    img.save(PATH+'/Exports/'+name+'.png')
  else:
    img.save(PATH+'/Exports/'+canvas.name+'.png')
def set_color_brick_h(_h):
  global h
  h = _h/360
  color = colorsys.hsv_to_rgb(h,s,v)
  window_space.miniWindow('Color Picker').color_brick.color = (color[0]*255,color[1]*255,color[2]*255)
  color_pure = colorsys.hsv_to_rgb(h,1,1)
  color_pure = color_pure[0]*255,color_pure[1]*255,color_pure[2]*255
  window_space.miniWindow('Color Picker').sat_bg.image.fill(color_pure)
  color_pure = colorsys.hsv_to_rgb(h,s,1)
  color_pure = color_pure[0]*255,color_pure[1]*255,color_pure[2]*255
  window_space.miniWindow('Color Picker').val_bg.image.fill(color_pure)
def set_color_brick_s(_s):
  global s
  s = _s/100
  color = colorsys.hsv_to_rgb(h,s,v)
  window_space.miniWindow('Color Picker').color_brick.color = (color[0]*255,color[1]*255,color[2]*255)
  color_pure = colorsys.hsv_to_rgb(h,s,1)
  color_pure = color_pure[0]*255,color_pure[1]*255,color_pure[2]*255
  window_space.miniWindow('Color Picker').val_bg.image.fill(color_pure)
def set_color_brick_v(_v):
  global v
  v = _v/100
  color = colorsys.hsv_to_rgb(h,s,v)
  window_space.miniWindow('Color Picker').color_brick.color = (color[0]*255,color[1]*255,color[2]*255)
def set_png_name(newVal) -> None:
  global save_as_png_name
  save_as_png_name = newVal
specify_platform('win32')
setFPS(144)
init((0,0),NOFRAME|HWSURFACE)
png_surf = loadImg('__Images/ppnngg.png',True)
pen_surf = loadImg('__Images/pencil.png',True)
eraser_surf = loadImg('__Images/eraser.png',True)
bucket_surf = loadImg('__Images/bucket.png',True)
line_surf = loadImg('__Images/line.png',True)
pan_surf = loadImg('__Images/pan.png',True)

hue_map = rotateSurface(loadImg('__Images/hue-map.png',1),270 )
hue_map = resizeSurface(hue_map,(360,10))

value_map = rotateSurface(loadImg('__Images/sv-map.png',1).subsurface(399,0,1,400),270)
value_map = resizeSurface(value_map,(360,10))

sat_map = loadImg('__Images/sv-map.png',1).subsurface(0,0,400,1)
sat_map = resizeSurface(sat_map,(360,10))

exit_surf = Surface((48,30)).convert_alpha()
exit_surf.fill((0,0,0,0))
line(exit_surf,light_grey,(18,9),(30,21),1)
line(exit_surf,light_grey,(18,21),(30,9),1)
min_surf = Surface((48,30)).convert_alpha()
min_surf.fill((0,0,0,0))
line(min_surf,light_grey,(17,15),(31,15),1)

def add_to_palette() -> None:
  color = colorsys.hsv_to_rgb(h,s,v)
  color = (round(color[0]*255),round(color[1]*255),round(color[2]*255))
  color_palette.add_color(color)
def start_MW(name:str) -> function:
  def _() -> None:
    global miniwindow_active
    miniwindow_active = window_space._miniwindowactive
    if miniwindow_active:
      window_space.deactivateMiniWindow()
    window_space.activateMiniWindow(name)
  return _
def end_MW() -> function:
  def _() -> None:
    global miniwindow_active
    window_space.deactivateMiniWindow()
    if miniwindow_active:
      window_space.activateMiniWindow('Palette')
  return _
def set_canvas_width(newVal) -> None:
  global canvas_width
  canvas_width = int(newVal) if newVal else 64
def set_canvas_height(newVal) -> None:
  global canvas_height
  canvas_height = int(newVal) if newVal else 64
def set_project_name(newVal) -> None:
  global project_name
  project_name = newVal if newVal else 'Project #'+str(len(saved_project_names))
set_project_name('')
def save_as_png() -> None:
  make_png(canvas.current_grid.grid,PNG_pixel_size,save_as_png_name)
def center_palette() -> None:
  offset = window_space.miniWindow('Palette')._offset
  window_space.miniWindow('Palette').move((framework.WIDTH//2-offset[0],framework.HEIGHT//2-offset[1]))

def backup_project(save_as) -> None:
  '''Does essentially the same thing as save_project but saves to a seperate file'''
  #get_canvas_info
  canvas_info = canvas.flatten_info()
  #get_palette_info
  palette_info = color_palette.get_info()
  #store_them_in_file
  with open('Backups/'+save_as+'.bin','wb') as file:
    pickle.dump((canvas_info,palette_info),file)
  
  
def save_project() -> None:
  #get_canvas_info
  canvas_info = canvas.flatten_info()
  #get_palette_info
  palette_info = color_palette.get_info()
  #store_them_in_file
  with open('__Projects/'+canvas.name+'.bin','wb') as file:
    pickle.dump((canvas_info,palette_info),file) 
  canvas.saved = True
def maybe_quit() -> None:
  if canvas.saved:
    quit()
  else:
    start_MW('Quit')()

def set_backup_name(newVal) -> None:
  global backup_name
  backup_name = newVal

def save_and_quit() -> None:
  save_project()
  quit()

def set_PNG_pixel_size(newVal) -> None:
  global PNG_pixel_size 
  PNG_pixel_size = newVal + 1
  window_space.miniWindow('Export As PNG').pixel_size_text.setText(str(PNG_pixel_size))

def center_canvas() -> None:
  global canvas
  canvas.pos = (window_space.MSSize[0]//2-canvas.grid_size[0]*canvas.screen_size//2,window_space.MSSize[1]//2-(canvas.grid_size[1]*canvas.screen_size)//2)
window_space = Window_Space()
window_space.addMiniWindow('Palette',(framework.WIDTH//2,framework.HEIGHT//2),(200,400),light_dark_grey,lambda:1,False)
window_space.addMiniWindow('Quit',(framework.WIDTH//2-200,framework.HEIGHT//2-50),(200,150),light_grey,end_MW())
window_space.miniWindow('Quit').normal_quit = Button((20,30),150,30,quit,grey,grey,dark_light_grey,'Quit',0,4)
window_space.miniWindow('Quit').save_and_quit = Button((20,70),150,30,save_and_quit,grey,grey,dark_light_grey,'Save and Quit',0,4)
window_space.miniWindow('Quit').cancel = Button((20,110),150,30,end_MW(),grey,grey,dark_light_grey,'Cancel',0,4)
window_space.addMiniWindow('Color Picker',(framework.WIDTH//2-200,framework.HEIGHT//2-200),(400,300),dark_light_grey,end_MW())
window_space.miniWindow('Color Picker').color_brick = ScreenSurface((20,45),(360,50),(0,0,0))
window_space.miniWindow('Color Picker').hue = Slider(20,120,360,12,0,361,set_color_brick_h,hue_map,purple)
window_space.miniWindow('Color Picker').sat_bg  = Image((20,160),Surface((360,10)))
window_space.miniWindow('Color Picker').saturation = Slider(20,160,360,12,0,100,set_color_brick_s,sat_map,theme_light_yellow)
window_space.miniWindow('Color Picker').val_bg  = Image((20,200),Surface((360,10)))
window_space.miniWindow('Color Picker').value = Slider(20,200,360,12,0,100,set_color_brick_v,value_map,purple)
window_space.miniWindow('Color Picker').add_button = Button((20,250),360,40,add_to_palette,light_grey,light_grey,grey,'Add To Palette',120,0,None,enter_unicode)

window_space.addMiniWindow('Export',(framework.WIDTH//2-200,framework.HEIGHT//2-200),(400,200),dark_light_grey,end_MW())
window_space.miniWindow('Export').as_png = Button((10,30),180,30,start_MW('Export As PNG'),grey,grey,light_dark_grey,'Export As PNG',40,3)
window_space.miniWindow('Export').as_gif = Button((10,70),180,30,start_MW('Export As GIF'),grey,grey,light_dark_grey,'Export As GIF',40,3)

window_space.addMiniWindow('Export As PNG',(framework.WIDTH//2-200,framework.HEIGHT//2-200),(400,200),dark_light_grey,end_MW())
window_space.miniWindow('Export As PNG').name = InputBox((20,30),(360,30),'Save as:',grey,20,set_png_name,fileNameFriendlyCharacters)
window_space.miniWindow('Export As PNG').text = TextBox((20,75),makeFont('Arial',17),'Pixel Size:',black)
window_space.miniWindow('Export As PNG').pixel_size = Slider(20,100,200,10,0,10,set_PNG_pixel_size,black,red)
window_space.miniWindow('Export As PNG').pixel_size_text = TextBox((250,95),makeFont('Arial',20),'1',black)
window_space.miniWindow('Export As PNG').done = Button((20,120),360,23,save_as_png,dark_grey,light_grey,grey,'Done')
window_space.miniWindow('Export As PNG').text2 = TextBox((15,150),makeFont('Arial',17),'NOTE: Will only use the currently selected frame.',black)

window_space.addMiniWindow('Export As GIF',(framework.WIDTH//2-200,framework.HEIGHT//2-200),(400,300),dark_light_grey,end_MW())
window_space.miniWindow('Export As GIF').name = InputBox((20,30),(360,30),'Save as:',grey,20,set_GIF_name,fileNameFriendlyCharacters)
window_space.miniWindow('Export As GIF').text = TextBox((20,75),makeFont('Arial',17),'Pixel Size:',black)
window_space.miniWindow('Export As GIF').pixel_size = Slider(20,100,200,10,0,10,set_GIF_pixel_size,black,red)
window_space.miniWindow('Export As GIF').pixel_size_text = TextBox((250,95),makeFont('Arial',20),'1',black)
window_space.miniWindow('Export As GIF').text2 = TextBox((20,120),makeFont('Arial',17),'FPS:',black)
window_space.miniWindow('Export As GIF').gif_fps = Slider(20,150,200,10,2,100,set_GIF_fps,black,red)
window_space.miniWindow('Export As GIF').gif_fps_text = TextBox((250,120),makeFont('Arial',20),'1',black)
window_space.miniWindow('Export As GIF').done = Button((20,200),360,20,make_gif,dark_grey,light_grey,grey,'Done')

window_space.addMiniWindow('Backup Project',(framework.WIDTH//2-200,framework.HEIGHT//2-200),(400,400),dark_light_grey,end_MW())
window_space.miniWindow('Backup Project').name = InputBox((20,30),(360,30),'Backup as:',grey,20,set_backup_name,fileNameFriendlyCharacters)
window_space.miniWindow('Backup Project').done = Button((20,100),360,50,lambda:backup_project(backup_name),light_green,light_green,green,'Back Up')


window_space.addBorder('top',30,dark_grey,2)
window_space.addBorder('right',48,dark_grey,2,light_dark_grey)
window_space.addBorder('left',100,dark_grey,2)
#left border should hold
#top border should hold 
window_space.top.exit_button = Button((framework.WIDTH-48,0),48,30,maybe_quit,(0,0,0,0),(0,0,0,0),(200,0,0),exit_surf)
window_space.top.minimize_button = Button((framework.WIDTH-48-48,0),48,30,iconify,(0,0,0,0),(0,0,0,0),(200,0,0),min_surf)
window_space.top.title = TextBox((framework.WIDTH//2-37,3),makeFont('Arial',20),'Pixel Art',light_grey)
#right border should hold
window_space.right.add_color = Button((0,0),48,48,start_MW('Color Picker'),black,grey,light_blue,'+')
window_space.right.pen =    Button((0,48*1),48,48,lambda:canvas.set_current_tool(0),grey,grey,light_dark_grey,pen_surf,key='q')
window_space.right.eraser = Button((0,48*2),48,48,lambda:canvas.set_current_tool(1),grey,grey,light_dark_grey,eraser_surf,key='e') 
window_space.right.bucket = Button((0,48*3),48,48,lambda:canvas.set_current_tool(2),grey,grey,light_dark_grey,bucket_surf,key='b')
window_space.right.line =   Button((0,48*4),48,48,lambda:canvas.set_current_tool(3),grey,grey,light_dark_grey,line_surf,key='w')
window_space.right.pan =    Button((0,48*5),48,48,lambda:canvas.set_current_tool(4),grey,grey,light_dark_grey,pan_surf,key='z')
window_space.right.png =    Button((0,48*6),48,48,start_MW('Export'),grey,grey,light_dark_grey,png_surf)
window_space.right.save =   Button((0,48*7),48,48,save_project,grey,grey,light_dark_grey,'save')
window_space.right.backup = Button((0,48*8),48,48,start_MW('Backup Project'),grey,grey,light_grey,'backup')
window_space.right.center_canvas = KeyBoundFunction(center_canvas,'c')
#left border should hold
#grid previews

window_space.mainSpace = ScrollingMS(2,0) #mainSpace #1

def check_alert() -> None:
  global title_screen
  while 1:
    if title_screen._title_done:
      return
    else:
      if -2<name_alert_time -time.time()< 0:  
        title_screen.__dict__['invalid_name'].hide()
    time.sleep(1)


def load_project(fileName:str) -> None:
  title_screen.stop_early()
  global canvas, color_palette
  with open('__Projects/'+fileName+'.bin','rb') as file:
    canvas_info,palette_info = pickle.load(file)
    window_space.mainSpace.canvas = canvas = Canvas((0,0),(3,3),fileName)
    canvas.load(*canvas_info)
    window_space.miniWindow('Palette').palette = color_palette = Palette((0,30),(200,370),canvas.set_current_color)
    color_palette.load(*palette_info)
    window_space.left.previews = Previews((0,0),(100,window_space.MSSize[1]-100),canvas)
    window_space.left.add_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-20),100,20,window_space.left.previews.add_frame,grey,grey,dark_grey,'Add Frame',0,1)
    window_space.left.del_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-40),100,20,window_space.left.previews.delete_frame,grey,grey,dark_grey,'Del. Frame',0,1)
    window_space.left.move_up_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-60),100,20,window_space.left.previews.move_up,grey,grey,dark_grey,'Move Up',0,1)
    window_space.left.move_down_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-80),100,20,window_space.left.previews.move_down,grey,grey,dark_grey,'Move Down',0,1)
    window_space.left.copy = Button((0,framework.HEIGHT-window_space.MSPos[1]-100),100,20,window_space.left.previews.copy,grey,grey,dark_grey,'Copy',3,1)

def make_new_project() -> None:
  global canvas,title_screen,project_name,color_palette,name_alert_time
  if project_name in saved_project_names:
    name_alert_time = 5 + time.time()
    title_screen.invalid_name.show()
    return
  title_screen.stop_early()
  window_space.mainSpace.canvas = canvas = Canvas((0,0),(canvas_width,canvas_height),project_name)
  window_space.miniWindow('Palette').palette = color_palette = Palette((0,30),(200,370),canvas.set_current_color)
  window_space.left.previews = Previews((0,0),(100,window_space.MSSize[1]-100),canvas)
  window_space.left.add_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-20),100,20,window_space.left.previews.add_frame,grey,grey,dark_grey,'Add Frame',0,1)
  window_space.left.del_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-40),100,20,window_space.left.previews.delete_frame,grey,grey,dark_grey,'Del. Frame',0,1)
  window_space.left.move_up_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-60),100,20,window_space.left.previews.move_up,grey,grey,dark_grey,'Move Up',0,1)
  window_space.left.move_down_frame = Button((0,framework.HEIGHT-window_space.MSPos[1]-80),100,20,window_space.left.previews.move_down,grey,grey,dark_grey,'Move Down',0,1)
  window_space.left.copy = Button((0,framework.HEIGHT-window_space.MSPos[1]-100),100,20,window_space.left.previews.copy,grey,grey,dark_grey,'Copy',3,1)

######## TITLE SCREEN ########
title_screen = TitleScreen()
#this mainSpace will be for seeing all your projects and a 'new project' 

title_screen.exit_button = Button((framework.WIDTH-48,0),48,30,quit,(0,0,0,0),(0,0,0,0),(200,0,0),exit_surf)
title_screen.minimize_button = Button((framework.WIDTH-48-48,0),48,30,iconify,(0,0,0,0),(0,0,0,0),(200,0,0),min_surf)
title_screen.projects_title = TextBox((30,30),makeFont('Roboto',30),'Saved Projects',white)
title_screen.projects  = Dropdown((30,55),(400,30),grey,grey,light_dark_grey,lambda:saved_project_names,lambda x:load_project(saved_project_names[x]),framework.HEIGHT-55)
title_screen.name = InputBox((framework.WIDTH//2-190,framework.HEIGHT//2-35),(380,25),'Example Project Name...',light_dark_grey,30,set_project_name,fileNameFriendlyCharacters)
title_screen.canvas_x = InputBox((framework.WIDTH//2-60,framework.HEIGHT//2),(50,22),'64',(160,160,160),4,set_canvas_width,numbers.union({back_unicode,}))
title_screen.times = TextBox((framework.WIDTH//2-8,framework.HEIGHT//2-4),makeFont('Roboto',40),'×',white)
title_screen.canvas_y = InputBox((framework.WIDTH//2+10,framework.HEIGHT//2),(50,22),'64',(160,160,160),4,set_canvas_height,numbers.union({back_unicode,}))
title_screen.new_project = Button((framework.WIDTH//2-60,framework.HEIGHT//2+35),120,30,make_new_project,grey,grey,light_dark_grey,'New Project',5)
title_screen.invalid_name = TextBox((framework.WIDTH//2-190,framework.HEIGHT//2-60),makeFont('Arial',20),'Invalid Name! Try Again.',red,False)
thread = threading.Thread(target = check_alert,daemon=True)
thread.start()
title_screen._start()
######## TITLE SCREEN ########
window_space.activateMiniWindow('Palette')
# startup
window_space.first_update()
window_space.first_draw()
running = 1
while running:
  myInput = getAllInput()
  if myInput.quitEvent: break
  window_space.update(myInput)
  window_space.draw()
  tick() 