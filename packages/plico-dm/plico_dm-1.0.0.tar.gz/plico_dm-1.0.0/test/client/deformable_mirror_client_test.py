#!/usr/bin/env python
import unittest
import numpy as np
from plico.utils.decorator import override
from plico.rpc.dummy_remote_procedure_call import DummyRpcHandler
from plico.rpc.dummy_sockets import DummySockets
from plico_dm.client.deformable_mirror_client import DeformableMirrorClient
from plico_dm.utils.timeout import Timeout
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus


class TesterRpcHandler(DummyRpcHandler):

    def __init__(self):
        self._sendRequestHistory = []
        self._receivePickableHistory = []
        self._sendRequestCounter = 0
        self._receivePickableCounter = 0

    @override
    def sendRequest(self, socket, command, args, timeout=1):
        self._sendRequestHistory.append(
            (socket, command, args, timeout))
        self._sendRequestCounter += 1

    @override
    def receivePickable(self, socket, timeout=1):
        self._receivePickableCounter += 1
        self._receivePickableHistory.append(
            (socket, timeout))
        return self._objToReturnWithReceivePickable

    def getLastSendRequestArguments(self):
        return self._sendRequestHistory[-1]

    def getLastReceivePickableArguments(self):
        return self._receivePickableHistory[-1]

    def wantsPickable(self, objToReturnWithReceivePickable):
        self._objToReturnWithReceivePickable = \
            objToReturnWithReceivePickable


class MyRpcHandler(TesterRpcHandler):
    pass


class MySockets(DummySockets):
    pass


class DeformableMirrorClientTest(unittest.TestCase):

    def setUp(self):
        self._rpc = MyRpcHandler()
        self._sockets = MySockets()
        self._client = DeformableMirrorClient(self._rpc, self._sockets)

    def tearDown(self):
        pass

    def testSetShape(self):
        mirrorWantedShape = np.identity(4)
        self._client.set_shape(mirrorWantedShape)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'setShape',
             [mirrorWantedShape],
             Timeout.MIRROR_SET_SHAPE))

    def testGetPosition(self):
        timeoutInSec = 12
        _ = self._client.get_shape(timeoutInSec)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'getShape',
             [],
             timeoutInSec))

    def testGetStatus(self):
        wantedInstrumentStatus = DeformableMirrorStatus(
            12, 34, 123, 'cmdtag')
        self._rpc.wantsPickable(wantedInstrumentStatus)

        timeoutInSec = 22
        gotInstrumentStatus = self._client.get_status(timeoutInSec)
        self.assertEqual(
            wantedInstrumentStatus, gotInstrumentStatus)

        self.assertEqual(
            self._rpc.getLastReceivePickableArguments(),
            (self._sockets.serverStatus(),
             timeoutInSec))

    def testSaveCurrentCommandAsReference(self):
        timeoutInSec = 12
        tag = 'asdf'
        self._client.save_current_shape_as_reference(
            tag, timeoutInSec=timeoutInSec)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'save_current_shape_as_reference',
             [tag],
             timeoutInSec))

    def testLoadReference(self):
        timeoutInSec = 12
        tag = 'assss'
        self._client.load_reference(
            tag, timeoutInSec=timeoutInSec)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'load_reference',
             [tag],
             timeoutInSec))

    def testGetReferenceCommand(self):
        timeoutInSec = 12
        _ = self._client.get_reference_shape(
            timeoutInSec=timeoutInSec)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'get_reference_shape',
             [],
             timeoutInSec))

    def testGetReferenceCommandTag(self):
        wantedInstrumentStatus = DeformableMirrorStatus(
            12, 34,  22, 'cmdtag')
        self._rpc.wantsPickable(wantedInstrumentStatus)

        timeoutInSec = 314
        cmdtag = self._client.get_reference_shape_tag(
            timeoutInSec=timeoutInSec)
        self.assertEqual(cmdtag, 'cmdtag')
        self.assertEqual(
            self._rpc.getLastReceivePickableArguments(),
            (self._sockets.serverStatus(),
             timeoutInSec))

    def testGetNumberOfActuators(self):
        nact = 12
        wantedInstrumentStatus = DeformableMirrorStatus(
            nact, 34,  22, 'cmdtag')
        self._rpc.wantsPickable(wantedInstrumentStatus)

        timeoutInSec = 314
        gotnact = self._client.get_number_of_actuators(
            timeoutInSec=timeoutInSec)
        self.assertEqual(gotnact, nact)
        self.assertEqual(
            self._rpc.getLastReceivePickableArguments(),
            (self._sockets.serverStatus(),
             timeoutInSec))

    def testGetNumberOfModes(self):
        nmodes = 11
        wantedInstrumentStatus = DeformableMirrorStatus(
            231, nmodes,  22, 'cmdtag')
        self._rpc.wantsPickable(wantedInstrumentStatus)

        timeoutInSec = 314
        gotnmodes = self._client.get_number_of_modes(
            timeoutInSec=timeoutInSec)
        self.assertEqual(gotnmodes, nmodes)
        self.assertEqual(
            self._rpc.getLastReceivePickableArguments(),
            (self._sockets.serverStatus(),
             timeoutInSec))


if __name__ == "__main__":
    unittest.main()
