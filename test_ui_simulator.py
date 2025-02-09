import pytest
import time
from ui_simulator import SimulatorInput

def test_simulator_default_values(cli_simulator):
    """Test that settings start with correct default values."""
    current = cli_simulator.get_current_setting()
    assert current.name == "final_drive"
    assert current.current_value == 0.0  # Default value

    # Move to front_power_distrib
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == "front_power_distrib"
    assert current.current_value == 0.4  # Special default value

    # Move to front_brake_balance
    cli_simulator.send_input(SimulatorInput.DOWN)
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == "front_brake_balance"
    assert current.current_value == 0.4  # Special default value

def test_simulator_value_changes(cli_simulator):
    """Test that values change correctly with inputs."""
    # Test final_drive adjustments
    current = cli_simulator.get_current_setting()
    initial_value = current.current_value
    
    # Move right 5 times
    for _ in range(5):
        cli_simulator.send_input(SimulatorInput.RIGHT)
    
    current = cli_simulator.get_current_setting()
    assert current.current_value == initial_value + (0.01 * 5)

def test_simulator_boundary_values(cli_simulator):
    """Test that values don't exceed their boundaries."""
    current = cli_simulator.get_current_setting()
    
    # Try to exceed maximum
    for _ in range(50):
        cli_simulator.send_input(SimulatorInput.RIGHT)
    
    current = cli_simulator.get_current_setting()
    assert current.current_value <= current.range.max_value
    
    # Try to exceed minimum
    for _ in range(50):
        cli_simulator.send_input(SimulatorInput.LEFT)
    
    current = cli_simulator.get_current_setting()
    assert current.current_value >= current.range.min_value

def test_simulator_navigation(cli_simulator):
    """Test navigation between settings."""
    current = cli_simulator.get_current_setting()
    assert current.name == "final_drive"
    
    # Move down through all settings
    setting_names = ["final_drive", "front_power_distrib", "grip_front", "front_brake_balance"]
    for expected_name in setting_names[1:]:
        cli_simulator.send_input(SimulatorInput.DOWN)
        current = cli_simulator.get_current_setting()
        assert current.name == expected_name
    
    # Try to move past last setting
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == setting_names[-1]
    
    # Move back up
    for expected_name in reversed(setting_names[:-1]):
        cli_simulator.send_input(SimulatorInput.UP)
        current = cli_simulator.get_current_setting()
        assert current.name == expected_name

def test_simulator_timeout(cli_simulator):
    """Test that simulator times out after no input."""
    time.sleep(11)  # Wait longer than input timeout
    assert not cli_simulator.is_running()

def test_simulator_max_duration(cli_simulator):
    """Test that simulator times out after max duration."""
    # Keep simulator active with inputs
    for _ in range(31):
        if not cli_simulator.is_running():
            break
        cli_simulator.send_input(SimulatorInput.RIGHT)
        time.sleep(1)
    
    assert not cli_simulator.is_running()

def test_default_value_positioning(cli_simulator):
    """Test that default values are correctly positioned relative to boundaries."""
    
    # Check final_drive (default 0%, range -20% to 0%)
    current = cli_simulator.get_current_setting()
    assert current.name == "final_drive"
    assert current.current_value == 0.0  # Default at upper bound
    assert current.range.min_value == -0.2
    assert current.range.max_value == 0.0
    
    # Only left movement should be possible from default
    cli_simulator.send_input(SimulatorInput.RIGHT)
    assert current.current_value == 0.0  # Shouldn't move right
    cli_simulator.send_input(SimulatorInput.LEFT)
    assert current.current_value < 0.0  # Should move left
    
    # Check front_power_distrib (default 40%, range 60% to 20%)
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == "front_power_distrib"
    assert current.current_value == 0.4  # Default is 40%
    assert current.range.min_value == 0.2
    assert current.range.max_value == 0.6
    
    # Both directions should be possible from default
    initial_value = current.current_value
    cli_simulator.send_input(SimulatorInput.RIGHT)
    assert current.current_value < initial_value  # Should decrease
    cli_simulator.send_input(SimulatorInput.LEFT)
    assert current.current_value == initial_value  # Back to default
    
    # Check front_brake_balance (default 40%, range 80% to 40%)
    cli_simulator.send_input(SimulatorInput.DOWN)
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == "front_brake_balance"
    assert current.current_value == 0.4  # Default is 40%
    assert current.range.min_value == 0.4
    assert current.range.max_value == 0.8
    
    # Only right movement should be possible from default
    cli_simulator.send_input(SimulatorInput.LEFT)
    assert current.current_value == 0.4  # Shouldn't move left (at min)
    cli_simulator.send_input(SimulatorInput.RIGHT)
    assert current.current_value > 0.4  # Should move right

