from classes.binarysearch import binarySearch
import numpy
'''
This file contains different functions that generate a list of OrbitTimePoints, which are objects whose main function is to store
various orbit parameters and calculate eclipse for any given time during the simulation. These objects are then referenced in the 
Battery class where the calculations are being made. 

'''

class OrbitTimePoint:
    # This class will represent one point in time and contain orbit information at that specific time

    def __init__(self, totalTime, orbitNumber, timeInOrbit, inSunlight: bool):
        self.totalTime = totalTime #Total time that has elapsed
        self.orbitNumber = orbitNumber #number of orbits that have passed
        self.timeInOrbit = timeInOrbit #time spent in current orbit
        self.inSunlight = inSunlight #boolean value for if the craft is in sunlight

    def __str__(self):
        return "| Total Time = " + str(self.totalTime) + " min | Orbit Number = " + str(
            self.orbitNumber) + " | Time in Current Orbit = " + str(self.timeInOrbit) + " min | In Sunlight? = " + str(
            self.inSunlight) + " |"



'''
:param list orbitAngleList: A list containing the obirt angle values
:param float orbitPeriod: Contains the length of an orbit in minutes
:param float endTime: Length of simulation
:param float eclipseLength: Length of eclipse in minutes
'''
def generateTimeListfromSunAnglesLEO(orbitAngleList:list, orbitPeriod: float, endTime: float, eclipseLength: float):
    '''
    Here, the user imports a list of orbit angles vs. sun angles per wing for one orbit. The user imports a list of orbit angles
    from 0 to 360 and assumes 180 to be noon, which is t=0. The function creates a time list based on the orbit angles for one orbit
    and then creates the OrbitTimePoints for the duration of the simulation. 
    '''

    #Instantiating lists to proper length so we can call the indices later
    orbitTimeList = [0] * len(orbitAngleList) #times corresponding to angles for one orbit
    timeStepList = [0] * len(orbitAngleList) #steps corresponding to angles for one orbit
    timePointList = [] #list we will populate with OrbitTimePoints
    currentTime = 0 
    inSun = False
    sunLength = orbitPeriod - eclipseLength

    '''
    Step 1: Generate time list correspoinding to angles starting from 180 by seeing how many minutes of the orbit one degree corresponds to
            The first function starts at the index after 180, since 0 is already populated in the list beforehand for 180. 
    '''
    index = binarySearch(orbitAngleList, 180) #Finds the index in orbitAngleList of the value closest to 180
    minsPerDegree = orbitPeriod/360

    for i in range (index+1, len(orbitAngleList)-1): #Time list for one orbit based on given angles
        delAngle = orbitAngleList[i+1]-orbitAngleList[i]
        timeStep = delAngle*minsPerDegree
        orbitTimeList[i+1] = (orbitTimeList[i]+timeStep)
        timeStepList[i+1] = (timeStep)
    '''
    Step 2: Generate the rest of the time list with the other half of the angles from 0 to 180. We need to calculate the time step from the end 
            of the list to the beginning of the list as well. 
    '''
    delAngle = 360-orbitAngleList[len(orbitAngleList)-1]
    timeStep = delAngle*minsPerDegree
    timeStepList[0] =(timeStep)
    orbitTimeList[0] = (orbitTimeList[len(orbitAngleList)-1]+timeStep)

    for i in range (0, index):
        delAngle = orbitAngleList[i+1]-orbitAngleList[i]
        timeStep = delAngle*minsPerDegree
        orbitTimeList[i+1] = (orbitTimeList[i]+timeStep)
        timeStepList[i+1] = (timeStep)

    '''
    Step 3: Generating a list of OrbitTimePoints for the length of the simulation for each orbit angle provided in the list. 
    '''
    j = 0
    orbitNumber = 1
    while currentTime <= endTime:
        orbitTime = orbitTimeList[j]
        #Starts LEO eclipse at noon
        if ((orbitTime > sunLength/2) and (orbitTime < (sunLength/2) + eclipseLength)):
            inSun = False
        else:
            inSun = True
        
        j = j+1
        if j > (len(orbitTimeList)-1): #iterates orbit if we went through one orbit time list, resets
            j = 0
            orbitNumber = orbitNumber +1
            
        timePointList.append(OrbitTimePoint(currentTime, orbitNumber, orbitTime, inSun))
        currentTime = currentTime + timeStepList[j]

    return timePointList

