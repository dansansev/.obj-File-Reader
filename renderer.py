import pygame as pg
import math
pg.init()
fps= 60
info = pg.display.Info()
xpixels = info.current_w
ypixels = info.current_h

screen_size=(xpixels,ypixels)

center = (xpixels/2,ypixels/2)

graph_scale = 100

fov = .3

#create elementary matrix functions
class matrix():

    all_matrices = [[],[],[]]

    #standard matrix multiplication
    def multiply(matrix1,matrix2):
        new_matrix = []
        for rowcounter1 in range(len(matrix1)):
            new_row = []
            for colcounter2 in range(len(matrix2[0])):
                val = 0
                for colindex in range(len(matrix2)):
                    #imagine the matrices
                    #x pos of left goes with y pos of right
                    val += matrix1[rowcounter1][colindex] * matrix2[colindex][colcounter2] 
                new_row.append(val)
            new_matrix.append(new_row)
        return new_matrix
    
    #x=0,y=1,z=2
    #defines rotation matrices
    def create_rot_matrices(theta,axis):
        if axis == 0:
            xrot=[ 
                [1,0,0],
                [0,math.cos(theta),-math.sin(theta)],
                [0,math.sin(theta),math.cos(theta)]
                        ]
            matrix.all_matrices[0] = xrot
        if axis == 1:
            yrot=[
                [math.cos(theta),0,math.sin(theta)],
                [0,1,0],
                [-math.sin(theta),0,math.cos(theta)]
                        ]
            matrix.all_matrices[1] = yrot
        if axis == 2:    
            zrot=[
                [math.cos(theta),-math.sin(theta),0],
                [math.sin(theta),math.cos(theta),0],
                [0,0,1]
                        ]
            matrix.all_matrices[2] = zrot


class camera():
    def __init__(self,pos,thetas):
        self.pos = pos
        self.thetalist=thetas
        self.mousemovement = (0,0)

        self.whold= False
        self.ahold= False
        self.shold= False
        self.dhold= False
        self.rhold= False
        self.spacehold = False
        self.chold = False

    #handles position updates
    def update_pos(self,change_list,lagslow_mult):
        for i in range(len(self.pos)):
            self.pos[i]+=change_list[i]*lagslow_mult
    #handles angle updates
    def turn(self):
        self.thetalist[1] -= (self.mousemovement[0])/500
        self.thetalist[0] += (self.mousemovement[1])/500

        #stop mouse from going off screen
        maxangle = math.pi/2 -.001
        if self.thetalist[0]>maxangle:
            self.thetalist[0]=maxangle
        if self.thetalist[0]<-maxangle:
            self.thetalist[0]=-maxangle
        #reset mousemovement
        self.mousemovement = (0,0)

        
    #creates rotation matrices with camera angles
    def set_rot_matrices(self):
        for index in range(3):
            matrix.create_rot_matrices(self.thetalist[index],index)

    #handles inputs with pygame
    def check_for_inputs(self,eventlist):
        for event in eventlist:
            if event.type == pg.KEYDOWN:
                downup = True
                if event.key == pg.K_ESCAPE:
                    return False
            if event.type == pg.KEYUP:
                downup = False
            if event.type == pg.KEYUP or event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.whold=downup
                if event.key == pg.K_a:
                    self.ahold=downup
                if event.key == pg.K_s:
                    self.shold = downup
                if event.key == pg.K_d:
                    self.dhold = downup
                if event.key == pg.K_r:
                    self.rhold = downup
                if event.key == pg.K_SPACE:
                    self.spacehold = downup
                if event.key == pg.K_LSHIFT:
                    self.chold = downup
            
            if event.type == pg.MOUSEMOTION:
                self.mousemovement=event.rel
                camera.check_for_outside()
                
        return True

    #returns mouse to center screen if nearing border of window
    def check_for_outside():
        mousepos = pg.mouse.get_pos()
        if mousepos[0] > xpixels-100 or mousepos[0] < 100:
            pg.mouse.set_pos(center[0],pg.mouse.get_pos()[1])
        if mousepos[1] > ypixels-100 or mousepos[1] < 100:
            pg.mouse.set_pos(pg.mouse.get_pos()[0],center[1])
        
    #handles logic to convert inputs to actions
    def determine_movement(self):
        fb_move=0
        if not (self.whold and self.shold):
            if self.whold:
                fb_move=.01
            if self.shold:
                fb_move=-.01
        
        lr_move=0
        if not (self.ahold and self.dhold):
            if self.dhold:
                lr_move=-.01
            if self.ahold:
                lr_move=.01
                
        updown_move=0
        if not (self.spacehold and self.chold):
            if self.spacehold:
                updown_move = .01
            if self.chold:
                updown_move=-.01
        adjuster = 60/fps
        if self.rhold:
            adjuster *= 30
        
        #determine movement based on direction the camera is looking
        fb_actforcamera = fb_move*math.cos(self.thetalist[1]) + lr_move*math.cos(self.thetalist[1]+math.pi/2)
        lr_actforcamera = fb_move*math.sin(self.thetalist[1]) + lr_move*math.sin(self.thetalist[1]+math.pi/2)
        
        return (lr_actforcamera*adjuster,updown_move*adjuster,fb_actforcamera*adjuster)



