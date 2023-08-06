

class DeformableMirrorStatus(object):

    def __init__(self,
                 number_of_actuators,
                 number_of_modes,
                 command_counter,
                 reference_command_tag):
        self.number_of_actuators = number_of_actuators
        self.number_of_modes = number_of_modes
        self.command_counter = command_counter
        self.reference_command_tag = reference_command_tag

    def __repr__(self):
        stra = "Number of Actuators: %s - " % self.number_of_actuators
        stra += "Number of Modes: %s - " % self.number_of_modes
        stra += "command counter: %s" % self.command_counter
        stra += "reference command tag: %s" % self.reference_command_tag
        return stra
