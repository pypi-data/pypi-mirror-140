import numpy as np
from plico.utils.decorator import override, returns
from plico_dm.client.abstract_deformable_mirror_client import \
    AbstractDeformableMirrorClient
from plico_dm.utils.timeout import Timeout
import time
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus


class SimulatedDeformableMirrorClient(AbstractDeformableMirrorClient):

    N_MODES = 4

    def __init__(self, timeModule=time):
        self._timeMod = timeModule
        self._shape = np.zeros(self.N_MODES)
        self._commandCounter = 0
        self._isControlLoopEnabled = False
        self._isShapeSequenceEnabled = False
        self._shapeSeq = np.zeros(self.N_MODES).reshape((
            self.N_MODES, 1))
        self._nElementsShapeSeq = 1
        self._seqTimeStepInSeconds = 1
        self._shapeSeqIdx = 0
        self._timeStampSequence = 0
        self._reference_command = np.zeros(self.N_MODES)
        self._reference_command_tag = 'zeros'
        self._ref_dict = {}
        self._ref_dict['zeros'] = np.zeros(self.N_MODES)

    @override
    def enable_control_loop(self,
                            boolEnableOrDisable,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isControlLoopEnabled = boolEnableOrDisable

    @override
    def load_shape_sequence(self,
                            shapeSequence,
                            timeStepInSeconds,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        self._shapeSeq = shapeSequence
        self._seqTimeStepInSeconds = timeStepInSeconds
        self._shapeSeqIdx = 0
        self._nElementsShapeSeq = self._shapeSeq.shape[1]

    @override
    def start_shape_sequence(self,
                             timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isShapeSequenceEnabled = True
        self._timeStampSequence = self._timeMod.time()

    @override
    def stop_shape_sequence(self,
                            timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isShapeSequenceEnabled = False

    @override
    def set_shape(self,
                  command,
                  timeoutInSec=Timeout.MIRROR_SET_SHAPE):
        self._shape = command + self._reference_command
        self._commandCounter += 1

    @override
    def get_shape(self, timeoutInSec=Timeout.MIRROR_GET_SHAPE):
        shape = self._shape - self._reference_command
        if self._isShapeSequenceEnabled:
            now = self._timeMod.time()
            nSteps = int((now - self._timeStampSequence) /
                         self._seqTimeStepInSeconds)
            seqIdx = nSteps % self._nElementsShapeSeq
            shape += self._shapeSeq[:, seqIdx]
        return shape

    @override
    def get_number_of_modes(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self.N_MODES

    @override
    def get_number_of_actuators(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self.N_MODES

    @override
    @returns(DeformableMirrorStatus)
    def get_status(self, timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return DeformableMirrorStatus(self._shape,
                                      self._commandCounter)

    @override
    def get_snapshot(self):
        return {}

    @override
    def save_current_shape_as_reference(self, tag):
        self._ref_dict[tag] = self._shape

    @override
    def load_reference(self, tag):
        self._reference_command = self._ref_dict[tag]
        self._reference_command_tag = tag

    @override
    def get_reference_shape(self):
        return self._reference_command

    @override
    def get_reference_shape_tag(self):
        return self._reference_command_tag
