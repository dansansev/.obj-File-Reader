import pygame as pg
import renderer
pg.init()

#Enter filename, with .obj extension here
filename = "cessna.obj"



#pixelsize for screen, useful for translating to pygame cords
#based on screen resolution
info = pg.display.Info()
xpixels = info.current_w
ypixels = info.current_h

fps=renderer.fps

#mouse invisible
pg.mouse.set_visible(False)
pg.event.set_grab(True)


#starting camera position, changed later during movement
camerapos = [0,0,2]

#initialize pygame screen
screen=pg.display.set_mode((0,0),pg.FULLSCREEN)
running=True
font=pg.font.SysFont("Roboto", 70)

#load file for obj
with open("objfiles/" + filename,"r") as objfile:
    file_contents = objfile.readlines()
allcords = []
allfaces = []

extraline_counter=0

#read the obj file, convert to useable data
for index in range(len(file_contents)):
    line = file_contents[index]
    #given a face or vertex
    if (line[0] == "v" and line[1] == " ") or line[0] == "f":
        #location of vertex or face
        cords = [index+1-extraline_counter]
        currentcord = ""
        letter_i = 1
        #go through space after the first letter
        while(line[letter_i] == " "):
            letter_i+=1
        
        #while we didnt go over
        while(letter_i < len(line)-1):
            #add to the cord
            currentcord+=line[letter_i]
            letter_i+=1
            
            #if we hit a slash
            if line[letter_i] == "/":
                #go through until a space or \n
                while(line[letter_i] != " " and line[letter_i] != "\n"):
                    letter_i+=1
                
                
            if line[letter_i] == "\n" or line[letter_i] == " ":
                cords.append(float(currentcord))
                currentcord = ""
                letter_i+=1
        if line[0] == "v":
            allcords.append(cords)
        else:
            allfaces.append(cords)
    elif line[0] != "v":
        extraline_counter+=1

#construct point objects, with cords and index
for cordlist in allcords:
    renderer.point(cordlist[1],cordlist[2],cordlist[3])

#use faces in file to connect point objects
for face in allfaces:
    for i in range(1,len(face)):
        mypoint = renderer.point.pointlist[int(face[i])-1]
        nextval = i+1
        if nextval == len(face):
            nextval = 1
        mypoint.connect((renderer.point.pointlist[int(face[nextval])-1],))
    
    
    
# #define rotation for each axis
thetax = 0
thetay = 0
thetaz = 0

#create camera
camera = renderer.camera(camerapos,[thetax,thetay,thetaz])

#center the points on the camera, do to all points
def get_camorigincords(camera):
    renderer.point.all_camorigin_cords = []
    for point_obj in renderer.point.pointlist:
        point_obj.center_on_camera(camera)
        #appends the point cords to a list to be used for rotation
        renderer.point.all_camorigin_cords.append(point_obj.cords_camorigin)

#scale all points for depth, convert to screen coordinates
def scale_z_and_getscreencords():
    for point in renderer.point.pointlist:
        point.scale_for_z()
        point.convert_to_screen_cords()
            
def draw_lines():
    #draw line between points
    for point in renderer.point.pointlist:
        for point_connect in point.connectwith:
            if not (point.behind_camera or point_connect.behind_camera):
                line_color = (255,255,255)
                pg.draw.line(screen,line_color,point.screencords,point_connect.screencords)

while (running):
    #note time before drawing and performing calculations
    start_time = pg.time.get_ticks()
    onscreen_start = pg.time.get_ticks()
    running = camera.check_for_inputs(pg.event.get())
    camera.turn()

    #initialize based on angle of camera
    camera.set_rot_matrices()
    #update cords based on camera
    get_camorigincords(camera)
    renderer.point.rotate_all()
    renderer.point.cutoff_points()
    scale_z_and_getscreencords()
    draw_lines()

    #assume 1 frame of time will pass
    frames_passed = 1
    end_time = pg.time.get_ticks()

    #difference between expected time per frame and the time this frame took
    time_under_oneframe = 1/fps*1000 - (end_time-start_time)

    #if we went faster than the framerate
    if time_under_oneframe > 0:
        #delay for that time
        pg.time.delay(int(time_under_oneframe))
    else:
        #save value of time / expected time per frame = expected frames that have passed
        frames_passed = (end_time-start_time)/(1/fps*1000)


    onscreen_end = pg.time.get_ticks()

    #update camera and position based on input
    movement = camera.determine_movement()
    camera.update_pos(movement,frames_passed)

    #render fps
    text = font.render(str(int(1000/(onscreen_end-onscreen_start))),1,(255,255,255))
    
    screen.blit(text,(0,0))
    
    pg.display.update()
    screen.fill("black")

    #remove temporary cutpoints from total points list
    obj_index= 0
    while (obj_index < len(renderer.point.pointlist)):
        pobj = renderer.point.pointlist[obj_index]
        if pobj.cutpoint:
            renderer.point.pointlist.remove(pobj)
            obj_index-=1
        obj_index+=1 
    
pg.quit()