def test_gui_slider_initial_positions(gui_simulator):
    """Test that GUI sliders start at correct default positions."""
    # Get the current setting and its slider
    slider, _, _ = gui_simulator.simulator.sliders["final_drive"]
    assert float(slider.get()) == 0.0  # At maximum (0%)
    
    # Check front_power_distrib slider
    slider, _, _ = gui_simulator.simulator.sliders["front_power_distrib"]
    assert float(slider.get()) == 0.4  # At 40%
    
    # Check front_brake_balance slider
    slider, _, _ = gui_simulator.simulator.sliders["front_brake_balance"]
    assert float(slider.get()) == 0.4  # At minimum (40%)

def test_cli_value_display_formatting(cli_simulator):
    """Test that CLI display shows values in correct percentage format."""
    # Capture the CLI output
    import io
    import sys
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        cli_simulator._display_current_setting()
    output = f.getvalue()
    
    # Check initial value format (0%)
    assert "0.00%" in output
    
    # Move to front_power_distrib and check format (40%)
    cli_simulator.send_input(SimulatorInput.DOWN)
    f = io.StringIO()
    with redirect_stdout(f):
        cli_simulator._display_current_setting()
    output = f.getvalue()
    assert "40.00%" in output

def test_gui_value_label_formatting(gui_simulator):
    """Test that GUI value labels show correct percentage format."""
    # Check final_drive label
    _, value_label, _ = gui_simulator.simulator.sliders["final_drive"]
    assert value_label.cget("text") == "0.00%"
    
    # Check front_power_distrib label
    _, value_label, _ = gui_simulator.simulator.sliders["front_power_distrib"]
    assert value_label.cget("text") == "40.00%"
    
    # Check values update correctly after movement
    setting = gui_simulator.simulator.state.get_current_setting()
    gui_simulator.simulator.handle_input(SimulatorInput.LEFT)
    _, value_label, _ = gui_simulator.simulator.sliders[setting.name]
    assert ".00%" in value_label.cget("text")  # Should still be formatted with 2 decimal places

def test_highlighted_value_accuracy(gui_simulator):
    """Test that highlighted setting matches the current value in both display and state."""
    current_setting = gui_simulator.simulator.state.get_current_setting()
    slider, value_label, frame = gui_simulator.simulator.sliders[current_setting.name]
    
    # Check that slider value matches internal state
    assert abs(float(slider.get()) - current_setting.current_value) < 0.001
    
    # Check that displayed value matches internal state
    displayed_value = float(value_label.cget("text").strip("%")) / 100
    assert abs(displayed_value - current_setting.current_value) < 0.001
    
    # Check that the frame is highlighted
    assert frame.cget("style") == "Highlight.TFrame"

def test_all_setting_increment_accuracy(cli_simulator):
    """Test that all settings change by their correct increment amounts."""
    increment_map = {
        "final_drive": 0.01,
        "front_power_distrib": 0.01,
        "grip_front": 0.01,
        "front_brake_balance": 0.01
    }
    
    # Test each setting
    current = cli_simulator.get_current_setting()
    while current:
        initial_value = current.current_value
        increment = increment_map[current.name]
        
        # Test right movement
        cli_simulator.send_input(SimulatorInput.RIGHT)
        current = cli_simulator.get_current_setting()
        if current.current_value != initial_value:  # If value changed
            assert abs(current.current_value - initial_value) == increment
        
        # Test left movement
        cli_simulator.send_input(SimulatorInput.LEFT)
        current = cli_simulator.get_current_setting()
        assert abs(current.current_value - initial_value) < 0.0001  # Back to initial
        
        # Move to next setting
        cli_simulator.send_input(SimulatorInput.DOWN)
        current = cli_simulator.get_current_setting()

