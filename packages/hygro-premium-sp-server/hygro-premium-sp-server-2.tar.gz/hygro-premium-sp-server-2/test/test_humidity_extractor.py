import unittest
from mock import patch, call

import fake_rpigpio.utils
fake_rpigpio.utils.install()

from RPi import GPIO
from hygro_premium_sp import humidity_extractor
from hygro_premium_sp.humidity_extractor import EasyHomeHygroPremiumSP, Configuration, Products


class TestHumidityExtractor(unittest.TestCase):
    def tearDown(self):
        patch.stopall()

    def test_velocity_per_ratio(self):
        assert EasyHomeHygroPremiumSP.by_ratio(0) == EasyHomeHygroPremiumSP.Off
        assert EasyHomeHygroPremiumSP.by_ratio(0.07) == EasyHomeHygroPremiumSP.Off
        assert EasyHomeHygroPremiumSP.by_ratio(0.1) == EasyHomeHygroPremiumSP.Velocity1
        assert EasyHomeHygroPremiumSP.by_ratio(0.15) == EasyHomeHygroPremiumSP.Velocity1
        assert EasyHomeHygroPremiumSP.by_ratio(0.30) == EasyHomeHygroPremiumSP.Velocity2
        assert EasyHomeHygroPremiumSP.by_ratio(0.45) == EasyHomeHygroPremiumSP.Velocity3
        assert EasyHomeHygroPremiumSP.by_ratio(0.60) == EasyHomeHygroPremiumSP.Velocity4
        assert EasyHomeHygroPremiumSP.by_ratio(0.75) == EasyHomeHygroPremiumSP.Velocity5
        assert EasyHomeHygroPremiumSP.by_ratio(0.90) == EasyHomeHygroPremiumSP.Velocity6
        assert EasyHomeHygroPremiumSP.by_ratio(0.95) == EasyHomeHygroPremiumSP.Velocity7

    def test_start(self):
        setmode = patch('RPi.GPIO.setmode').start()
        setup = patch('RPi.GPIO.setup').start()
        output = patch('RPi.GPIO.output').start()
        conf = Configuration(velocity_ratio=0.1)
        patch('hygro_premium_sp.humidity_extractor.load_configuration').start().return_value = conf

        humidity_extractor.start(conf)

        setmode.assert_called_once_with(GPIO.BCM)
        setup.assert_has_calls([
            call(2, GPIO.OUT, initial=GPIO.LOW),
            call(3, GPIO.OUT, initial=GPIO.HIGH),
        ])
        output.assert_has_calls([
            call(2, GPIO.HIGH),
        ])

    def test_start_solid_state_relays(self):
        setmode = patch('RPi.GPIO.setmode').start()
        setup = patch('RPi.GPIO.setup').start()
        output = patch('RPi.GPIO.output').start()
        conf = Configuration(velocity_ratio=0.1, product=Products.SolidStateRelaysEasyHomeHygroPremiumSP)
        patch('hygro_premium_sp.humidity_extractor.load_configuration').start().return_value = conf

        humidity_extractor.start(conf)

        setmode.assert_called_once_with(GPIO.BCM)
        setup.assert_has_calls([
            call(2, GPIO.OUT, initial=GPIO.HIGH),
            call(3, GPIO.OUT, initial=GPIO.HIGH),
        ])
        output.assert_has_calls([
            call(2, GPIO.LOW),
        ])

    def test_ratio_for(self):
        assert EasyHomeHygroPremiumSP.ratio_for(EasyHomeHygroPremiumSP.Velocity1) == 1 / 7.0
