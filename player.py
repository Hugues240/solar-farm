import numpy as np
import os
from numpy.random import randint

class Player:

    def __init__(self):
        self.dt = 0.5
        self.efficiency=0.95
        self.sun=[]
        self.bill = np.zeros(48) # prix de vente de l'électricité
        self.load= np.zeros(48) # chargement de la batterie (li)
        self.penalty=np.zeros(48)
        self.grid_relative_load=np.zeros(48)
        self.battery_stock = np.zeros(49) #a(t)
        self.capacity = 100
        self.max_load = 70
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}

    def take_decision(self, time):

            # TO DO:
            # implement your policy here to return the load charged / discharged in the battery
            # below is a simple example
                
        #Pendant le jour on vend la moitié de ce qu'on produit et un peu de la batterie               
        if time>=12 and time<=40 and time>1 and self.grid_relative_load[time-2]<-50:
            return (-self.max_load/5)
        
        #pendant la nuit si le grid est déséquilibré on vend de la batterie    
        elif (time<=12 or time>=44) and time>1 and self.grid_relative_load[time-2]>180:
            return(-self.max_load/5)
            
        elif (time<=12 or time>=44) and time>1:
            return(self.max_load/5)
        
        #Sinon on vend ce qu'on produit plus 1/16 de nos batteries (car 16 pas de temps
        #le jour)    
        return (-self.max_load/5)
                

    def update_battery_stock(self, time,load):
            if abs(load) > self.max_load:
                load = self.max_load*np.sign(load) #saturation au maximum de la batterie
            
            new_stock = self.battery_stock[time] + (self.efficiency*max(0,load) - 1/self.efficiency * max(0,-load))*self.dt
            
            #On rétablit les conditions si le joueur ne les respecte pas :
            
            if new_stock < 0: #impossible, le min est 0, on calcule le load correspondant
                load = - self.battery_stock[time] / (self.efficiency*self.dt)
                new_stock = 0
    
            elif new_stock > self.capacity:
                load = (self.capacity - self.battery_stock[time]) / (self.efficiency*self.dt)
                new_stock = self.capacity
    
            self.battery_stock[time+1] = new_stock
            
            
            return load
        
    def compute_load(self,time,sun):
        load_player = self.take_decision(time)
        load_battery=self.update_battery_stock(time,load_player)
        self.load[time]=load_battery - sun
        
        return self.load[time]
    
    def observe(self, t, sun, price, imbalance,grid_relative_load):
        self.sun.append(sun)
        
        self.prices["purchase"].append(price["purchase"])
        self.prices["sale"].append(price["sale"])

        self.imbalance["purchase_cover"].append(imbalance["purchase_cover"])
        self.imbalance["sale_cover"].append(imbalance["sale_cover"])
        self.grid_relative_load[t]=grid_relative_load
    
    def reset(self):
        self.load= np.zeros(48)
        self.bill = np.zeros(48)
        self.penalty=np.zeros(48)
        self.grid_relative_load=np.zeros(48)
        
        last_bat = self.battery_stock[-1]
        self.battery_stock = np.zeros(49)
        self.battery_stock[0] = last_bat
        
        self.sun=[]
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}