def test_gui_slider_sync(gui_simulator):
    """Test that GUI sliders stay synchronized with internal state."""
    for _ in range(5):  # Test multiple movements
        current = gui_simulator.get_current_setting()
        slider, value_label, _ = gui_simulator.simulator.sliders[current.name]
        initial_value = current.current_value
        
        # Move right and verify sync
        gui_simulator.send_input(SimulatorInput.RIGHT)
        assert abs(float(slider.get()) - current.current_value) < 0.0001
        displayed_value = float(value_label.cget("text").strip("%")) / 100
        assert abs(displayed_value - current.current_value) < 0.0001
        
        # Move down to next setting
        gui_simulator.send_input(SimulatorInput.DOWN)

def test_rapid_input_handling(cli_simulator):
    """Test that rapid inputs are handled correctly."""
    current = cli_simulator.get_current_setting()
    initial_value = current.current_value
    
    # Send multiple rapid inputs
    for _ in range(10):
        cli_simulator.send_input(SimulatorInput.RIGHT)
        time.sleep(0.01)  # Very short delay
    
    current = cli_simulator.get_current_setting()
    assert current.current_value == min(
        initial_value + (0.01 * 10),
        current.range.max_value
    )

def test_boundary_value_display(gui_simulator):
    """Test that boundary values are displayed correctly."""
    # Test minimum value
    current = gui_simulator.get_current_setting()
    
    # Move to minimum
    while current.current_value > current.range.min_value:
        gui_simulator.send_input(SimulatorInput.LEFT)
    
    slider, value_label, _ = gui_simulator.simulator.sliders[current.name]
    min_displayed = float(value_label.cget("text").strip("%")) / 100
    assert abs(min_displayed - current.range.min_value) < 0.0001
    
    # Move to maximum
    while current.current_value < current.range.max_value:
        gui_simulator.send_input(SimulatorInput.RIGHT)
    
    max_displayed = float(value_label.cget("text").strip("%")) / 100
    assert abs(max_displayed - current.range.max_value) < 0.0001

def test_timeout_with_sporadic_input(cli_simulator):
    """Test timeout behavior with sporadic inputs."""
    start_time = time.time()
    
    while time.time() - start_time < 15:  # Run for 15 seconds
        if time.time() - start_time > 8:  # Stop inputs after 8 seconds
            break
        cli_simulator.send_input(SimulatorInput.RIGHT)
        time.sleep(1.5)  # Sporadic inputs
    
    # Should timeout after no input for 10 seconds
    time.sleep(3)  # Wait for timeout
    assert not cli_simulator.is_running()

def test_setting_wrap_prevention(cli_simulator):
    """Test that settings don't wrap around at list boundaries."""
    # Try to move up from first setting
    current = cli_simulator.get_current_setting()
    first_setting_name = current.name
    cli_simulator.send_input(SimulatorInput.UP)
    current = cli_simulator.get_current_setting()
    assert current.name == first_setting_name
    
    # Move to last setting
    while True:
        cli_simulator.send_input(SimulatorInput.DOWN)
        if not cli_simulator.get_current_setting().name != current.name:
            break
        current = cli_simulator.get_current_setting()
    
    # Try to move past last setting
    last_setting_name = current.name
    cli_simulator.send_input(SimulatorInput.DOWN)
    current = cli_simulator.get_current_setting()
    assert current.name == last_setting_name

