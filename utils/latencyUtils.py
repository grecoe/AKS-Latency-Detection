
'''
    Class used to collect latency and time information of the service calls. 
'''
class LatencyTracker :
    def __init__(self):
        self.latencies = []
        self.timeStamps = []

    def getStats(self):
        # High, Low, Average, Total
        high = 0.0
        low = 100.0
        totalTime = 0.0
        total = len(self.latencies)
        for lat in self.latencies:
            totalTime += lat
            if lat > high:
                high = lat
            if lat < low:
                low = lat 
        
        averageTime = 0
        if total > 0:
            averageTime = totalTime/total 
        return total, averageTime, high, low 
    
    def getTimes(self):
        earliest = None
        latest = None
        totalTimes = len(self.timeStamps)
        for dt in self.timeStamps:
            if earliest is None:
                earliest = dt
            if latest is None:
                latest = dt

            if dt < earliest:
                earliest = dt
            if dt > latest:
                latest = dt
        
        return totalTimes, earliest, latest

