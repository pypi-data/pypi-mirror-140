#!/usr/bin/env python
import unittest
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus


class DeformableMirrorStatusTest(unittest.TestCase):

    def testHappyPath(self):
        numberOfActs = 10
        numberOfModes = 8
        commandCounter = 42
        reference_command_tag = 'sadf'
        status = DeformableMirrorStatus(
            numberOfActs,
            numberOfModes,
            commandCounter,
            reference_command_tag)

        self.assertEqual(numberOfActs, status.number_of_actuators)
        self.assertEqual(numberOfModes, status.number_of_modes)
        self.assertEqual(commandCounter, status.command_counter)
        self.assertEqual(reference_command_tag, status.reference_command_tag)


if __name__ == "__main__":
    unittest.main()