#class for points in obj file
class point():
    pointlist = []
    all_camorigin_cords = []
    def __init__(self,x,y,z,cutpoint_tf=False):
        self.startx = x
        self.starty = y
        self.startz = z
        self.startcords = (x,y,z)

        #point cords if camera defines as origin
        self.cords_camorigin = []
        #point cords after rotated by camera
        self.cords_rotated = []
        #2d cords scaled for depth
        self.zscaled_cords = []
        #zscaled cords scaled for screen
        self.screencords = []

        #boolean for point being temporary, clipped point
        self.cutpoint = cutpoint_tf
        self.behind_camera = False
        #list of points the point connects with
        self.connectwith=[]
        
        point.pointlist.append(self)

        if self.cutpoint:
            self.cords_rotated=[x,y,z]

    def connect(self,connectlist):
        for obj in connectlist:
            self.connectwith.append(obj)
        
            

    #centers a given point on the user (camera movement)
    def center_on_camera(self,camera):
        self.cords_camorigin = []
        for index in range(3):
            self.cords_camorigin.append(self.startcords[index]-camera.pos[index])
    

    

    #accounts for the z, scaling the x and y cords accordingly
    #checks for a z cord behind 
    def scale_for_z(self):
        self.zscaled_cords = []
        for index in range(2):
            distance = self.cords_rotated[2]
            if distance == 0:
                #fov for depth changing
                self.zscaled_cords.append(self.cords_rotated[index]*-1/(fov*.001))
            else:
                distance = self.cords_rotated[2]
                self.zscaled_cords.append(self.cords_rotated[index] * -1/(fov*distance))

    #takes in (x,y) on my own scale, converts that to the screen
    def convert_to_screen_cords(self):
        self.screencords= []
        #just goes through x and  y
        for index in range(2):
            self.screencords.append(center[index] + self.zscaled_cords[index]*graph_scale)
        
    


    #cut off the points behind the camera
    def cutoff_points():
        #go through each point
        for point_obj in point.pointlist:
            #if that point is behind the camera
            if point_obj.cords_rotated[2] < 0:
                point_obj.behind_camera = True
                #create more points at the spot the lines cross the camera
                for connect_obj in point_obj.connectwith:
                    
                    if connect_obj.cords_rotated[2] > 0:
                        #get differences in the connected value (on screen) and the current (off screen)
                        change_in_x=point_obj.cords_rotated[0]-connect_obj.cords_rotated[0]
                        change_in_y=point_obj.cords_rotated[1]-connect_obj.cords_rotated[1]
                        change_in_z=point_obj.cords_rotated[2]-connect_obj.cords_rotated[2]

                        #handle division by 0
                        dxzero= False
                        dyzero = False
                        if change_in_x == 0:
                            dxzero = True
                            if change_in_y == 0:
                                dyzero = True
                                
                        #if both are zero, use same cords
                        if dyzero:
                            newx =point_obj.cords_rotated[0]
                            newy = point_obj.cords_rotated[1]
                        #if only x was zero
                        elif dxzero:
                            #use same x
                            newx=point_obj.cords_rotated[0]
                            #yz projection of line we are drawing, solving for y intercept (z=0)
                            yz_intercept = (change_in_z/change_in_y) * point_obj.cords_rotated[1]-point_obj.cords_rotated[2]
                            #rearrange into b/m to find new y value, when the line clips the z=0 plane
                            newy = yz_intercept*(change_in_y/change_in_z)
                        else:
                            #if y was zero and x wasnt, or both werent
                            #construct line equations in xy plane
                            xz_intercept = (change_in_z/change_in_x) * point_obj.cords_rotated[0] - point_obj.cords_rotated[2]
                            #construct line equations in xy plane
                            xy_intercept = (change_in_y/change_in_x) * point_obj.cords_rotated[0] - point_obj.cords_rotated[1]

                            #rearrange to b/m again
                            newx = xz_intercept * (1/(change_in_z/change_in_x))
                            #we already found new x, so plug into y=mx+b
                            newy = -xy_intercept + (change_in_y/change_in_x)*newx

                        new_point = point(newx,newy,0,True)
                        new_point.connect((connect_obj,))
            else:
                point_obj.behind_camera = False





    #to rotate every cord
    def rotate_all():
        #rotates around axis 1 (y) first, then around 0 (x)
        rotated_matrix = matrix.multiply(matrix.multiply(point.all_camorigin_cords,matrix.all_matrices[1]),matrix.all_matrices[0])
        #puts the rotated values back in to each object
        for index in range(len(rotated_matrix)):
            point.pointlist[index].cords_rotated = rotated_matrix[index]
