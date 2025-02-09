import pytest
import pandas as pd
import tempfile
from pathlib import Path
import threading
import time
from typing import List
from queue import Queue
from ui_simulator import SimulatorInput, CLISimulator, GUISimulator

class SimulationController:
    """Controls a simulator instance for testing."""
    def __init__(self, simulator_type, available_settings: List[str]):
        self.simulator = simulator_type(available_settings)
        self.command_queue = Queue()
        self._simulator_thread = None
        self.timeout_reason = None
    
    def start(self):
        """Start simulator in a separate thread."""
        def run_simulator():
            try:
                self.simulator.start()
            except Exception as e:
                self.command_queue.put(("error", str(e)))
        
        self._simulator_thread = threading.Thread(target=run_simulator)
        self._simulator_thread.daemon = True
        self._simulator_thread.start()
        time.sleep(0.5)  # Give simulator time to start
    
    def stop(self):
        """Stop the simulator."""
        self.simulator.stop()
        if self._simulator_thread:
            self._simulator_thread.join(timeout=1)
    
    def send_input(self, input_type: SimulatorInput):
        """Send input to the simulator."""
        self.simulator.handle_input(input_type)
        time.sleep(0.1)  # Allow time for input processing
    
    def get_current_setting(self):
        """Get the current setting state."""
        return self.simulator.state.get_current_setting()
    
    def is_running(self):
        """Check if simulator is still running."""
        return self.simulator.running

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory for test data"""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture
def complex_settings_excel(test_data_dir):
    """Create an Excel file with multiple cars and settings"""
    df = pd.DataFrame({
        'Car': ['Car1', 'Car2', 'Car3'],
        'Creator': ['Creator1', 'Creator2', 'Creator1'],
        'Final Drive': [0.05, -0.03, 0.02],
        'Front Power Distrib': [2, -1, 3],
        'Grip Front': [0.3, 0.2, -0.1],
        'Grip Rear': [0.2, 0.1, -0.2]
    })
    
    file_path = test_data_dir / "complex_settings.xlsx"
    df.to_excel(file_path, sheet_name='Street', index=False)
    return str(file_path)

@pytest.fixture
def cli_simulator():
    """Fixture providing a CLI simulator controller."""
    controller = SimulationController(CLISimulator, [
        "final_drive",
        "front_power_distrib",
        "grip_front",
        "front_brake_balance"
    ])
    controller.start()
    yield controller
    controller.stop()

@pytest.fixture
def gui_simulator():
    """Fixture providing a GUI simulator controller."""
    controller = SimulationController(GUISimulator, [
        "final_drive",
        "front_power_distrib",
        "grip_front",
        "front_brake_balance"
    ])
    controller.start()
    yield controller
    controller.stop()