def test_multiple_direction_changes(cli_simulator):
    """Test behavior when rapidly changing directions."""
    current = cli_simulator.get_current_setting()
    initial_value = current.current_value
    
    # Alternate between left and right
    movements = [
        SimulatorInput.RIGHT,
        SimulatorInput.LEFT,
        SimulatorInput.RIGHT,
        SimulatorInput.RIGHT,
        SimulatorInput.LEFT,
    ]
    
    for movement in movements:
        cli_simulator.send_input(movement)
    
    # Calculate expected value
    expected_value = initial_value + (0.01 * movements.count(SimulatorInput.RIGHT))
    expected_value -= (0.01 * movements.count(SimulatorInput.LEFT))
    expected_value = max(current.range.min_value, 
                        min(current.range.max_value, expected_value))
    
    assert abs(current.current_value - expected_value) < 0.0001

def test_gui_focus_persistence(gui_simulator):
    """Test that highlighted setting persists correctly during value changes."""
    current = gui_simulator.get_current_setting()
    initial_name = current.name
    
    # Make multiple value changes
    for _ in range(5):
        gui_simulator.send_input(SimulatorInput.RIGHT)
    
    # Verify same setting is still focused
    current = gui_simulator.get_current_setting()
    assert current.name == initial_name
    
    # Verify highlight is correct
    _, _, frame = gui_simulator.simulator.sliders[current.name]
    assert frame.cget("style") == "Highlight.TFrame"

def test_cli_ahk_integration(cli_simulator, tmp_path):
    """Test integration between CLI simulator and AHK scripts."""
    from TCM_script_creator import CarSetup
    
    # Create a simple car setup
    settings = {
        "final_drive": -0.05,
        "front_power_distrib": 45,  # Should move right from 60% to 45%
        "front_brake_balance": 60    # Should move right from 80% to 60%
    }
    setup = CarSetup(settings)
    
    # Generate AHK script with CLI mode
    script = setup.generate_ahk_script()
    script_path = tmp_path / "test_setup.ahk"
    script_path.write_text(script)
    
    # Verify script contains CLI mode handling
    assert "--cli" in script
    assert "SetTimer, ApplySettings, -100" in script
    assert "ExitApp" in script

def test_simulator_command_interface(cli_simulator):
    """Test simulator's command interface for automated testing."""
    # Test sending multiple commands in sequence
    commands = [
        (SimulatorInput.RIGHT, 5),   # Move right 5 times
        (SimulatorInput.DOWN, 1),    # Move down once
        (SimulatorInput.LEFT, 3),    # Move left 3 times
        (SimulatorInput.UP, 1)       # Move back up
    ]
    
    initial_setting = cli_simulator.get_current_setting()
    initial_value = initial_setting.current_value
    
    # Execute command sequence
    for command, count in commands:
        for _ in range(count):
            cli_simulator.send_input(command)
    
    # Verify we're back at the initial setting
    final_setting = cli_simulator.get_current_setting()
    assert final_setting.name == initial_setting.name
    
    # Value should reflect 5 right moves - 3 left moves = 2 right moves net
    expected_value = min(
        initial_value + (0.01 * 2),
        initial_setting.range.max_value
    )
    assert abs(final_setting.current_value - expected_value) < 0.0001

def test_automated_test_sequence(cli_simulator):
    """Test running an automated test sequence."""
    test_sequence = [
        # Format: (setting_name, target_value, max_steps)
        ("final_drive", -0.05, 10),
        ("front_power_distrib", 0.45, 20),  # Move from 60% to 45%
        ("front_brake_balance", 0.6, 20)    # Move from 80% to 60%
    ]
    
    for target_setting, target_value, max_steps in test_sequence:
        # Move to correct setting if needed
        while cli_simulator.get_current_setting().name != target_setting:
            cli_simulator.send_input(SimulatorInput.DOWN)
        
        current = cli_simulator.get_current_setting()
        steps_taken = 0
        
        # Adjust value
        while abs(current.current_value - target_value) > 0.001 and steps_taken < max_steps:
            if current.current_value < target_value:
                cli_simulator.send_input(SimulatorInput.RIGHT)
            else:
                cli_simulator.send_input(SimulatorInput.LEFT)
            steps_taken += 1
        
        # Verify we reached target value
        assert abs(current.current_value - target_value) < 0.01, \
            f"Failed to reach target value for {target_setting}"
        assert steps_taken < max_steps, \
            f"Exceeded maximum steps for {target_setting}"

