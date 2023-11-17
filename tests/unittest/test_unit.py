import unittest
from unittest.mock import patch, Mock
from app import get_system_info, plot_system_info

class TestAppFunctions(unittest.TestCase):

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.sensors_battery')
    @patch('psutil.process_iter')
    def test_get_system_info(self, mock_process_iter, mock_sensors_battery, mock_virtual_memory, mock_cpu_percent):
        mock_process = Mock()
        mock_process.info = {'name': 'test_process', 'cpu_percent': 10}
        mock_process_iter.return_value = [mock_process]

        mock_sensors_battery.return_value = Mock(percent=50, power_plugged=True)
        mock_virtual_memory.return_value = Mock(percent=40)
        mock_cpu_percent.return_value = 30

        cpu_usage, memory_usage, battery_info, processes = get_system_info()

        self.assertEqual(cpu_usage, 30)
        self.assertEqual(memory_usage, 40)
        self.assertEqual(battery_info, {'percent': 50, 'power_plugged': True})
        self.assertEqual(processes, [{'name': 'test_process', 'cpu_percent': 10}])

    def test_plot_system_info(self):
        cpu_plot, memory_plot, battery_plot, process_plot = plot_system_info(50, 60, {'percent': 70, 'power_plugged': True}, [{'name': 'test_process', 'cpu_percent': 20}])

        self.assertIn("CPU Usage", cpu_plot)
        self.assertIn("Memory Usage", memory_plot)
        self.assertIn("Battery Percentage", battery_plot)
        self.assertIn("test_process", process_plot)
        self.assertIn("20", process_plot)

if __name__ == '__main__':
    unittest.main()