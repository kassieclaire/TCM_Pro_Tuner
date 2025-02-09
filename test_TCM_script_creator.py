import pytest
import pandas as pd
import tempfile
from pathlib import Path
from TCM_script_creator import CarSetting, CarSetup, SettingsConverter
from TCM_script_creator import main
import sys
from unittest.mock import patch

# test_TCM_script_creator.py

@pytest.fixture
def sample_excel():
    """Create a temporary Excel file with test data"""
    df = pd.DataFrame({
        'Car': ['Test Car'],
        'Creator': ['Test Creator'],
        'Final Drive': [0.05],
        'Front Power Distrib': [2],
        'Grip Front': [0.3]
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, sheet_name='Street', index=False)
        return tmp.name

@pytest.fixture
def sample_csv():
    """Create a temporary CSV file with test data"""
    df = pd.DataFrame({
        'Car': ['Test Car'],
        'Creator': ['Test Creator'],
        'Final Drive': [0.05],
        'Front Power Distrib': [2],
        'Grip Front': [0.3]
    })
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        return tmp.name

def test_car_setting_keystrokes():
    """Test CarSetting keystrokes generation"""
    # Test positive value
    setting = CarSetting(name="test", value=0.05, increment=0.01, is_delta=True)
    assert setting.get_keystrokes() == ["Right"] * 5
    
    # Test negative value
    setting = CarSetting(name="test", value=-0.03, increment=0.01, is_delta=True)
    assert setting.get_keystrokes() == ["Left"] * 3
    
    # Test zero value
    setting = CarSetting(name="test", value=0, increment=0.01, is_delta=True)
    assert setting.get_keystrokes() == []

def test_car_setup_script_generation():
    """Test CarSetup AHK script generation"""
    settings = {
        "final_drive": 0.05,
        "front_power_distrib": 2
    }
    setup = CarSetup(settings)
    script = setup.generate_ahk_script()
    
    assert "#SingleInstance Force" in script
    assert "Send {Right}" in script
    assert "Settings applied!" in script

def test_settings_converter(sample_excel):
    """Test SettingsConverter functionality"""
    converter = SettingsConverter(sample_excel)
    setup = converter.get_car_setup("Street", "Test Car", "Test Creator")
    
    assert len(setup.settings) > 0
    assert any(s.name == "final_drive" for s in setup.settings)
    assert any(s.name == "front_power_distrib" for s in setup.settings)

def test_invalid_file():
    """Test handling of invalid files"""
    with pytest.raises(FileNotFoundError):
        SettingsConverter("nonexistent.xlsx")
    
    with pytest.raises(ValueError):
        SettingsConverter("invalid.txt")

def test_missing_car_settings(sample_excel):
    """Test handling of missing car settings"""
    converter = SettingsConverter(sample_excel)
    with pytest.raises(ValueError):
        converter.get_car_setup("Street", "Nonexistent Car", "Test Creator")

def test_integration(sample_excel, tmp_path):
    """Integration test using temporary files"""
    output_file = tmp_path / "test_setup.ahk"
    
    
    test_args = [
        "script.py",
        "--settings-file", sample_excel,
        "--sheet", "Street",
        "--car", "Test Car",
        "--creator", "Test Creator",
        "--output", str(output_file)
    ]
    
    with patch.object(sys, 'argv', test_args):
        assert main() == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "#SingleInstance Force" in content

def test_setting_increments():
    """Test various setting increment values"""
    settings = {
        "final_drive": 0.03,
        "grip_front": 0.5,
        "front_brake_balance": 3
    }
    setup = CarSetup(settings)
    
    for setting in setup.settings:
        if setting.name == "final_drive":
            assert len(setting.get_keystrokes()) == 3
        elif setting.name == "grip_front":
            assert len(setting.get_keystrokes()) == 5
        elif setting.name == "front_brake_balance":
            assert len(setting.get_keystrokes()) == 3

def test_csv_support(sample_csv):
    """Test CSV file support"""
    converter = SettingsConverter(sample_csv)
    setup = converter.get_car_setup("Street", "Test Car", "Test Creator")
    assert len(setup.settings) > 0

def test_skip_settings(sample_excel):
    """Test skipping specific settings"""
    test_args = [
        "script.py",
        "--settings-file", sample_excel,
        "--sheet", "Street",
        "--car", "Test Car",
        "--creator", "Test Creator",
        "--skip-settings", "final_drive", "grip_front"
    ]
    
    with patch.object(sys, 'argv', test_args):
        assert main() == 0

def test_invalid_setting_values(sample_excel):
    """Test handling of invalid setting values"""
    df = pd.DataFrame({
        'Car': ['Invalid Car'],
        'Creator': ['Test Creator'],
        'Final Drive': ['invalid'],  # Invalid non-numeric value
        'Front Power Distrib': [2],
        'Grip Front': [0.3]
    })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, sheet_name='Street', index=False)
        converter = SettingsConverter(tmp.name)
        with pytest.raises(ValueError):
            converter.get_car_setup("Street", "Invalid Car", "Test Creator")

