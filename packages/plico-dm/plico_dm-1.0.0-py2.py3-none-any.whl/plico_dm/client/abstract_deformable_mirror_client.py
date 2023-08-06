import abc
from plico.utils.decorator import returnsNone, returns, returnsForExample
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus
from six import with_metaclass


class SnapshotEntry(object):
    COMMAND_COUNTER = "COMMAND_COUNTER"
    SERIAL_NUMBER = "SERIAL_NUMBER"
    STEP_COUNTER = "STEP_COUNTER"


class AbstractDeformableMirrorClient(with_metaclass(abc.ABCMeta, object)):
    """
    Interface to control a deformable mirror


    Assume a modal control of the DM.

    """

    @abc.abstractmethod
    def get_number_of_modes(self):
        """ Number of modes of the deformable mirror

        Return the number of modes of the deformable mirror.
        number of degrees of freedom.

        Return:
            numberOfModes (int): the number of modes of the deformable mirror.
        """
        assert False

    @abc.abstractmethod
    def get_number_of_actuators(self):
        """ Number of actuators of the deformable mirror

        Return the number of actuators of the deformable mirror.

        Return:
            numberOfActuators (int): the number of actuators of the deformable mirror.
        """
        assert False

    @abc.abstractmethod
    @returnsNone
    def set_shape(self, command):
        """ Set Deformable Mirror Shape

        Send to the controller the request to set the DM shape

        Parameters:
            command (:obj:ndarray): an array containing the required value for the actuators/modes
                The size of the array must be equal to the number of modes of the DM


        """
        assert False

    @abc.abstractmethod
    @returnsNone
    def get_shape(self):
        """ Get Deformable Mirror Shape

        Get the current DM shape, reference subtracted

        Return:
            shape (:obj:ndarray): an array containing the measured value for the actuators/modes
                The size of the array must be equal to the number of modes of the DM

        The value are measured if the DM has an internal metrology on position
        The shape sequence is taken into account.

        """
        assert False

    @abc.abstractmethod
    def load_shape_sequence(self, shapeSequence, timeStepInSeconds):
        """ Load a shape sequence to be applied to the mirror

        Every element of the sequence correspond to a DM shape
        After timeStepInSeconds the next element of the sequence is applied
        The sequence is executed ciclycally until 

        The shape sequence is added to the current shape
        The shape sequence is applied as a circular buffer 

        Parameters:
            shapeSequence (:obj:ndarray): an array containing the shape sequence value for the actuators/modes
                The array size is (nModes, nTimeSteps)
            timeStepInSeconds (float): updating interval of sequence.
                Every timeStepInSeconds the controller applies the next column of shapeSequence
        """
        assert False

    @abc.abstractmethod
    @returnsNone
    def start_shape_sequence(self):
        assert False

    @abc.abstractmethod
    @returnsNone
    def stop_shape_sequence(self):
        assert False

    @abc.abstractmethod
    @returnsNone
    def enable_control_loop(self, boolEnableOrDisable):
        """ Enable control loop

        If the deformable mirror controller has position feedback, 
        enable the position control loop
        Else, raise TypeError
        """
        assert False

    @abc.abstractmethod
    @returnsForExample({'WFS_CAMERA.EXPOSURE_TIME_MS': 10})
    def get_snapshot(self, prefix):
        assert False

    @abc.abstractmethod
    @returns(DeformableMirrorStatus)
    def get_status(self):
        assert False

    @abc.abstractmethod
    def save_current_shape_as_reference(self, tag):
        assert False

    @abc.abstractmethod
    def load_reference(self, tag):
        assert False

    @abc.abstractmethod
    def get_reference_shape(self):
        assert False

    @abc.abstractmethod
    def get_reference_shape_tag(self):
        assert False
