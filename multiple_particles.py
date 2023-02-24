#file
#multiple gold particles
from vpython import *
import math
import numpy as np
import matplotlib.pyplot as plt
scale = 1e-10
scene2 = canvas(title='Rutherford Scattering', background=color.white)
#scene.range = 0.5*scale
run = True
R = scale
qe = 1.6e-19
KE = 1e5*1.6e-19 # eV*conversion_factor_to_J
kel = 9e9
range_of_particles = arange(-0.02*scale,scale*0.20,scale*0.01)
vx=[]
vy=[]
yi=[]
theta=[]
#arange(, height,density )

alphas = []

for i in range_of_particles:
    particle = sphere(color=color.black,radius=0.001*R,stop=False)
    attach_trail(particle,radius=0.001*R,color=color.black)
    particle.mass = 4*1.67e-27 # kg
    particle.charge = 2*qe
    particle.pos = vec(-0.6*scale, i, 0)
    yi.append(particle.pos.y)
    particle.mom = sqrt(2*particle.mass*KE)*vec(1,0,0)
    alphas.append(particle)

gold = sphere(color=color.black,radius=0.01*scale)
gold2 = sphere(color=color.black,radius=0.01*scale)
gold2.pos=vec(0.2*scale,0.1*scale,0)
gold3 = sphere(color=color.black,radius=0.01*scale)
gold3.pos=vec(0.1*scale,0.2*scale,0)
gold4 = sphere(color=color.black,radius=0.01*scale)
gold4.pos=vec(0.1*scale,0.05*scale,0)
gold.charge, gold2.charge, gold3.charge, gold4.charge = 79*qe,79*qe,79*qe,79*qe
dt = 1e-19
t=0
while(run==True):
    rate(40)
    for particle in alphas:
        if particle.stop == False:
            runit = particle.pos/mag(particle.pos)
            runit2 = (particle.pos-gold2.pos)/mag(particle.pos-gold2.pos)
            runit3 = (particle.pos-gold3.pos)/mag(particle.pos-gold3.pos)
            runit4 = (particle.pos-gold4.pos)/mag(particle.pos-gold4.pos)
            F = kel*particle.charge*gold.charge/mag2(particle.pos)*runit
            F2= kel*particle.charge*gold2.charge/mag2(particle.pos-gold2.pos)*runit2
            F3= kel*particle.charge*gold3.charge/mag2(particle.pos-gold3.pos)*runit3
            F4= kel*particle.charge*gold4.charge/mag2(particle.pos-gold4.pos)*runit4
            particle.mom = particle.mom + (F+F2+F3+F4)*dt
            particle.pos = particle.pos + (particle.mom/particle.mass)*dt
            #print(particle.mom)
        #if mag(particle.pos) < 1:
        #    particle.stop = True
        if mag(particle.pos) > scale*0.7:
            particle.stop = True
            run=False
label(pos=vec(0,-0.7*scale,0),text='''Figure 2a. Simulation of Rutherford scattering with 
four randomly placed charged particles''',box=False)
def ang(cx,cy):
    #scattering angle
    if((abs(cx)==0) and (cy>0)):
        return (np.pi/2)
    elif((abs(cx)==0) and (cy<0)): 
        return (3*np.pi/2)
    elif((abs(cx)==cx) and (abs(cy)==cy)): #first
        return math.atan2(cy,cx)
    elif((abs(cx)==-cx) and (abs(cy)==cy)): #second
        return math.atan2(cy,cx)
    elif((abs(cx)==-cx) and (abs(cy)==-cy)): #third
        return 2*np.pi+math.atan2(cy,cx)
    elif((abs(cx)==cx) and (abs(cy)==-cy)):  #fourth
        return math.atan2(cy,cx)+2*np.pi
    else:
        return 0
for particle in alphas:
    vx.append(particle.mom.x)
    vy.append(particle.mom.y)
    theta.append(ang(particle.pos.x,particle.pos.y)*180/np.pi)
#print(theta)
plt.scatter(yi,theta, s=0.3)
plt.xlabel('''Impact Parameter

Figure 2b. Plot of Rutherford scattering with the setup from figure 2a. 
1800 data points are used for the plot.''')
plt.ylabel('Scattering Angle')
plt.title('Impact Parameter vs. Scattering Angle')