def test_multiple_sheets(test_data_dir):
    """Test handling multiple sheets in Excel file"""
    street_data = pd.DataFrame({
        'Car': ['Street Car'],
        'Creator': ['Test Creator'],
        'Final Drive': [0.05],
        'Front Power Distrib': [2]
    })
    
    race_data = pd.DataFrame({
        'Car': ['Race Car'],
        'Creator': ['Test Creator'],
        'Final Drive': [0.07],
        'Front Power Distrib': [3]
    })
    
    file_path = test_data_dir / "multi_sheet.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        street_data.to_excel(writer, sheet_name='Street', index=False)
        race_data.to_excel(writer, sheet_name='Race', index=False)
    
    converter = SettingsConverter(str(file_path))
    street_setup = converter.get_car_setup("Street", "Street Car", "Test Creator")
    race_setup = converter.get_car_setup("Race", "Race Car", "Test Creator")
    
    assert any(s.value == 0.05 for s in street_setup.settings if s.name == "final_drive")
    assert any(s.value == 0.07 for s in race_setup.settings if s.name == "final_drive")

def test_cli_arguments():
    """Test command line interface argument handling"""
    test_args = [
        "script.py",
        "--settings-file", "nonexistent.xlsx",  # Invalid file
        "--sheet", "Street",
        "--car", "Test Car",
        "--creator", "Test Creator"
    ]
    
    with patch.object(sys, 'argv', test_args):
        assert main() == 1  # Should return error code 1
    
    test_args = [
        "script.py",
        "--invalid-arg", "value"  # Invalid argument
    ]
    
    with patch.object(sys, 'argv', test_args), pytest.raises(SystemExit):
        main()

def test_complex_script_generation(complex_settings_excel):
    """Test script generation with complex settings"""
    converter = SettingsConverter(complex_settings_excel)
    setup = converter.get_car_setup("Street", "Car1", "Creator1")
    script = setup.generate_ahk_script()
    
    # Verify script structure and content
    assert "#SingleInstance Force" in script
    assert "SetKeyDelay" in script
    assert "^!s::" in script  # Hotkey
    assert "MsgBox, Settings applied!" in script
    
    # Verify all settings are included
    for setting in setup.settings:
        keystrokes = setting.get_keystrokes()
        if keystrokes:
            assert f"; Adjusting {setting.name}" in script

def test_non_zero_default_settings():
    """Test settings that have non-zero default values"""
    # Test front_power_distrib (60% to 20% range)
    settings = {
        "front_power_distrib": 40  # Target value
    }
    setup = CarSetup(settings)
    setting = next(s for s in setup.settings if s.name == "front_power_distrib")
    keystrokes = setting.get_keystrokes()
    # Should move right 20 times (60 -> 40)
    assert len(keystrokes) == 20
    assert all(k == "Right" for k in keystrokes)

    # Test front_brake_balance (80% to 40% range)
    settings = {
        "front_brake_balance": 60  # Target value
    }
    setup = CarSetup(settings)
    setting = next(s for s in setup.settings if s.name == "front_brake_balance")
    keystrokes = setting.get_keystrokes()
    # Should move right 20 times (80 -> 60)
    assert len(keystrokes) == 20
    assert all(k == "Right" for k in keystrokes)

def test_camber_increments():
    """Test camber settings that change in 0.01 increments"""
    settings = {
        "camber_front": 0.05,  # Should need 5 keystrokes
        "camber_rear": -0.03   # Should need 3 keystrokes
    }
    setup = CarSetup(settings)
    
    front_setting = next(s for s in setup.settings if s.name == "camber_front")
    rear_setting = next(s for s in setup.settings if s.name == "camber_rear")
    
    front_keystrokes = front_setting.get_keystrokes()
    rear_keystrokes = rear_setting.get_keystrokes()
    
    assert len(front_keystrokes) == 5
    assert all(k == "Right" for k in front_keystrokes)
    
    assert len(rear_keystrokes) == 3
    assert all(k == "Left" for k in rear_keystrokes)