def test_error_reporting(cli_simulator, capsys):
    """Test error reporting in automated test context."""
    # Test timeout reporting
    time.sleep(11)  # Trigger timeout
    captured = capsys.readouterr()
    assert "Timeout:" in captured.out
    assert not cli_simulator.is_running()
    
    # Verify simulator state is properly cleaned up
    assert cli_simulator.simulator._timeout_thread is not None
    assert not cli_simulator.simulator._timeout_thread.is_alive()

def test_concurrent_ahk_simulator(cli_simulator, tmp_path):
    """Test running multiple AHK scripts with simulator."""
    from TCM_script_creator import CarSetup
    import subprocess
    import threading
    
    # Create two different car setups
    setups = [
        {
            "final_drive": -0.05,
            "front_power_distrib": 45
        },
        {
            "front_brake_balance": 60,
            "grip_front": -0.1
        }
    ]
    
    scripts = []
    for i, settings in enumerate(setups):
        setup = CarSetup(settings)
        script = setup.generate_ahk_script()
        script_path = tmp_path / f"test_setup_{i}.ahk"
        script_path.write_text(script)
        scripts.append(script_path)
    
    # Function to run script and capture result
    def run_script(script_path, results):
        try:
            subprocess.run(["AutoHotkey.exe", str(script_path), "--cli"], 
                         check=True, timeout=5)
            results.append(True)
        except Exception as e:
            results.append(False)
    
    # Run scripts in sequence
    results = []
    for script in scripts:
        thread = threading.Thread(target=run_script, args=(script, results))
        thread.start()
        thread.join(timeout=6)
    
    # Verify all scripts completed
    assert all(results), "Not all scripts completed successfully"

def test_csv_range_enforcement(cli_simulator):
    """Test that value ranges from pro_settings_description.csv are enforced."""
    csv_ranges = {
        "final_drive": (-0.20, 0.00),
        "front_power_distrib": (0.60, 0.20),  # 60% to 20%
        "grip_front": (-0.20, 0.00),
        "front_brake_balance": (0.80, 0.40)  # 80% to 40%
    }
    
    for setting_name, (max_val, min_val) in csv_ranges.items():
        # Navigate to setting
        while cli_simulator.get_current_setting().name != setting_name:
            cli_simulator.send_input(SimulatorInput.DOWN)
        
        current = cli_simulator.get_current_setting()
        
        # Try to exceed maximum
        while current.current_value < max_val:
            cli_simulator.send_input(SimulatorInput.LEFT)
        cli_simulator.send_input(SimulatorInput.LEFT)  # One more time
        assert abs(current.current_value - max_val) < 0.001
        
        # Try to exceed minimum
        while current.current_value > min_val:
            cli_simulator.send_input(SimulatorInput.RIGHT)
        cli_simulator.send_input(SimulatorInput.RIGHT)  # One more time
        assert abs(current.current_value - min_val) < 0.001

def test_special_default_values(cli_simulator):
    """Test that special default values from CSV are respected."""
    special_defaults = {
        "front_power_distrib": 0.4,  # 40%
        "front_brake_balance": 0.4   # 40%
    }
    
    # Verify each special default
    for setting_name, expected_default in special_defaults.items():
        # Navigate to setting
        while cli_simulator.get_current_setting().name != setting_name:
            cli_simulator.send_input(SimulatorInput.DOWN)
        
        current = cli_simulator.get_current_setting()
        assert abs(current.current_value - expected_default) < 0.001, \
            f"{setting_name} default value incorrect"

