# automatically generated by the FlatBuffers compiler, do not modify

# namespace: proto

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Yield(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Yield()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsYield(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Yield
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Yield
    def Request(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, o + self._tab.Pos)
        return 0

    # Yield
    def Payload(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # Yield
    def PayloadAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint8Flags, o)
        return 0

    # Yield
    def PayloadLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Yield
    def PayloadIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

    # Yield
    def EncAlgo(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Yield
    def EncSerializer(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Yield
    def EncKey(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 1))
        return 0

    # Yield
    def EncKeyAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Uint8Flags, o)
        return 0

    # Yield
    def EncKeyLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Yield
    def EncKeyIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        return o == 0

    # Yield
    def Progress(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return bool(self._tab.Get(flatbuffers.number_types.BoolFlags, o + self._tab.Pos))
        return False

    # Yield
    def Callee(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, o + self._tab.Pos)
        return 0

    # Yield
    def CalleeAuthid(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(18))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Yield
    def CalleeAuthrole(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(20))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # Yield
    def ForwardFor(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 8
            from wamp.proto.Principal import Principal
            obj = Principal()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # Yield
    def ForwardForLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # Yield
    def ForwardForIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(22))
        return o == 0

def Start(builder): builder.StartObject(10)
def YieldStart(builder):
    """This method is deprecated. Please switch to Start."""
    return Start(builder)
def AddRequest(builder, request): builder.PrependUint64Slot(0, request, 0)
def YieldAddRequest(builder, request):
    """This method is deprecated. Please switch to AddRequest."""
    return AddRequest(builder, request)
def AddPayload(builder, payload): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(payload), 0)
def YieldAddPayload(builder, payload):
    """This method is deprecated. Please switch to AddPayload."""
    return AddPayload(builder, payload)
def StartPayloadVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def YieldStartPayloadVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartPayloadVector(builder, numElems)
def AddEncAlgo(builder, encAlgo): builder.PrependUint8Slot(2, encAlgo, 0)
def YieldAddEncAlgo(builder, encAlgo):
    """This method is deprecated. Please switch to AddEncAlgo."""
    return AddEncAlgo(builder, encAlgo)
def AddEncSerializer(builder, encSerializer): builder.PrependUint8Slot(3, encSerializer, 0)
def YieldAddEncSerializer(builder, encSerializer):
    """This method is deprecated. Please switch to AddEncSerializer."""
    return AddEncSerializer(builder, encSerializer)
def AddEncKey(builder, encKey): builder.PrependUOffsetTRelativeSlot(4, flatbuffers.number_types.UOffsetTFlags.py_type(encKey), 0)
def YieldAddEncKey(builder, encKey):
    """This method is deprecated. Please switch to AddEncKey."""
    return AddEncKey(builder, encKey)
def StartEncKeyVector(builder, numElems): return builder.StartVector(1, numElems, 1)
def YieldStartEncKeyVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartEncKeyVector(builder, numElems)
def AddProgress(builder, progress): builder.PrependBoolSlot(5, progress, 0)
def YieldAddProgress(builder, progress):
    """This method is deprecated. Please switch to AddProgress."""
    return AddProgress(builder, progress)
def AddCallee(builder, callee): builder.PrependUint64Slot(6, callee, 0)
def YieldAddCallee(builder, callee):
    """This method is deprecated. Please switch to AddCallee."""
    return AddCallee(builder, callee)
def AddCalleeAuthid(builder, calleeAuthid): builder.PrependUOffsetTRelativeSlot(7, flatbuffers.number_types.UOffsetTFlags.py_type(calleeAuthid), 0)
def YieldAddCalleeAuthid(builder, calleeAuthid):
    """This method is deprecated. Please switch to AddCalleeAuthid."""
    return AddCalleeAuthid(builder, calleeAuthid)
def AddCalleeAuthrole(builder, calleeAuthrole): builder.PrependUOffsetTRelativeSlot(8, flatbuffers.number_types.UOffsetTFlags.py_type(calleeAuthrole), 0)
def YieldAddCalleeAuthrole(builder, calleeAuthrole):
    """This method is deprecated. Please switch to AddCalleeAuthrole."""
    return AddCalleeAuthrole(builder, calleeAuthrole)
def AddForwardFor(builder, forwardFor): builder.PrependUOffsetTRelativeSlot(9, flatbuffers.number_types.UOffsetTFlags.py_type(forwardFor), 0)
def YieldAddForwardFor(builder, forwardFor):
    """This method is deprecated. Please switch to AddForwardFor."""
    return AddForwardFor(builder, forwardFor)
def StartForwardForVector(builder, numElems): return builder.StartVector(8, numElems, 8)
def YieldStartForwardForVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartForwardForVector(builder, numElems)
def End(builder): return builder.EndObject()
def YieldEnd(builder):
    """This method is deprecated. Please switch to End."""
    return End(builder)