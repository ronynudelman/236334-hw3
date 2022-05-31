from dataclasses import dataclass
from math import log
from operator import concat
from random import random
from typing import List
from argparse import ArgumentParser


def getArgs():
    parser = ArgumentParser()
    parser.add_argument('totalTime', type=float)
    parser.add_argument('fIn', type=float)
    parser.add_argument('fOut', type=float)
    parser.add_argument('probs', type=float, nargs='+')
    args = parser.parse_args()
    return args


@dataclass
class Event:
    time : float
    isPrint : bool


class Simulator:
    def __init__(self,totalTime,fIn,fOut,probs):
        self.totalTime = totalTime
        self.fIn = fIn
        self.fOut = fOut
        self.probs = probs
        self.arrivalTimes = list()
        self.printTimes = list()

    def createArrivalTimes(self):
        t = 0
        while(t < self.totalTime):
            t += -log(random())/self.fIn
            self.arrivalTimes.append(Event(t,False))
        self.last_arrival_time = self.arrivalTimes[-1].time

    def createPrintTimes(self):
        t = 0.0
        for arrival_time in self.arrivalTimes:
            t += -log(random())/self.fOut
            self.printTimes.append(Event(t,True))
            while t < arrival_time.time:
                t += -log(random())/self.fOut
                self.printTimes.append(Event(t,True))

    def validate(self):
        return random() <= self.probs[len(self.buffer)]

    def run(self):
        self.createArrivalTimes()
        self.createPrintTimes()
        self.events = concat(self.arrivalTimes,self.printTimes)
        self.events : List[Event] = sorted(self.events,key = lambda x: x.time)
        self.buffer = list()
        self.buffTimes = [0]*len(self.probs)
        counterPrintedMsg = 0
        counterDeclinedMsg = 0
        t = 0.0
        totalWaitTime = 0
        totalMessageLifetimes = 0
        lastServiceTime = 0
        last_message_arrived = False
        for event in self.events:
            if event.time == self.last_arrival_time and not event.isPrint:
                last_message_arrived = True
            self.buffTimes[len(self.buffer)] += event.time - t
            t = event.time
            if event.isPrint:
                if len(self.buffer) > 0:
                    totalMessageLifetimes += t - self.buffer.pop(0)
                    if len(self.buffer) > 0:
                        totalWaitTime += t - self.buffer[0]
            else:
                if self.validate():
                    self.buffer.append(t)
                    counterPrintedMsg += 1
                else:
                    counterDeclinedMsg += 1
            if last_message_arrived and event.isPrint:
                break

        totalServiceTime = totalMessageLifetimes - totalWaitTime

        self.sumBuffTimes = sum(self.buffTimes)
        self.Ti = ' '.join([str(t) for t in self.buffTimes])
        self.Zi = ' '.join([str(i/sum(self.buffTimes)) for i in self.buffTimes])

        print(counterPrintedMsg,
              counterDeclinedMsg,
              self.sumBuffTimes,
              self.Ti,
              self.Zi,
              totalWaitTime/counterPrintedMsg,
              totalServiceTime/counterPrintedMsg,
              counterPrintedMsg/t)


if __name__ == "__main__":
    args = getArgs()
    s = Simulator(args.totalTime, args.fIn, args.fOut, args.probs)
    s.run()