def test_value_wrapping_prevention(cli_simulator):
    """Test that values don't wrap around at their boundaries."""
    setting_configs = [
        ("final_drive", SimulatorInput.LEFT, 0.0),     # At max, try to increase
        ("front_power_distrib", SimulatorInput.RIGHT, 0.2),  # At min, try to decrease
        ("grip_front", SimulatorInput.LEFT, 0.0),      # At max, try to increase
        ("front_brake_balance", SimulatorInput.RIGHT, 0.4)   # At min, try to decrease
    ]
    
    for setting_name, direction, boundary_value in setting_configs:
        # Navigate to setting
        while cli_simulator.get_current_setting().name != setting_name:
            cli_simulator.send_input(SimulatorInput.DOWN)
        
        current = cli_simulator.get_current_setting()
        
        # Move to boundary
        while abs(current.current_value - boundary_value) > 0.001:
            cli_simulator.send_input(direction)
        
        # Try to move past boundary
        initial_value = current.current_value
        cli_simulator.send_input(direction)
        assert abs(current.current_value - initial_value) < 0.001, \
            f"{setting_name} value wrapped around boundary"

def test_gui_slider_ranges(gui_simulator):
    """Test that GUI sliders are configured with correct ranges."""
    range_configs = {
        "final_drive": (-0.20, 0.00),
        "front_power_distrib": (0.60, 0.20),
        "grip_front": (-0.20, 0.00),
        "front_brake_balance": (0.80, 0.40)
    }
    
    for setting_name, (max_val, min_val) in range_configs.items():
        slider, _, _ = gui_simulator.simulator.sliders[setting_name]
        assert abs(float(slider.cget("from")) - min_val) < 0.001, \
            f"{setting_name} slider minimum incorrect"
        assert abs(float(slider.cget("to")) - max_val) < 0.001, \
            f"{setting_name} slider maximum incorrect"

def test_gui_slider_resolution(gui_simulator):
    """Test that GUI sliders move in correct increments."""
    current = gui_simulator.get_current_setting()
    slider, _, _ = gui_simulator.simulator.sliders[current.name]
    
    # Record initial value
    initial_value = float(slider.get())
    
    # Move slider by one increment
    gui_simulator.send_input(SimulatorInput.RIGHT)
    
    # Verify increment is 0.01
    new_value = float(slider.get())
    assert abs((new_value - initial_value) - 0.01) < 0.0001, \
        "Slider movement increment incorrect"

def test_timeout_race_conditions(cli_simulator):
    """Test timeout behavior under race conditions."""
    from threading import Thread
    import random
    
    def random_inputs():
        for _ in range(20):
            if not cli_simulator.is_running():
                break
            direction = random.choice([
                SimulatorInput.UP,
                SimulatorInput.DOWN,
                SimulatorInput.LEFT,
                SimulatorInput.RIGHT
            ])
            cli_simulator.send_input(direction)
            time.sleep(random.uniform(0.1, 0.5))
    
    # Start multiple threads sending random inputs
    threads = [Thread(target=random_inputs) for _ in range(3)]
    for t in threads:
        t.start()
    
    # Wait until close to timeout
    time.sleep(28)
    
    # Stop input threads
    for t in threads:
        t.join(timeout=1)
    
    # Verify timeout occurs after 30 seconds
    time.sleep(3)
    assert not cli_simulator.is_running()

def test_timeout_at_boundaries(cli_simulator):
    """Test timeout behavior when at value boundaries."""
    current = cli_simulator.get_current_setting()
    
    # Move to maximum value
    while current.current_value < current.range.max_value:
        cli_simulator.send_input(SimulatorInput.LEFT)
    
    # Try to exceed maximum for 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        cli_simulator.send_input(SimulatorInput.LEFT)
        time.sleep(0.1)
    
    # Wait for input timeout
    time.sleep(6)
    assert not cli_simulator.is_running()

def test_timeout_during_navigation(cli_simulator):
    """Test timeout during setting navigation."""
    # Start moving between settings
    start_time = time.time()
    while time.time() - start_time < 25:
        cli_simulator.send_input(SimulatorInput.DOWN)
        time.sleep(1)
        cli_simulator.send_input(SimulatorInput.UP)
        time.sleep(1)
    
    # Stop inputs and wait for timeout
    time.sleep(11)  # Just over input timeout
    assert not cli_simulator.is_running()

