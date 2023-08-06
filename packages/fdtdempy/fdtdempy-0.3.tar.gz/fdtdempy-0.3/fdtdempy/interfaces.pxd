cdef class IStimulatingField:
    cpdef public double Get(self, int tIndex, int xIndex, int yIndex, int zIndex)

cdef class IDimension:
    cdef public int Begin
    cdef public int End
    cdef public int Step

cdef class IStimulatedField:
    cdef public str Name
    cdef public str FilePath
    cdef public IDimension xDimension
    cdef public IDimension yDimension
    cdef public IDimension zDimension
    cdef public int WriteXIndexBegin
    cdef public int WriteXIndexEnd
    cdef public int WriteYIndexBegin
    cdef public int WriteYIndexEnd
    cdef public int WriteZIndexBegin
    cdef public int WriteZIndexEnd

    cpdef public void Init(self)
    cpdef public double Get(self, int xIndex, int yIndex, int zIndex)
    cpdef public double GetNext(self, int xIndex, int yIndex, int zIndex)
    cpdef public void Set(self, int xIndex, int yIndex, int zIndex, double value)
    cpdef public void Flush(self, int t)

cdef class ISimulation:
    cdef public int TimeSteps
    cdef public IStimulatingField Jx
    cdef public IStimulatingField Jy
    cdef public IStimulatingField Jz
    cdef public IStimulatedField Ex
    cdef public IStimulatedField Ey
    cdef public IStimulatedField Ez
    cdef public IStimulatedField Hx
    cdef public IStimulatedField Hy
    cdef public IStimulatedField Hz

    cpdef public void Init(self, double dx)
    cpdef public void Run(self)