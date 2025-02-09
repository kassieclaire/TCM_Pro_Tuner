#!/usr/bin/env python3
"""
The Crew Motorfest Settings Converter
Converts pro settings from Excel/CSV to AutoHotkey scripts for easy sharing and input.
"""

import pandas as pd
import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

# Configuration Constants
SETTINGS_FILE = "settings.xlsx"

# Setting change amounts per tick (customize these based on game values)
SETTING_INCREMENTS = {
    "final_drive": 0.01,
    "front_power_distrib": 1,
    "grip_front": 0.1,
    "grip_rear": 0.1,
    "front_brake_balance": 1,
    "brake_power": 1,
    "load_front": 0.1,
    "load_rear": 0.1,
    "spring_front": 0.1,
    "spring_rear": 0.1,
    "compression_front": 0.1,
    "compression_rear": 0.1,
    "rebound_front": 0.1,
    "rebound_rear": 0.1,
    "arb_front": 0.1,
    "arb_rear": 0.1,
    "camber_front": 0.1,
    "camber_rear": 0.1
}

# Whether each setting is a delta from default (True) or absolute value (False)
SETTING_IS_DELTA = {
    "final_drive": True,
    "front_power_distrib": True,
    "grip_front": True,
    "grip_rear": True,
    "front_brake_balance": True,
    "brake_power": True,
    "load_front": True,
    "load_rear": True,
    "spring_front": True,
    "spring_rear": True,
    "compression_front": True,
    "compression_rear": True,
    "rebound_front": True,
    "rebound_rear": True,
    "arb_front": True,
    "arb_rear": True,
    "camber_front": True,
    "camber_rear": True
}

@dataclass
class CarSetting:
    """Represents a single car setting with its value and metadata."""
    name: str
    value: float
    increment: float
    is_delta: bool

    def get_keystrokes(self) -> List[str]:
        """Convert setting value to required keystrokes."""
        if not self.value:
            return []
        
        ticks = round(self.value / self.increment)
        direction = "Right" if ticks > 0 else "Left"
        return [direction] * abs(ticks)

class CarSetup:
    """Manages a complete car setup with all its settings."""
    def __init__(self, settings_dict: Dict[str, float]):
        self.settings = []
        for name, value in settings_dict.items():
            if name in SETTING_INCREMENTS:
                setting = CarSetting(
                    name=name,
                    value=value,
                    increment=SETTING_INCREMENTS[name],
                    is_delta=SETTING_IS_DELTA[name]
                )
                self.settings.append(setting)

    def generate_ahk_script(self) -> str:
        """Generate AutoHotkey script for the car setup."""
        script_lines = [
            "#SingleInstance Force",
            "SetWorkingDir %A_ScriptDir%",
            "",
            "^!s::",  # Ctrl+Alt+S hotkey
            "{",
            "    SetKeyDelay, 50, 50  ; Adjust timing if needed",
            ""
        ]

        for setting in self.settings:
            keystrokes = setting.get_keystrokes()
            if keystrokes:
                script_lines.append(f"    ; Adjusting {setting.name}")
                script_lines.append("    Send {Down}")  # Move to next setting
                for key in keystrokes:
                    script_lines.append(f"    Send {{{key}}}")

        script_lines.extend([
            "",
            "    MsgBox, Settings applied!",
            "    return",
            "}"
        ])

        return "\n".join(script_lines)

class SettingsConverter:
    """Handles conversion of settings from Excel/CSV to AutoHotkey scripts."""
    def __init__(self, settings_file: str):
        self.settings_file = Path(settings_file)
        self._validate_file()

    def _validate_file(self):
        """Validate that the settings file exists and is the correct format."""
        if not self.settings_file.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_file}")
        if self.settings_file.suffix not in ['.xlsx', '.csv']:
            raise ValueError("Settings file must be .xlsx or .csv format")

    def get_car_setup(self, sheet_name: str, car_name: str, creator: str) -> CarSetup:
        """Retrieve settings for a specific car and creator."""
        if self.settings_file.suffix == '.xlsx':
            df = pd.read_excel(self.settings_file, sheet_name=sheet_name)
        else:
            df = pd.read_csv(self.settings_file)

        car_data = df[(df['Car'] == car_name) & (df['Creator'] == creator)]
        if car_data.empty:
            raise ValueError(f"No settings found for car '{car_name}' by '{creator}'")

        settings_dict = {
            col.lower().replace(' ', '_'): car_data[col].iloc[0]
            for col in car_data.columns
            if col.lower().replace(' ', '_') in SETTING_INCREMENTS
        }

        return CarSetup(settings_dict)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Convert car settings to AutoHotkey script")
    parser.add_argument("--settings-file", default=SETTINGS_FILE,
                      help="Path to settings Excel/CSV file")
    parser.add_argument("--sheet", required=True,
                      help="Sheet name (category) containing the car")
    parser.add_argument("--car", required=True,
                      help="Car name exactly as it appears in the sheet")
    parser.add_argument("--creator", required=True,
                      help="Setup creator name")
    parser.add_argument("--output", default="car_setup.ahk",
                      help="Output AutoHotkey script filename")
    parser.add_argument("--skip-settings", nargs='+', default=[],
                      help="Settings to skip (e.g., final_drive)")

    args = parser.parse_args()

    try:
        converter = SettingsConverter(args.settings_file)
        setup = converter.get_car_setup(args.sheet, args.car, args.creator)
        
        # Remove skipped settings
        setup.settings = [s for s in setup.settings if s.name not in args.skip_settings]
        
        # Generate and save script
        script = setup.generate_ahk_script()
        with open(args.output, 'w') as f:
            f.write(script)
        
        print(f"AutoHotkey script generated successfully: {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())