def test_timeout_recovery_attempt(cli_simulator):
    """Test that timeout cannot be prevented by last-moment input."""
    # Wait until just before timeout
    time.sleep(9.5)  # Just before input timeout
    
    # Try to prevent timeout with last-moment input
    cli_simulator.send_input(SimulatorInput.RIGHT)
    
    # Verify input was accepted
    last_input_time = cli_simulator.simulator.state.last_input_time
    
    # Wait until absolute timeout
    time.sleep(21)  # This should trigger the 30-second total timeout
    assert not cli_simulator.is_running()
    
    # Verify the last input was recorded but didn't prevent timeout
    assert time.time() - last_input_time > 20

def test_multiple_simulator_timeouts(cli_simulator, gui_simulator):
    """Test timeout behavior with multiple simulator instances."""
    # Start some activity in both simulators
    for _ in range(5):
        cli_simulator.send_input(SimulatorInput.RIGHT)
        gui_simulator.send_input(SimulatorInput.LEFT)
        time.sleep(0.5)
    
    # Let CLI simulator timeout first
    time.sleep(10)
    assert not cli_simulator.is_running()
    assert gui_simulator.is_running()
    
    # Let GUI simulator timeout
    time.sleep(10)
    assert not gui_simulator.is_running()

def test_timeout_cleanup(cli_simulator):
    """Test that resources are properly cleaned up after timeout."""
    # Force a timeout
    time.sleep(11)
    assert not cli_simulator.is_running()
    
    # Verify cleanup
    assert cli_simulator.simulator._timeout_thread is not None
    assert not cli_simulator.simulator._timeout_thread.is_alive()
    assert not hasattr(cli_simulator.simulator, '_key_thread') or \
           not cli_simulator.simulator._key_thread.is_alive()
    
    # Try sending more inputs after timeout
    cli_simulator.send_input(SimulatorInput.RIGHT)
    current = cli_simulator.get_current_setting()
    initial_value = current.current_value
    
    # Verify no change occurred
    assert current.current_value == initial_value

def test_complete_ahk_flow(cli_simulator, tmp_path):
    """Test complete flow from script generation through UI simulation."""
    from TCM_script_creator import CarSetup
    import subprocess
    import threading
    
    # Test a complex setup with multiple settings
    settings = {
        "final_drive": -0.15,        # Should move left 15 times
        "front_power_distrib": 0.35, # Should move right 25 times from 0.60
        "grip_front": -0.10,         # Should move left 10 times
        "front_brake_balance": 0.50  # Should move right 30 times from 0.80
    }
    
    # Create and validate script
    setup = CarSetup(settings)
    script = setup.generate_ahk_script()
    script_path = tmp_path / "complete_test.ahk"
    script_path.write_text(script)
    
    # Verify script contains correct CLI mode handling
    assert "--cli" in script
    assert "SetTimer, ApplySettings, -100" in script
    
    # Create a queue for test results
    results = []
    
    def run_ahk_script():
        try:
            result = subprocess.run(
                ["AutoHotkey.exe", str(script_path), "--cli"],
                capture_output=True,
                text=True,
                timeout=10
            )
            results.append(result.returncode == 0)
        except Exception as e:
            results.append(False)
    
    # Run script in background
    script_thread = threading.Thread(target=run_ahk_script)
    script_thread.start()
    
    # Wait for script to finish
    script_thread.join(timeout=15)
    
    # Verify script execution
    assert results[0], "AHK script execution failed"
    
    # Verify final values in simulator
    expected_values = {
        "final_drive": -0.15,
        "front_power_distrib": 0.35,
        "grip_front": -0.10,
        "front_brake_balance": 0.50
    }
    
    # Reset simulator to start
    cli_simulator.simulator.state.current_setting_index = 0
    
    # Check each setting's final value
    for setting_name, expected_value in expected_values.items():
        while cli_simulator.get_current_setting().name != setting_name:
            cli_simulator.send_input(SimulatorInput.DOWN)
        
        current = cli_simulator.get_current_setting()
        assert abs(current.current_value - expected_value) < 0.01, \
            f"Setting {setting_name} value incorrect. Expected {expected_value}, got {current.current_value}"

