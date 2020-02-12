import simpy
import random

#Daniel Walpole 
#Project 1 Part 1
#System Simulation 
#Assignment is to make a simulation of a fast food resturant with 2 ordering window and 1 pickup window
#Lines for ordering have a total of 10 spots to include the ordering windows themselves
#The Pickup line has 7 spots to include the pickup window
#The program will find the average time of orders that are complete


MeanOrderTime = 2.0 #average time to order a meal
MeanCookTime = 5.0 #average time to cook a meal
MeanPickupTime = 2.0 #average time to pay and pickup meal
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


def Customer(env, window, name):
    global carsServed
    global timesOfService
    if(len(window.line1.queue) + len(window.line2.queue) < 8):
        if (len(window.line1.queue) <= len(window.line2.queue)):
            startTime = env.now
            order = window.line1.request()
            env.process(window.Order())
            yield order
            window.line1.release(order)
            startOrder = env.now
            cookFood = window.CookFood()
            req = window.payWindowLine.request()
            yield req
            window.payWindowLine.release(req)
            rq = window.payWindow.request()
            yield rq
            env.process(window.Pickup())
            atWindow = env.now
            if atWindow < (cookFood + startOrder):
                yield env.timeout(abs(atWindow-cookFood+startOrder))
            window.payWindow.release(rq)
            endtime = env.now
            carsServed += 1
            print('Start time for %s from line 1 {}'.format(startTime) % name)
            print('End time from line 1 {}'.format(endtime))
            timesOfService.append(endtime-startTime)
        elif(len(window.line1.queue) > len(window.line2.queue)):
            startTime = env.now
            order = window.line2.request()
            env.process(window.Order())
            yield order
            window.line2.release(order)
            startOrder = env.now
            cookFood = window.CookFood()
            req = window.payWindowLine.request()
            yield req
            window.payWindowLine.release(req)
            rq = window.payWindow.request()
            yield rq
            env.process(window.Pickup())
            atWindow = env.now
            if atWindow < (cookFood + startOrder):
                yield env.timeout(abs(atWindow-cookFood+startOrder))
                window.payWindow.release(rq)
            else:
                window.payWindow.release(rq)
            endtime = env.now
            carsServed += 1
            print('Start time for %s from line 2 {}'.format(startTime) % name)
            print('End time from line 2 {}'.format(endtime))
            timesOfService.append(endtime-startTime)
    else:
        print('Im outta here %s' % name)


def Start(env, AR):
    global cars
    global carsServed
    stuff = FastFood(env)
    while True:
        name = cars + 1
        cars += 1
        yield env.timeout(random.expovariate(1.0 / AR))
        env.process(Customer(env, stuff, name))
random.seed(123456)
env = simpy.Environment()
env.process(Start(env, AR))
env.run(until=Time)
print('%s cars seen' % cars)
print('%s cars got their food' % carsServed)
print(timesOfService)
sum = 0.0
for i in range(len(timesOfService)):
    sum += timesOfService[i]
print('The average time is %s' % (sum/len(timesOfService)))