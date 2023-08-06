from fdtdempy.interfaces cimport IStimulatingField
from fdtdempy.interfaces cimport IDimension
from fdtdempy.interfaces cimport IStimulatedField

from fdtdempy.interfaces import IStimulatingField
from fdtdempy.interfaces import IDimension
from fdtdempy.interfaces import IStimulatedField

import math

cdef class AggregatedField(IStimulatingField):
    cdef public list CalculatedFieldList
    
    def __cinit__(self):
        self.CalculatedFieldList = []
        
    cpdef public double Get(self, int tIndex, int xIndex, int yIndex, int zIndex):
        cdef double value = 0.0

        for field in self.CalculatedFieldList:
            value += field.Get(tIndex, xIndex, yIndex, zIndex)

        return value

cdef class DipoleCurrentField(IStimulatingField):
    cdef int __c
    cdef double __courant
    cdef double __dt
    cdef double __wavelength
    cdef int __currentDirection
    cdef double __amplitude
    cdef double __dx
    cdef double __frequency

    cdef public int CenterXIndex
    cdef public int CenterYIndex
    cdef public int CenterZIndex
    cdef public int LengthIndex
    cdef public int Orientation
    
    def __cinit__(self):
        self.__c = 299792458
        self.__courant = 1 / math.sqrt(3)
        self.__dt = 0.0
        self.__wavelength = 0.0
        self.__currentDirection = 0
        self.__amplitude = 0.0
        self.__dx = 0.0
        self.__frequency = 0.0

        self.CenterXIndex = 0
        self.CenterYIndex = 0
        self.CenterZIndex = 0
        self.LengthIndex = 0
        self.Orientation = 0

    cdef int __sign(self, int x):
        return -1 if x < 0 else (1 if x > 0 else 0)

    cpdef public void SetCurrentDirection(self, int value):
        self.__currentDirection = value
        
    cpdef public void SetAmplitude(self, int value):
        self.__amplitude = value

    cpdef public void SetFrequency(self, double value):
        self.__frequency = value
        self.__wavelength = self.__c / self.__frequency

    cpdef public void SetdX(self, double value):
        self.__dx = value
        self.__dt = self.__courant * self.__dx / self.__c

    cpdef public double Get(self, int tIndex, int xIndex, int yIndex, int zIndex):
        if (self.Orientation == 0):
            if ((yIndex == self.CenterYIndex) and (zIndex == self.CenterZIndex)):
                if ((self.CenterXIndex - self.LengthIndex <= xIndex) and (xIndex <= self.CenterXIndex + self.LengthIndex)):
                    return self.__amplitude * math.cos(2 * math.pi / self.__wavelength * self.__dx * (xIndex - self.CenterXIndex) - 2 * math.pi * self.__frequency * self.__dt * tIndex * self.__sign(self.__currentDirection))
        elif (self.Orientation == 1):
            if ((xIndex == self.CenterXIndex) and (zIndex == self.CenterZIndex)):
                if ((self.CenterYIndex - self.LengthIndex <= yIndex) and (yIndex <= self.CenterYIndex + self.LengthIndex)):
                    return self.__amplitude * math.cos(2 * math.pi / self.__wavelength * self.__dx * (yIndex - self.CenterYIndex) - 2 * math.pi * self.__frequency * self.__dt * tIndex * self.__sign(self.__currentDirection))
        elif (self.Orientation == 2):
            if ((xIndex == self.CenterXIndex) and (yIndex == self.CenterYIndex)):
                if ((self.CenterZIndex - self.LengthIndex <= zIndex) and (zIndex <= self.CenterZIndex + self.LengthIndex)):
                    return self.__amplitude * math.cos(2 * math.pi / self.__wavelength * self.__dx * (zIndex - self.CenterZIndex) - 2 * math.pi * self.__frequency * self.__dt * tIndex * self.__sign(self.__currentDirection))
        else:
            return 0.0

