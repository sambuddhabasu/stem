"""
Tests for the examples given in stem's tutorial.
"""

import StringIO
import unittest

import stem.response

from stem.control import Controller
from test import mocking

try:
  # added in python 3.3
  from unittest.mock import patch
except ImportError:
  from mock import patch

CIRC_CONTENT = '650 CIRC %d %s \
%s \
PURPOSE=%s'

PATH_CONTENT = '$%s=%s,$%s=%s,$%s=%s'

LIST_CIRCUITS_OUTPUT = """\

Circuit 4 (GENERAL)
 |- B1FA7D51B8B6F0CB585D944F450E7C06EDE7E44C (ByTORAndTheSnowDog, 173.209.180.61)
 |- 0DD9935C5E939CFA1E07B8DDA6D91C1A2A9D9338 (afo02, 87.238.194.176)
 +- DB3B1CFBD3E4D97B84B548ADD5B9A31451EEC4CC (edwardsnowden3, 109.163.234.10)

Circuit 6 (GENERAL)
 |- B1FA7D51B8B6F0CB585D944F450E7C06EDE7E44C (ByTORAndTheSnowDog, 173.209.180.61)
 |- EC01CB4766BADC1611678555CE793F2A7EB2D723 (sprockets, 46.165.197.96)
 +- 9EA317EECA56BDF30CAEB208A253FB456EDAB1A0 (bolobolo1, 96.47.226.20)

Circuit 10 (GENERAL)
 |- B1FA7D51B8B6F0CB585D944F450E7C06EDE7E44C (ByTORAndTheSnowDog, 173.209.180.61)
 |- 00C2C2A16AEDB51D5E5FB7D6168FC66B343D822F (ph3x, 86.59.119.83)
 +- 65242C91BFF30F165DA4D132C81A9EBA94B71D62 (torexit16, 176.67.169.171)
"""


def _get_event(content):
  controller_event = mocking.get_message(content)
  stem.response.convert('EVENT', controller_event)
  return controller_event


class TestTutorialExamples(unittest.TestCase):
  @patch('sys.stdout', new_callable = StringIO.StringIO)
  @patch('stem.control.Controller.from_port', spec = Controller)
  def test_list_circuits(self, from_port_mock, stdout_mock):
    def tutorial_example():
      from stem import CircStatus
      from stem.control import Controller

      with Controller.from_port(port = 9051) as controller:
        controller.authenticate()

        for circ in sorted(controller.get_circuits()):
          if circ.status != CircStatus.BUILT:
            continue

          print
          print "Circuit %s (%s)" % (circ.id, circ.purpose)

          for i, entry in enumerate(circ.path):
            div = '+' if (i == len(circ.path) - 1) else '|'
            fingerprint, nickname = entry

            desc = controller.get_network_status(fingerprint, None)
            address = desc.address if desc else 'unknown'

            print " %s- %s (%s, %s)" % (div, fingerprint, nickname, address)

    def side_effect_get_network_status(relay, default):
      values = {
        path_1[0]: mocking.get_protocolinfo_response(address = "173.209.180.61"),
        path_2[0]: mocking.get_protocolinfo_response(address = "87.238.194.176"),
        path_3[0]: mocking.get_protocolinfo_response(address = "109.163.234.10"),
        path_4[0]: mocking.get_protocolinfo_response(address = "46.165.197.96"),
        path_5[0]: mocking.get_protocolinfo_response(address = "96.47.226.20"),
        path_6[0]: mocking.get_protocolinfo_response(address = "86.59.119.83"),
        path_7[0]: mocking.get_protocolinfo_response(address = "176.67.169.171")
      }
      return values[relay]

    path_1 = ('B1FA7D51B8B6F0CB585D944F450E7C06EDE7E44C', 'ByTORAndTheSnowDog')
    path_2 = ('0DD9935C5E939CFA1E07B8DDA6D91C1A2A9D9338', 'afo02')
    path_3 = ('DB3B1CFBD3E4D97B84B548ADD5B9A31451EEC4CC', 'edwardsnowden3')
    path_4 = ('EC01CB4766BADC1611678555CE793F2A7EB2D723', 'sprockets')
    path_5 = ('9EA317EECA56BDF30CAEB208A253FB456EDAB1A0', 'bolobolo1')
    path_6 = ('00C2C2A16AEDB51D5E5FB7D6168FC66B343D822F', 'ph3x')
    path_7 = ('65242C91BFF30F165DA4D132C81A9EBA94B71D62', 'torexit16')

    circuit_4_path = PATH_CONTENT % (path_1[0], path_1[1], path_2[0], path_2[1], path_3[0], path_3[1])
    circuit_6_path = PATH_CONTENT % (path_1[0], path_1[1], path_4[0], path_4[1], path_5[0], path_5[1])
    circuit_10_path = PATH_CONTENT % (path_1[0], path_1[1], path_6[0], path_6[1], path_7[0], path_7[1])

    circuit_4_content = CIRC_CONTENT % (4, 'BUILT', circuit_4_path, 'GENERAL')
    circuit_6_content = CIRC_CONTENT % (6, 'BUILT', circuit_6_path, 'GENERAL')
    circuit_10_content = CIRC_CONTENT % (10, 'BUILT', circuit_10_path, 'GENERAL')

    circuit_4 = _get_event(circuit_4_content)
    circuit_6 = _get_event(circuit_6_content)
    circuit_10 = _get_event(circuit_10_content)

    controller = from_port_mock().__enter__()
    controller.get_circuits.return_value = [circuit_4, circuit_6, circuit_10]
    controller.get_network_status.side_effect = side_effect_get_network_status
    tutorial_example()
    self.assertEqual(LIST_CIRCUITS_OUTPUT, stdout_mock.getvalue())
