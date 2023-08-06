#!/usr/bin/env python
import unittest
import numpy as np
from plico_dm.client.simulated_deformable_mirror_client import \
    SimulatedDeformableMirrorClient
from test.fake_time_mod import FakeTimeMod


class SimulatedDeformableMirrorClientTest(unittest.TestCase):

    def setUp(self):
        self.timeMod = FakeTimeMod()
        self.dm = SimulatedDeformableMirrorClient(timeModule=self.timeMod)
        self.nModes = SimulatedDeformableMirrorClient.N_MODES

    def testGetNumberOfModes(self):
        nModes = self.dm.get_number_of_modes()
        self.assertEqual(
            SimulatedDeformableMirrorClient.N_MODES, nModes)

    def testSetAndGetShape(self):
        wantShape = np.arange(self.nModes)
        self.dm.set_shape(wantShape)
        get_shape = self.dm.get_shape()
        self.assertTrue(np.array_equal(wantShape, get_shape))

    def testLoopSequence(self):
        timeStepInSeconds = 0.1
        seqNumberOfTimeSteps = 100

        initialShape = np.arange(self.nModes) * 42
        self.dm.set_shape(initialShape)
        seq = np.arange(self.nModes * seqNumberOfTimeSteps).reshape(
            self.nModes, seqNumberOfTimeSteps)
        self.dm.load_shape_sequence(seq, timeStepInSeconds)

        self.dm.start_shape_sequence()
        shapeBefore = self.dm.get_shape()
        self.timeMod.sleep(timeStepInSeconds * 2)
        shapeAfter = self.dm.get_shape()
        self.assertFalse(np.array_equal(shapeAfter, shapeBefore))

        self.dm.stop_shape_sequence()
        shapeBefore = self.dm.get_shape()
        self.timeMod.sleep(timeStepInSeconds * 2)
        shapeAfter = self.dm.get_shape()
        self.assertTrue(np.array_equal(shapeAfter, shapeBefore))

    def testCommandsReference(self):
        self.dm.load_reference('zeros')
        initial_shape = np.arange(self.nModes) * 42
        self.dm.set_shape(initial_shape)

        tag = 'asdf'
        self.dm.save_current_shape_as_reference(tag)
        self.dm.load_reference(tag)
        got_tag = self.dm.get_reference_shape_tag()
        reference_command = self.dm.get_reference_shape()

        self.assertEqual(tag, got_tag)
        np.testing.assert_allclose(initial_shape, reference_command)


if __name__ == "__main__":
    unittest.main()