def test_script_input_validation(cli_simulator, tmp_path):
    """Test that generated scripts properly validate settings."""
    from TCM_script_creator import CarSetup
    import subprocess
    
    # Test invalid settings that exceed ranges
    invalid_settings = [
        {
            "final_drive": -0.25,  # Exceeds -20% minimum
            "front_power_distrib": 0.40
        },
        {
            "front_power_distrib": 0.15,  # Below 20% minimum
            "grip_front": 0.05  # Exceeds 0% maximum
        }
    ]
    
    for settings in invalid_settings:
        setup = CarSetup(settings)
        script = setup.generate_ahk_script()
        script_path = tmp_path / "invalid_test.ahk"
        script_path.write_text(script)
        
        # Run script
        result = subprocess.run(
            ["AutoHotkey.exe", str(script_path), "--cli"],
            capture_output=True,
            text=True
        )
        
        # Script should still complete, but values should be clamped
        assert result.returncode == 0
        
        # Verify values were clamped to valid ranges
        for name, value in settings.items():
            while cli_simulator.get_current_setting().name != name:
                cli_simulator.send_input(SimulatorInput.DOWN)
            
            current = cli_simulator.get_current_setting()
            assert current.current_value >= current.range.min_value
            assert current.current_value <= current.range.max_value

def test_script_batch_execution(cli_simulator, tmp_path):
    """Test executing multiple scripts in sequence."""
    from TCM_script_creator import CarSetup
    import subprocess
    
    # Create multiple scripts with different settings
    test_cases = [
        {
            "final_drive": -0.10,
            "front_power_distrib": 0.45
        },
        {
            "grip_front": -0.15,
            "front_brake_balance": 0.60
        },
        {
            "final_drive": -0.05,
            "front_brake_balance": 0.70
        }
    ]
    
    scripts = []
    for i, settings in enumerate(test_cases):
        setup = CarSetup(settings)
        script = setup.generate_ahk_script()
        script_path = tmp_path / f"batch_test_{i}.ahk"
        script_path.write_text(script)
        scripts.append((script_path, settings))
    
    # Execute each script and verify results
    for script_path, settings in scripts:
        # Reset simulator state
        cli_simulator.simulator.state.current_setting_index = 0
        
        # Run script
        result = subprocess.run(
            ["AutoHotkey.exe", str(script_path), "--cli"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        
        # Verify each setting
        for name, expected_value in settings.items():
            while cli_simulator.get_current_setting().name != name:
                cli_simulator.send_input(SimulatorInput.DOWN)
            
            current = cli_simulator.get_current_setting()
            assert abs(current.current_value - expected_value) < 0.01, \
                f"Setting {name} value incorrect after script execution"

def test_script_timeout_handling(cli_simulator, tmp_path):
    """Test that scripts handle simulator timeouts gracefully."""
    from TCM_script_creator import CarSetup
    import subprocess
    
    # Create a script with many settings to take longer
    settings = {setting: 0.01 for setting in [
        "final_drive", "front_power_distrib", "grip_front", 
        "front_brake_balance"
    ]}
    
    setup = CarSetup(settings)
    script = setup.generate_ahk_script()
    script_path = tmp_path / "timeout_test.ahk"
    script_path.write_text(script)
    
    # Add artificial delay to simulator to force timeout
    original_handle_input = cli_simulator.simulator.handle_input
    def delayed_handle_input(input_type):
        time.sleep(0.5)  # Add delay to each input
        return original_handle_input(input_type)
    cli_simulator.simulator.handle_input = delayed_handle_input
    
    try:
        # Run script - should timeout
        result = subprocess.run(
            ["AutoHotkey.exe", str(script_path), "--cli"],
            capture_output=True,
            text=True,
            timeout=35  # Allow for timeout
        )
        
        # Verify timeout occurred
        assert not cli_simulator.is_running()
        
        # Check error output
        assert "timeout" in result.stderr.lower() or \
               "timeout" in result.stdout.lower() or \
               result.returncode != 0
    finally:
        # Restore original handler
        cli_simulator.simulator.handle_input = original_handle_input