cdef class StimulatedField(IStimulatedField):
    cdef list __currentField
    cdef list __nextField
    
    def __cinit__(self):
        self.__currentField = []
        self.__nextField = []
        self.Name = ""
        self.FilePath = ""
        self.WriteXIndexBegin = 0
        self.WriteXIndexEnd = 0
        self.WriteYIndexBegin = 0
        self.WriteYIndexEnd = 0
        self.WriteZIndexBegin = 0
        self.WriteZIndexEnd = 0

    cdef void __initNextField(self):
        if (((self.xDimension.End - self.xDimension.Begin) % self.xDimension.Step) != 0):
            raise ValueError("xDimension does not map to an array range")
        if (((self.yDimension.End - self.yDimension.Begin) % self.yDimension.Step) != 0):
            raise ValueError("yDimension does not map to an array range")
        if (((self.zDimension.End - self.zDimension.Begin) % self.zDimension.Step) != 0):
            raise ValueError("zDimension does not map to an array range")

        xSize = int((self.xDimension.End - self.xDimension.Begin) / self.xDimension.Step + 1)
        ySize = int((self.yDimension.End - self.yDimension.Begin) / self.yDimension.Step + 1)
        zSize = int((self.zDimension.End - self.zDimension.Begin) / self.zDimension.Step + 1)
        self.__nextField = [[[0.0 for z in range(zSize)] for y in range(ySize)] for x in range(xSize)]

    cpdef public void Init(self):
        if (((self.xDimension.End - self.xDimension.Begin) % self.xDimension.Step) != 0):
            raise ValueError("xDimension does not map to an array range")
        if (((self.yDimension.End - self.yDimension.Begin) % self.yDimension.Step) != 0):
            raise ValueError("yDimension does not map to an array range")
        if (((self.zDimension.End - self.zDimension.Begin) % self.zDimension.Step) != 0):
            raise ValueError("zDimension does not map to an array range")

        xSize = int((self.xDimension.End - self.xDimension.Begin) / self.xDimension.Step + 1)
        ySize = int((self.yDimension.End - self.yDimension.Begin) / self.yDimension.Step + 1)
        zSize = int((self.zDimension.End - self.zDimension.Begin) / self.zDimension.Step + 1)

        self.__currentField = [[[0.0 for z in range(zSize)] for y in range(ySize)] for x in range(xSize)]
        
        self.__initNextField()
        
        with open(self.FilePath, 'a') as output:
            output.write("t,x,y,z," + self.Name + "\n")

    cpdef public double Get(self, int xIndex, int yIndex, int zIndex):
        if (((xIndex - self.xDimension.Begin) % self.xDimension.Step) != 0):
            raise ValueError("xIndex does not map to an array index")
        if (((yIndex - self.yDimension.Begin) % self.yDimension.Step) != 0):
            raise ValueError("yIndex does not map to an array index")
        if (((zIndex - self.zDimension.Begin) % self.zDimension.Step) != 0):
            raise ValueError("zIndex does not map to an array index")

        x = int((xIndex - self.xDimension.Begin) / self.xDimension.Step)
        y = int((yIndex - self.yDimension.Begin) / self.yDimension.Step)
        z = int((zIndex - self.zDimension.Begin) / self.zDimension.Step)

        return self.__currentField[x][y][z]

    cpdef public void Set(self, int xIndex, int yIndex, int zIndex, double value):
        if (((xIndex - self.xDimension.Begin) % self.xDimension.Step) != 0):
            raise ValueError("xIndex does not map to an array index")
        if (((yIndex - self.yDimension.Begin) % self.yDimension.Step) != 0):
            raise ValueError("yIndex does not map to an array index")
        if (((zIndex - self.zDimension.Begin) % self.zDimension.Step) != 0):
            raise ValueError("zIndex does not map to an array index")

        x = int((xIndex - self.xDimension.Begin) / self.xDimension.Step)
        y = int((yIndex - self.yDimension.Begin) / self.yDimension.Step)
        z = int((zIndex - self.zDimension.Begin) / self.zDimension.Step)
            
        self.__nextField[x][y][z] = value

    cpdef public double GetNext(self, int xIndex, int yIndex, int zIndex):
        if (((xIndex - self.xDimension.Begin) % self.xDimension.Step) != 0):
            raise ValueError("xIndex does not map to an array index")
        if (((yIndex - self.yDimension.Begin) % self.yDimension.Step) != 0):
            raise ValueError("yIndex does not map to an array index")
        if (((zIndex - self.zDimension.Begin) % self.zDimension.Step) != 0):
            raise ValueError("zIndex does not map to an array index")

        x = int((xIndex - self.xDimension.Begin) / self.xDimension.Step)
        y = int((yIndex - self.yDimension.Begin) / self.yDimension.Step)
        z = int((zIndex - self.zDimension.Begin) / self.zDimension.Step)

        return self.__nextField[x][y][z]

    cpdef public void Flush(self, int t):
        for xIndex in range (self.WriteXIndexBegin, self.WriteXIndexEnd, self.xDimension.Step):
            for yIndex in range(self.WriteYIndexBegin, self.WriteYIndexEnd, self.yDimension.Step):
                for zIndex in range(self.WriteZIndexBegin, self.WriteZIndexEnd, self.zDimension.Step):
                    x = int((xIndex - self.xDimension.Begin) / self.xDimension.Step)
                    y = int((yIndex - self.yDimension.Begin) / self.yDimension.Step)
                    z = int((zIndex - self.zDimension.Begin) / self.zDimension.Step)

                    with open(self.FilePath, 'a') as output:
                        output.write(str(t) + "," + str(xIndex) + "," + str(yIndex) + "," + str(zIndex) + "," + str(self.__nextField[x][y][z]) + "\n")

        self.__currentField = self.__nextField
        self.__initNextField()

cdef class ZeroField(IStimulatingField):
    cpdef public double Get(self, int tIndex, int xIndex, int yIndex, int zIndex):
        return 0.0
