from fdtdempy.interfaces cimport IDimension
from fdtdempy.interfaces cimport ISimulation
from fdtdempy.interfaces cimport IStimulatingField
from fdtdempy.interfaces cimport IStimulatedField

from fdtdempy.interfaces import IDimension
from fdtdempy.interfaces import ISimulation
from fdtdempy.interfaces import IStimulatingField
from fdtdempy.interfaces import IStimulatedField

import math
import time

cdef class Dimension(IDimension):
    def __cinit__(self):
        self.Begin = 0
        self.End = 0
        self.Step = 0

cdef class Simulation(ISimulation):
    cdef double __impedance
    cdef double __ur
    cdef double __er
    cdef double __courant
    cdef double __abcCoef
    cdef double __magCoef
    cdef double __elecCoef
    cdef double __currCoef

    def __cinit__(self):
        self.TimeSteps = 0
        self.__impedance = 376.730313668
        self.__ur = 1.0
        self.__er = 1.0
        self.__courant = 1 / math.sqrt(3)
        self.__abcCoef = 0.0
        self.__magCoef = 0.0
        self.__elecCoef = 0.0
        self.__currCoef = 0.0

    cdef void __calculateHx(self):
        cdef double nextHx
        for xIndex in range(self.Hx.xDimension.Begin, self.Hx.xDimension.End + self.Hx.xDimension.Step, self.Hx.xDimension.Step):
            for yIndex in range(self.Hx.yDimension.Begin, self.Hx.yDimension.End + self.Hx.yDimension.Step, self.Hx.yDimension.Step):
                for zIndex in range(self.Hx.zDimension.Begin, self.Hx.zDimension.End + self.Hx.zDimension.Step, self.Hx.zDimension.Step):
                    nextHx = self.Hx.Get(xIndex, yIndex, zIndex) - self.__magCoef * ((self.Ez.Get(xIndex, yIndex + 1, zIndex) - self.Ez.Get(xIndex, yIndex - 1, zIndex)) - (self.Ey.Get(xIndex, yIndex, zIndex + 1) - self.Ey.Get(xIndex, yIndex, zIndex - 1)))
                    self.Hx.Set(xIndex, yIndex, zIndex, nextHx)

    cdef void __calculateHy(self):
        cdef double nextHy
        for xIndex in range(self.Hy.xDimension.Begin, self.Hy.xDimension.End + self.Hy.xDimension.Step, self.Hy.xDimension.Step):
            for yIndex in range(self.Hy.yDimension.Begin, self.Hy.yDimension.End + self.Hy.yDimension.Step, self.Hy.yDimension.Step):
                for zIndex in range(self.Hy.zDimension.Begin, self.Hy.zDimension.End + self.Hy.zDimension.Step, self.Hy.zDimension.Step):
                    nextHy = self.Hy.Get(xIndex, yIndex, zIndex) - self.__magCoef * ((self.Ex.Get(xIndex, yIndex, zIndex + 1) - self.Ex.Get(xIndex, yIndex, zIndex - 1)) - (self.Ez.Get(xIndex + 1, yIndex, zIndex) - self.Ez.Get(xIndex - 1, yIndex, zIndex)))
                    self.Hy.Set(xIndex, yIndex, zIndex, nextHy)

    cdef void __calculateHz(self):
        cdef double nextHz
        for xIndex in range (self.Hz.xDimension.Begin, self.Hz.xDimension.End + self.Hz.xDimension.Step, self.Hz.xDimension.Step):
            for yIndex in range (self.Hz.yDimension.Begin, self.Hz.yDimension.End + self.Hz.yDimension.Step, self.Hz.yDimension.Step):
                for zIndex in range (self.Hz.zDimension.Begin, self.Hz.zDimension.End + self.Hz.zDimension.Step, self.Hz.zDimension.Step):
                    nextHz = self.Hz.Get(xIndex, yIndex, zIndex) - self.__magCoef * ((self.Ey.Get(xIndex + 1, yIndex, zIndex) - self.Ey.Get(xIndex - 1, yIndex, zIndex)) - (self.Ex.Get(xIndex, yIndex + 1, zIndex) - self.Ex.Get(xIndex, yIndex - 1, zIndex)))
                    self.Hz.Set(xIndex, yIndex, zIndex, nextHz)

    cdef void __calculateH(self):
        self.__calculateHx()
        self.__calculateHy()
        self.__calculateHz()

    cdef void __flushH(self, int tIndex):
        self.Hx.Flush(tIndex)
        self.Hy.Flush(tIndex)
        self.Hz.Flush(tIndex)

    cdef void __calculateEx(self, int tIndex):
        cdef double nextEx
        for xIndex in range(self.Ex.xDimension.Begin + self.Ex.xDimension.Step, self.Ex.xDimension.End, self.Ex.xDimension.Step):
            for yIndex in range(self.Ex.yDimension.Begin + self.Ex.yDimension.Step, self.Ex.yDimension.End, self.Ex.yDimension.Step):
                for zIndex in range(self.Ex.zDimension.Begin + self.Ex.yDimension.Step, self.Ex.zDimension.End, self.Ex.zDimension.Step):
                    nextEx = self.Ex.Get(xIndex, yIndex, zIndex) - self.__currCoef * self.Jx.Get(tIndex, xIndex, yIndex, zIndex) + self.__elecCoef * ((self.Hz.Get(xIndex, yIndex + 1, zIndex) - self.Hz.Get(xIndex, yIndex - 1, zIndex)) - (self.Hy.Get(xIndex, yIndex, zIndex + 1) - self.Hy.Get(xIndex, yIndex, zIndex - 1)))
                    self.Ex.Set(xIndex, yIndex, zIndex, nextEx)

    cdef void __calculateEy(self, int tIndex):
        cdef double nextEy
        for xIndex in range(self.Ey.xDimension.Begin + self.Ey.xDimension.Step, self.Ey.xDimension.End, self.Ey.xDimension.Step):
            for yIndex in range(self.Ey.yDimension.Begin + self.Ey.yDimension.Step, self.Ey.yDimension.End, self.Ey.yDimension.Step):
                for zIndex in range(self.Ey.zDimension.Begin + self.Ey.zDimension.Step, self.Ey.zDimension.End, self.Ey.zDimension.Step):
                    nextEy = self.Ey.Get(xIndex, yIndex, zIndex) - self.__currCoef * self.Jy.Get(tIndex, xIndex, yIndex, zIndex) + self.__elecCoef * ((self.Hx.Get(xIndex, yIndex, zIndex + 1) - self.Hx.Get(xIndex, yIndex, zIndex - 1)) - (self.Hz.Get(xIndex + 1, yIndex, zIndex) - self.Hz.Get(xIndex - 1, yIndex, zIndex)))
                    self.Ey.Set(xIndex, yIndex, zIndex, nextEy)

    cdef void __calculateEz(self, int tIndex):
        cdef double nextEz
        for xIndex in range(self.Ez.xDimension.Begin + self.Ez.xDimension.Step, self.Ez.xDimension.End, self.Ez.xDimension.Step):
            for yIndex in range(self.Ez.yDimension.Begin + self.Ez.yDimension.Step, self.Ez.yDimension.End, self.Ez.yDimension.Step):
                for zIndex in range(self.Ez.zDimension.Begin + self.Ez.zDimension.Step, self.Ez.zDimension.End, self.Ez.zDimension.Step):
                    nextEz = self.Ez.Get(xIndex, yIndex, zIndex) - self.__currCoef * self.Jz.Get(tIndex, xIndex, yIndex, zIndex) + self.__elecCoef * ((self.Hy.Get(xIndex + 1, yIndex, zIndex) - self.Hy.Get(xIndex - 1, yIndex, zIndex)) - (self.Hx.Get(xIndex, yIndex + 1, zIndex) - self.Hx.Get(xIndex, yIndex - 1, zIndex)))
                    self.Ez.Set(xIndex, yIndex, zIndex, nextEz)

    cdef void __calculateE(self, int tIndex):
        self.__calculateEx(tIndex)
        self.__calculateEy(tIndex)
        self.__calculateEz(tIndex)

    cdef void __flushE(self, int tIndex):
        self.Ex.Flush(tIndex)
        self.Ey.Flush(tIndex)
        self.Ez.Flush(tIndex)

    cdef void __calculateEyOnXsideAbc(self):
        cdef double nextEy
        for yIndex in range(self.Ey.yDimension.Begin + self.Ey.yDimension.Step, self.Ey.yDimension.End, self.Ey.yDimension.Step):
            for zIndex in range(self.Ey.zDimension.Begin + self.Ey.zDimension.Step, self.Ey.zDimension.End, self.Ey.zDimension.Step):
                nextEy = self.Ey.Get(self.Ey.xDimension.Begin + self.Ey.xDimension.Step, yIndex, zIndex) + self.__abcCoef * (self.Ey.GetNext(self.Ey.xDimension.Begin + self.Ey.xDimension.Step, yIndex, zIndex) - self.Ey.Get(self.Ey.xDimension.Begin, yIndex, zIndex))
                self.Ey.Set(self.Ey.xDimension.Begin, yIndex, zIndex, nextEy)
                nextEy = self.Ey.Get(self.Ey.xDimension.End - self.Ey.xDimension.Step, yIndex, zIndex) + self.__abcCoef * (self.Ey.GetNext(self.Ey.xDimension.End - self.Ey.xDimension.Step, yIndex, zIndex) - self.Ey.Get(self.Ey.xDimension.End, yIndex, zIndex))
                self.Ey.Set(self.Ey.xDimension.End, yIndex, zIndex, nextEy)

    cdef void __calculateEzOnXsideAbc(self):
        cdef double nextEz
        for yIndex in range(self.Ez.yDimension.Begin + self.Ez.yDimension.Step, self.Ez.yDimension.End, self.Ez.yDimension.Step):
            for zIndex in range(self.Ez.zDimension.Begin + self.Ez.zDimension.Step, self.Ez.zDimension.End, self.Ez.zDimension.Step):
                nextEz = self.Ez.Get(self.Ez.xDimension.Begin + self.Ez.xDimension.Step, yIndex, zIndex) + self.__abcCoef * (self.Ez.GetNext(self.Ez.xDimension.Begin + self.Ez.xDimension.Step, yIndex, zIndex) - self.Ez.Get(self.Ez.xDimension.Begin, yIndex, zIndex))
                self.Ez.Set(self.Ez.xDimension.Begin, yIndex, zIndex, nextEz)
                nextEz = self.Ez.Get(self.Ez.xDimension.End - self.Ez.xDimension.Step, yIndex, zIndex) + self.__abcCoef * (self.Ez.GetNext(self.Ez.xDimension.End - self.Ez.xDimension.Step, yIndex, zIndex) - self.Ez.Get(self.Ez.xDimension.End, yIndex, zIndex))
                self.Ez.Set(self.Ez.xDimension.End, yIndex, zIndex, nextEz)

    cdef void __calculateExOnYsideAbc(self):
        cdef double nextEx
        for xIndex in range(self.Ex.xDimension.Begin + self.Ex.xDimension.Step, self.Ex.xDimension.End, self.Ex.xDimension.Step):
            for zIndex in range(self.Ex.zDimension.Begin + self.Ex.zDimension.Step, self.Ex.zDimension.End, self.Ex.zDimension.Step):
                nextEx = self.Ex.Get(xIndex, self.Ex.yDimension.Begin + self.Ex.yDimension.Step, zIndex) + self.__abcCoef * (self.Ex.GetNext(xIndex, self.Ex.yDimension.Begin + self.Ex.yDimension.Step, zIndex) - self.Ex.Get(xIndex, self.Ex.yDimension.Begin, zIndex))
                self.Ex.Set(xIndex, self.Ex.yDimension.Begin, zIndex, nextEx)
                nextEx = self.Ex.Get(xIndex, self.Ex.yDimension.End - self.Ex.yDimension.Step, zIndex) + self.__abcCoef * (self.Ex.GetNext(xIndex, self.Ex.yDimension.End - self.Ex.yDimension.Step, zIndex) - self.Ex.Get(xIndex, self.Ex.yDimension.End, zIndex))
                self.Ex.Set(xIndex, self.Ex.yDimension.End, zIndex, nextEx)

    cdef void __calculateEzOnYsideAbc(self):
        cdef double nextEz
        for xIndex in range(self.Ez.xDimension.Begin + self.Ez.xDimension.Step, self.Ez.xDimension.End, self.Ez.xDimension.Step):
            for zIndex in range(self.Ez.zDimension.Begin + self.Ez.zDimension.Step, self.Ez.zDimension.End, self.Ez.zDimension.Step):
                nextEz = self.Ez.Get(xIndex, self.Ez.yDimension.Begin + self.Ez.yDimension.Step, zIndex) + self.__abcCoef * (self.Ez.GetNext(xIndex, self.Ez.yDimension.Begin + self.Ez.yDimension.Step, zIndex) - self.Ez.Get(xIndex, self.Ez.yDimension.Begin, zIndex))
                self.Ez.Set(xIndex, self.Ez.yDimension.Begin, zIndex, nextEz)
                nextEz = self.Ez.Get(xIndex, self.Ez.yDimension.End - self.Ez.yDimension.Step, zIndex) + self.__abcCoef * (self.Ez.GetNext(xIndex, self.Ez.yDimension.End - self.Ez.yDimension.Step, zIndex) - self.Ez.Get(xIndex, self.Ez.yDimension.End, zIndex))
                self.Ez.Set(xIndex, self.Ez.yDimension.End, zIndex, nextEz)

    cdef void __calculateExOnZsideAbc(self):
        cdef double nextEx
        for xIndex in range(self.Ex.xDimension.Begin + self.Ex.xDimension.Step, self.Ex.xDimension.End, self.Ex.xDimension.Step):
            for yIndex in range(self.Ex.yDimension.Begin + self.Ex.yDimension.Step, self.Ex.yDimension.End, self.Ex.yDimension.Step):
                nextEx = self.Ex.Get(xIndex, yIndex, self.Ex.zDimension.Begin + self.Ex.zDimension.Step) + self.__abcCoef * (self.Ex.GetNext(xIndex, yIndex, self.Ex.zDimension.Begin + self.Ex.zDimension.Step) - self.Ex.Get(xIndex, yIndex, self.Ex.zDimension.Begin))
                self.Ex.Set(xIndex, yIndex, self.Ex.zDimension.Begin, nextEx)
                nextEx = self.Ex.Get(xIndex, yIndex, self.Ex.zDimension.End - self.Ex.zDimension.Step) + self.__abcCoef * (self.Ex.GetNext(xIndex, yIndex, self.Ex.zDimension.End - self.Ex.zDimension.Step) - self.Ex.Get(xIndex, yIndex, self.Ex.zDimension.End))
                self.Ex.Set(xIndex, yIndex, self.Ex.zDimension.End, nextEx)

    cdef void __calculateEyOnZsideAbc(self):
        cdef double nextEy
        for xIndex in range(self.Ey.xDimension.Begin + self.Ey.xDimension.Step, self.Ey.xDimension.End, self.Ey.xDimension.Step):
            for yIndex in range(self.Ey.yDimension.Begin + self.Ey.yDimension.Step, self.Ey.yDimension.End, self.Ey.yDimension.Step):
                nextEy = self.Ey.Get(xIndex, yIndex, self.Ey.zDimension.Begin + self.Ey.zDimension.Step) + self.__abcCoef * (self.Ey.GetNext(xIndex, yIndex, self.Ey.zDimension.Begin + self.Ey.zDimension.Step) - self.Ey.Get(xIndex, yIndex, self.Ey.zDimension.Begin))
                self.Ey.Set(xIndex, yIndex, self.Ey.zDimension.Begin, nextEy)
                nextEy = self.Ey.Get(xIndex, yIndex, self.Ey.zDimension.End - self.Ey.zDimension.Step) + self.__abcCoef * (self.Ey.GetNext(xIndex, yIndex, self.Ey.zDimension.End - self.Ey.zDimension.Step) - self.Ey.Get(xIndex, yIndex, self.Ey.zDimension.End))
                self.Ey.Set(xIndex, yIndex, self.Ey.zDimension.End, nextEy)

    cdef void __calculateXsideAbc(self):
        self.__calculateEyOnXsideAbc()
        self.__calculateEzOnXsideAbc()

    cdef void __calculateYsideAbc(self):
        self.__calculateExOnYsideAbc()
        self.__calculateEzOnYsideAbc()

    cdef void __calculateZsideAbc(self):
        self.__calculateExOnZsideAbc()
        self.__calculateEyOnZsideAbc()

    cdef void __calculateAbc(self):
        self.__calculateXsideAbc()
        self.__calculateYsideAbc()
        self.__calculateZsideAbc()

    cpdef public void Init(self, double dx):
        self.__abcCoef = (self.__courant / math.sqrt(self.__ur * self.__er) - 1) / (self.__courant / math.sqrt(self.__ur * self.__er) + 1)
        self.__magCoef = self.__courant / self.__ur / self.__impedance
        self.__elecCoef = self.__courant * self.__impedance / self.__er
        self.__currCoef = self.__elecCoef * dx

    cpdef public void Run(self):
        cdef double tic
        cdef double toc
        cdef double totalSeconds
        cdef double totalMinutes

        for tIndex in range(0, self.TimeSteps):
            print("Begin step", tIndex, "of", self.TimeSteps, "steps")
            tic = time.process_time()

            self.__calculateH()

            self.__flushH(tIndex)

            self.__calculateE(tIndex)

            self.__calculateAbc()

            self.__flushE(tIndex)

            toc = time.process_time()
            print("End step", tIndex, "of", self.TimeSteps, "steps")
            totalSeconds = toc - tic
            totalMinutes = totalSeconds / 60;
            print("Seconds taken on step:", totalSeconds)
            print("Minutes left in run:", (self.TimeSteps - tIndex - 1) * totalMinutes)
