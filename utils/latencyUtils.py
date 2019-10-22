
class RequestData :
    def __init__(self):
        self.latency = 0.0
        self.time = None
        self.requestId = ''

'''
    Class used to collect latency and time information of the service calls. 
'''
class LatencyTracker :
    def __init__(self):
        self.requestInfo = []

    def findByRequestId(self, requestId):
        return [x for x in self.requestInfo if x.requestId == requestId] 

    def getPrintableFormat(self, fileName):
        results = []
        total, avg, high, low = self.getStats()
        totalTimes, first, last = self.getTimes()
        elapsedTime = ((last - first).total_seconds()) / 60
    
        results.append("{}File : {}".format('\n', fileName))
        results.append("Times ({}):".format(totalTimes))
        results.append("\t Earliest: {}".format(first))
        results.append("\t Latest: {}".format(last))
        results.append("\t Time in minutes: {}".format(elapsedTime))

        results.append("Scoring Calls ({}):".format(total))
        results.append("\t Average: {} ms".format(avg))
        results.append("\t Slowest: {} ms".format(high))
        results.append("\t Fastest: {} ms".format(low))
        results.append("\t Throughput: {} RPS".format(total / (elapsedTime *60)))

        return results

    def getStats(self):
        latencies = [x.latency for x in self.requestInfo]

        # High, Low, Average, Total
        high = 0.0
        low = 100.0
        totalTime = 0.0
        total = len(latencies)
        for lat in latencies:
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
        recordedTimes = [x.time for x in self.requestInfo]
        earliest = None
        latest = None
        totalTimes = len(recordedTimes)
        for dt in recordedTimes:
            if earliest is None:
                earliest = dt
            if latest is None:
                latest = dt

            if dt < earliest:
                earliest = dt
            if dt > latest:
                latest = dt
        
        return totalTimes, earliest, latest