def test_mixed_settings():
    """Test a combination of different setting types"""
    settings = {
        "front_power_distrib": 30,  # Non-zero default (60->30)
        "front_brake_balance": 50,  # Non-zero default (80->50)
        "camber_front": 0.02,       # 0.01 increments
        "grip_front": -5            # Regular delta-based setting
    }
    setup = CarSetup(settings)
    
    # Check power distribution
    power_setting = next(s for s in setup.settings if s.name == "front_power_distrib")
    power_keystrokes = power_setting.get_keystrokes()
    assert len(power_keystrokes) == 30  # 60->30 = 30 steps
    
    # Check brake balance
    brake_setting = next(s for s in setup.settings if s.name == "front_brake_balance")
    brake_keystrokes = brake_setting.get_keystrokes()
    assert len(brake_keystrokes) == 30  # 80->50 = 30 steps
    
    # Check camber
    camber_setting = next(s for s in setup.settings if s.name == "camber_front")
    camber_keystrokes = camber_setting.get_keystrokes()
    assert len(camber_keystrokes) == 2  # 0.02/0.01 = 2 steps
    
    # Check grip
    grip_setting = next(s for s in setup.settings if s.name == "grip_front")
    grip_keystrokes = grip_setting.get_keystrokes()
    assert len(grip_keystrokes) == 5
    assert all(k == "Left" for k in grip_keystrokes)

def test_auto_skip_settings(test_data_dir):
    """Test automatic skipping of unavailable settings"""
    df = pd.DataFrame({
        'Car': ['Test Car'],
        'Creator': ['Test Creator'],
        'Final Drive': ['--'],              # Should be skipped
        'Front Power Distrib': [40],        # Should be included
        'Grip Front': ['--'],               # Should be skipped
        'Front Brake Balance': [60],        # Should be included
        'Spring Front': ['nan'],            # Should be skipped
        'Spring Rear': [''],                # Should be skipped
        'Camber Front': [0.05]             # Should be included
    })
    
    file_path = test_data_dir / "skip_settings.xlsx"
    df.to_excel(file_path, sheet_name='Street', index=False)
    
    converter = SettingsConverter(str(file_path))
    setup = converter.get_car_setup("Street", "Test Car", "Test Creator")
    
    # Check that correct settings were included and skipped
    assert len(setup.settings) == 3  # Only power_distrib, brake_balance, and camber_front
    assert len(setup.auto_skipped_settings) > 0
    
    # Verify specific settings were skipped
    assert 'final_drive' in setup.auto_skipped_settings
    assert 'grip_front' in setup.auto_skipped_settings
    assert 'spring_front' in setup.auto_skipped_settings
    assert 'spring_rear' in setup.auto_skipped_settings
    
    # Generate script and verify structure
    script = setup.generate_ahk_script()
    script_lines = script.split('\n')
    
    # Check that skipped settings are documented in comments
    assert "; Auto-skipped settings (not available for this car):" in script_lines
    assert any("; - final_drive" in line for line in script_lines)
    
    # Count Down keystrokes - should be 2 (between the 3 available settings)
    down_count = script.count("Send {Down}")
    assert down_count == 2

def test_skipped_settings_script_flow():
    """Test that script correctly handles gaps between available settings"""
    settings = {
        'front_power_distrib': 40,    # First available setting
        'arb_front': 5,               # Much later in the list
        'camber_rear': 0.05           # Last setting
    }
    setup = CarSetup(settings)
    
    script = setup.generate_ahk_script()
    script_lines = script.split('\n')
    
    # Verify only two Down commands (between the three settings)
    down_count = script.count("Send {Down}")
    assert down_count == 2
    
    # Verify order of operations
    power_index = next(i for i, line in enumerate(script_lines) 
                      if "; Adjusting front_power_distrib" in line)
    arb_index = next(i for i, line in enumerate(script_lines) 
                    if "; Adjusting arb_front" in line)
    camber_index = next(i for i, line in enumerate(script_lines) 
                       if "; Adjusting camber_rear" in line)
    
    assert power_index < arb_index < camber_index  # Correct order
    
    # Verify intermediate settings are listed as skipped
    skipped_settings = [line.strip() for line in script_lines 
                       if line.strip().startswith("; - ")]
    assert len(skipped_settings) > 10  # Should have many skipped settings