'''
:param list timesForSunAngles: Times at which sun angle occurs
:param float endTime: Length of simulation
:param float eclipseStart: Time eclipse starts
:param float eclipseEnd: Time eclipses ends
:param float integration step: Size of time steps
'''
def generateTimeListfromSunAnglesL1L2(timesForSunAngles:list, endTime: float, eclipseStart: float, eclipseEnd: float, integrationStep: float): #given a list of times for entire simulation duration
    '''
    The user will import a list of sun angles vs. time for the duration of the simulation. For each time in the list the user imported,
    there will be an OrbitTimePoint generated.
    '''
    
    timePointList = []
    timeRun = 0
    inSun = False

    j = 0
    while timeRun <= endTime:
        if j > (len(timesForSunAngles)-1):
            currentTime = timesForSunAngles[len(timesForSunAngles)-1] #if given sun angle timelist is shorter than simulation end time, use last given value
        else:
            currentTime = timesForSunAngles[j]
        #Starts L1/L2 eclipse at given times
        if ((currentTime > eclipseStart) and (currentTime < eclipseEnd)):
            inSun = False
        else:
            inSun = True
        
        timePointList.append(OrbitTimePoint(currentTime, 0 , 0, inSun))
        j = j+1
        timeRun = timeRun + integrationStep
    
    return timePointList


'''
:param bool isLEO: Boolean value for if the craft is in LEO
:param float endTime: Length of simulation
:param float orbitPeriod: Contains the length of an orbit in minutes
:param float eclipseLength: Length of eclipse in minutes
:param float eclipseStart: Start time of eclipse
:param float timeStep: size of time step 
'''
def generateTimeListfromConstant(isLEO: bool, endTime: float, orbitPeriod: float, eclipseLength: float, eclipseStart: float, eclipseEnd: float, timeStep: float):
    '''
    If there is no time-dependent sun angles, then we will just generate an OrbitTimePoint for each point in the constant time list. 
    The eclipse will be calculated differently based on if it is LEO or L1/L2 orbit. 
    '''
    sunLength = orbitPeriod - eclipseLength
    timeList = []
    currentTime = 0
    inSun = False

    while currentTime <= endTime:
        orbitNumber = int((currentTime / orbitPeriod) + 1)
        orbitTime = currentTime - orbitPeriod * (orbitNumber - 1) #TODO: calculate orbit time only if LEO

        if isLEO: #calculates eclipse for LEO, starts eclipse at noon
            if ((orbitTime > sunLength/2) and (orbitTime < (sunLength/2)+eclipseLength)):
                inSun = False
            else:
                inSun = True
        else: #calculates eclipse using start and end point for L1/L2
            if ((currentTime > eclipseStart) and (currentTime < eclipseEnd)):
                inSun = False
            else:
                inSun = True
        timeList.append(OrbitTimePoint(currentTime, orbitNumber, orbitTime, inSun))
        currentTime = currentTime + timeStep
    
    return timeList


'''
:param float rpm: revolutions per minute. Rotational speed of spinner spacecraft
:param int numSides: Number of sides on spinner space craft
:param float timeStep: size of time step 
:param float endTime: Length of simulation
'''

def generateSpinnerList(rpm: float, numSides: int, timeStep: float, endTime: float):
    '''
    This function generates sun angles for a spinner spacecraft. These sun angles take the place of what would be a user input sun angle list.
    The list will be for the duration of the simulation
    '''
    offsetAngle = 360/numSides
    sunAngleList = [[0] for _ in range(numSides)]

    j = 1
    for time in numpy.arange(timeStep, endTime, timeStep): #generates a list of sun angles for each side
        for side in range(numSides):
            angleIteration = (time*rpm) % 1
            sunAngleList[side].append(((angleIteration * 360) + (offsetAngle*side))%360)
        j = j+1
    return sunAngleList

