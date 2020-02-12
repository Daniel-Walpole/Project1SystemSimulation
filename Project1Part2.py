import simpy
import random

#Daniel Walpole 
#Project 1 Part 1
#System Simulation 
#Assignment is to make a simulation of a fast food resturant with 2 ordering window and 1 pickup window
#Lines for ordering have a total of 10 spots to include the ordering windows themselves
#The Pickup line has 7 spots to include the pickup window
#The program will find the average time of orders that are complete


MeanOrderTime = 1.5 #average time to order a meal
MeanCookTime = 5.0 #average time to cook a meal
MeanPickupTime = 1.0 #average time to pay and pickup meal
AR = 1 #how often a car should arive
Time = 120 #how long simulation should run
cars = 0 #total number of cars generated
carsServed = 0 #total number of cars that got food
timesOfService = [] #list of all times of completed orders

#this class is a representation of the restrant 
class FastFood(object):

    #initalize the object with the enviorment as variable
    #sets all resources with 2 orderstaions 1 pickup window and the line for between the two
    def __init__(self, env):
        self.env = env
        self.line1 = simpy.Resource(env, 1)
        self.line2 = simpy.Resource(env, 1)
        self.payWindowLine = simpy.Resource(env, 6)
        self.payWindow = simpy.Resource(env, 1)

    #function to wait a randomly distributed amount of time relative to the order time
    def Order(self):
        yield self.env.timeout(random.expovariate(1.0 / MeanOrderTime))
    
    #function to wait a randomly distributed amount of time relative to pickup time
    def Pickup(self):
        yield self.env.timeout(random.expovariate(1.0 / MeanPickupTime))

    #function that returns a value of time to represent cooking the meal
    def CookFood(self):
        return random.expovariate(1.0 / MeanCookTime)

#function to have a customer go through line 
def Customer(env, window, name):
    #to use global variables use this define
    global carsServed
    global timesOfService
    #if line 1 is shorter than line 2 go through line 1 
    if (len(window.line1.queue) <= len(window.line2.queue)):
        #keeping track of start time 
        startTime = env.now
        #ensuring the length of the queue is shorter than 4
        if(len(window.line1.queue) < 4):
            #getting to order window and ordering
            order = window.line1.request()
            yield order
            env.process(window.Order())
            window.line1.release(order)
            #getting times for food cook
            startOrder = env.now
            cookFood = window.CookFood()
            #getting in line to pay
            req = window.payWindowLine.request()
            yield req
            window.payWindowLine.release(req)
            #getting to window to pay
            rq = window.payWindow.request()
            yield rq
            env.process(window.Pickup())
            atWindow = env.now
            #can only leave if food was cooked 
            if atWindow < (cookFood + startOrder):
                yield env.timeout(abs(atWindow-cookFood+startOrder))
            window.payWindow.release(rq)
            endtime = env.now
            carsServed += 1
            #outputing start and end times
            print('Start time for %s from line 1 {}'.format(startTime) % name)
            print('End time from line 1 {}'.format(endtime))
            #adding completed time to list
            timesOfService.append(endtime-startTime)
        else:
            #if the queue is to long they leave
            print('Im outta here %s' % name)
    #if line 1 has more people in it go to line 2
    elif(len(window.line1.queue) > len(window.line2.queue)):
        #keeping track of start time 
        startTime = env.now
        #ensuring the length of the queue is shorter than 4
        if(len(window.line2.queue) < 4):
            #getting to order window and ordering
            order = window.line2.request()
            yield order
            env.process(window.Order())
            window.line2.release(order)
            #getting times for food cook
            startOrder = env.now
            cookFood = window.CookFood()
            #getting in line to pay
            req = window.payWindowLine.request()
            yield req
            window.payWindowLine.release(req)
            #getting to window to pay
            rq = window.payWindow.request()
            yield rq
            env.process(window.Pickup())
            atWindow = env.now
            #can only leave if food was cooked 
            if atWindow < (cookFood + startOrder):
                yield env.timeout(abs(atWindow-cookFood+startOrder))
            window.payWindow.release(rq)
            endtime = env.now
            carsServed += 1
            #outputing start and end times
            print('Start time for %s from line 2 {}'.format(startTime) % name)
            print('End time from line 2 {}'.format(endtime))
            #adding completed time to list
            timesOfService.append(endtime-startTime)
        else:
            #if the queue is to long they leave
            print('Im outta here %s' % name)

#function to start the whole simulation
def Start(env, AR):
    #for use of global variables 
    global cars
    global carsServed
    #making the resturant
    stuff = FastFood(env)
    #run until out of time
    while True:
        #nameing cars and adding to total cars in simulation
        name = cars + 1
        cars += 1
        #passing time for cars randomly spawn
        yield env.timeout(random.expovariate(1.0 / AR))
        #having them go and attempt to order food
        env.process(Customer(env, stuff, name))

#setting random seed can be changed 
random.seed(123456)
#declaring and starting the simulation with calls
env = simpy.Environment()
env.process(Start(env, AR))
#setting simulation to end after set amount of time
env.run(until=Time)

#printing useful information 
print('%s cars seen' % cars)
print('%s cars got their food' % carsServed)
print(timesOfService)
#getting mean time of cars who were served
sum = 0.0
for i in range(len(timesOfService)):
    sum += timesOfService[i]
print('The average time is %s' % (sum/len(timesOfService)))