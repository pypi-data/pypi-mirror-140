cdef class IStimulatingField:
    cpdef public double Get(self, int tIndex, int xIndex, int yIndex, int zIndex):
        pass

cdef class IDimension:
    pass

cdef class IStimulatedField:
    cpdef public void Init(self):
        pass
    
    cpdef public double Get(self, int xIndex, int yIndex, int zIndex):
        pass

    cpdef public double GetNext(self, int xIndex, int yIndex, int zIndex):
        pass
    
    cpdef public void Set(self, int xIndex, int yIndex, int zIndex, double value):
        pass
    
    cpdef public void Flush(self, int t):
        pass

cdef class ISimulation:
    cpdef public void Init(self, double dx):
        pass

    cpdef public void Run(self):
        pass