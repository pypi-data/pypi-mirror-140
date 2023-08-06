#!/usr/bin/env python

from plico.client.hackerable_client import HackerableClient
from plico_dm.client.abstract_deformable_mirror_client import \
    AbstractDeformableMirrorClient
from plico.rpc.abstract_remote_procedure_call import \
    AbstractRemoteProcedureCall
from plico.utils.logger import Logger
from plico.utils.decorator import override, returns
from plico_dm.utils.timeout import Timeout
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus
from plico.client.serverinfo_client import ServerInfoClient


class DeformableMirrorClient(AbstractDeformableMirrorClient,
                             HackerableClient, ServerInfoClient):

    def __init__(self,
                 rpcHandler,
                 sockets):
        assert isinstance(rpcHandler, AbstractRemoteProcedureCall)

        self._rpcHandler = rpcHandler
        self._requestSocket = sockets.serverRequest()
        self._statusSocket = sockets.serverStatus()
        self._logger = Logger.of('DeformableMirrorClient')

        HackerableClient.__init__(self,
                                  self._rpcHandler,
                                  self._requestSocket,
                                  self._logger)
        ServerInfoClient.__init__(self,
                                  self._rpcHandler,
                                  self._requestSocket,
                                  self._logger)

    @override
    def enable_control_loop(self,
                            boolEnableOrDisable,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'enable_control_loop', [boolEnableOrDisable],
            timeout=timeoutInSec)

    @override
    def load_shape_sequence(self,
                            shapeSequence,
                            timeStepInSeconds,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'loadShapeSequence', [shapeSequence, timeStepInSeconds],
            timeout=timeoutInSec)

    @override
    def start_shape_sequence(self,
                             timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'startShapeSequence', [],
            timeout=timeoutInSec)

    @override
    def stop_shape_sequence(self,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'stopShapeSequence', [],
            timeout=timeoutInSec)

    @override
    def set_shape(self,
                  command,
                  timeoutInSec=Timeout.MIRROR_SET_SHAPE):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'setShape', [command],
            timeout=timeoutInSec)

    @override
    def get_shape(self, timeoutInSec=Timeout.MIRROR_GET_SHAPE):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getShape', [],
            timeout=timeoutInSec)

    @override
    def get_number_of_modes(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return int(self.get_status(timeoutInSec).number_of_modes)

    @override
    def get_number_of_actuators(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return int(self.get_status(timeoutInSec).number_of_actuators)

    @override
    @returns(DeformableMirrorStatus)
    def get_status(self, timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.receivePickable(
            self._statusSocket,
            timeoutInSec)

    @override
    def get_snapshot(self,
                     prefix,
                     timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getSnapshot', [prefix],
            timeout=timeoutInSec)

    @override
    def save_current_shape_as_reference(
            self,
            tag,
            timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'save_current_shape_as_reference', [tag],
            timeout=timeoutInSec)

    @override
    def load_reference(
            self,
            tag,
            timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'load_reference', [tag],
            timeout=timeoutInSec)

    @override
    def get_reference_shape(
            self,
            timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_reference_shape', [],
            timeout=timeoutInSec)

    @override
    def get_reference_shape_tag(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self.get_status(timeoutInSec).reference_command_tag
