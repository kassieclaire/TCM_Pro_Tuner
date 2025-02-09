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

# Setting change amounts per tick
SETTING_INCREMENTS = {
    "final_drive": 1,
    "front_power_distrib": 1,  # Changes by 1% per tick
    "grip_front": 1,
    "grip_rear": 1,
    "front_brake_balance": 1,  # Changes by 1% per tick
    "brake_power": 1,
    "load_front": 1,
    "load_rear": 1,
    "spring_front": 1,
    "spring_rear": 1,
    "compression_front": 1,
    "compression_rear": 1,
    "rebound_front": 1,
    "rebound_rear": 1,
    "arb_front": 1,
    "arb_rear": 1,
    "camber_front": 0.01,  # Special case: changes by 0.01 per tick
    "camber_rear": 0.01    # Special case: changes by 0.01 per tick
}

# Settings with non-zero defaults and their ranges
SETTING_DEFAULTS = {
    "front_power_distrib": 60,  # Starts at 60%, decrease to lower value
    "front_brake_balance": 80   # Starts at 80%, decrease to lower value
}

# Whether each setting needs to be reset to start value first
SETTING_NEEDS_RESET = {
    "front_power_distrib": True,
    "front_brake_balance": True
}

# Whether each setting is a delta from default (True) or absolute value (False)
SETTING_IS_DELTA = {
    "final_drive": True,
    "front_power_distrib": False,  # Uses absolute values
    "grip_front": True,
    "grip_rear": True,
    "front_brake_balance": False,  # Uses absolute values
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
        keystrokes = []
        
        # Handle settings with non-zero defaults
        if self.name in SETTING_DEFAULTS:
            start_value = SETTING_DEFAULTS[self.name]
            # Calculate ticks needed (moving right decreases value)
            ticks = round((start_value - self.value) / self.increment)
            if ticks > 0:
                keystrokes.extend(["Right"] * ticks)
            elif ticks < 0:
                keystrokes.extend(["Left"] * abs(ticks))
            return keystrokes
        
        # For regular delta-based settings
        if not self.value:
            return []
        
        ticks = round(self.value / self.increment)
        direction = "Right" if ticks > 0 else "Left"
        return [direction] * abs(ticks)

class CarSetup:
    """Manages a complete car setup with all its settings."""
    def __init__(self, settings_dict: Dict[str, float]):
        self.settings = []
        self.auto_skipped_settings = []
        
        # Get all possible settings in their expected order
        all_settings = [
            'final_drive', 'front_power_distrib', 'grip_front', 'grip_rear',
            'front_brake_balance', 'brake_power', 'load_front', 'load_rear',
            'spring_front', 'spring_rear', 'compression_front', 'compression_rear',
            'rebound_front', 'rebound_rear', 'arb_front', 'arb_rear',
            'camber_front', 'camber_rear'
        ]
        
        # Track the last included setting to know when to send Down
        last_included_setting = None
        
        for name in all_settings:
            if name in settings_dict and name in SETTING_INCREMENTS:
                value = settings_dict[name]
                # Create setting with appropriate metadata
                setting = CarSetting(
                    name=name,
                    value=value,
                    increment=SETTING_INCREMENTS[name],
                    is_delta=(name not in SETTING_DEFAULTS)
                )
                self.settings.append(setting)
                last_included_setting = name
            else:
                self.auto_skipped_settings.append(name)

    def generate_ahk_script(self) -> str:
        """Generate AutoHotkey script for the car setup."""
        script_lines = [
            "#SingleInstance Force",
            "SetWorkingDir %A_ScriptDir%",
            "",
            "; Command line mode support",
            "if (A_Args.Length() > 0 && A_Args[1] = \"--cli\") {",
            "    SetTimer, ApplySettings, -100  ; Run after 100ms",
            "    return",
            "}",
            "",
            "; Default starting positions:",
            "; - Front Power Distribution: Starts at 60% (right to decrease)",
            "; - Front Brake Balance: Starts at 80% (right to decrease)",
            "; - All other settings: Start at 0",
            "",
            "; Auto-skipped settings (not available for this car):"
        ]
        
        # Add comments for skipped settings
        for setting in self.auto_skipped_settings:
            script_lines.append(f"; - {setting}")
        
        script_lines.extend([
            "",
            "ApplySettings:",
            "{",
            "    SetKeyDelay, 50, 50  ; Adjust timing if needed",
            ""
        ])

        # Track if we need to move to the next setting
        needs_down = False
        
        for setting in self.settings:
            keystrokes = setting.get_keystrokes()
            if keystrokes:
                if setting.name in SETTING_DEFAULTS:
                    script_lines.append(f"    ; Adjusting {setting.name} (from {SETTING_DEFAULTS[setting.name]}%)")
                else:
                    script_lines.append(f"    ; Adjusting {setting.name}")
                
                if needs_down:
                    script_lines.append("    Send {Down}")  # Move to next setting
                for key in keystrokes:
                    script_lines.append(f"    Send {{{key}}}")
                needs_down = True

        script_lines.extend([
            "",
            "    if (A_Args.Length() > 0 && A_Args[1] = \"--cli\") {",
            "        ExitApp",  # Exit immediately in CLI mode
            "    } else {",
            "        MsgBox, Settings applied!",
            "    }",
            "    return",
            "}"
        ])

        return "\n".join(script_lines)

class SettingsConverter:
    """Handles conversion of settings from Excel/CSV to AutoHotkey scripts."""
    def __init__(self, settings_file: str):
        self.settings_file = Path(settings_file)
        self._validate_file()
        self._load_data()

    def _validate_file(self):
        if not self.settings_file.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_file}")
        if self.settings_file.suffix not in ['.xlsx', '.csv']:
            raise ValueError("Settings file must be .xlsx or .csv format")

    def _load_data(self):
        """Load and validate data from the settings file."""
        try:
            if self.settings_file.suffix == '.xlsx':
                self.data = {}
                df = pd.read_excel(self.settings_file, sheet_name=None)
                
                # Filter vehicle sheets
                valid_categories = ['STREET TIER 1', 'STREET TIER 2', 'RACING', 'DRIFT', 
                                  'RALLY', 'RALLY RAID', 'HYPERCAR', 'DRAGSTER', 'ALPHA', 
                                  'DEMOLITION DERBY', 'MONSTER TRUCK', 'MOTO']
                
                # Setting column identifiers
                setting_identifiers = {
                    'Final Drive': 'final_drive',
                    'Front Power Distrib': 'front_power_distrib',
                    'Front Brake Balance': 'front_brake_balance',
                    'Brake Power': 'brake_power',
                    'Grip Front': 'grip_front',
                    'Grip Rear': 'grip_rear',
                    'Load Front': 'load_front',
                    'Load Rear': 'load_rear',
                    'Spring Front': 'spring_front',
                    'Spring Rear': 'spring_rear',
                    'Compression Front': 'compression_front',
                    'Compression Rear': 'compression_rear',
                    'Rebound Front': 'rebound_front',
                    'Rebound Rear': 'rebound_rear',
                    'ARB Front': 'arb_front',
                    'ARB Rear': 'arb_rear',
                    'Camber Front': 'camber_front',
                    'Camber Rear': 'camber_rear'
                }
                
                # Non-car values to skip
                skip_values = {'nan', 'NaN', '--', '', 'WELCOME', 'SETTINGS', 'CAR NAME'}
                
                # Known manufacturers to check
                manufacturers = {
                    'BMW', 'AUDI', 'MERCEDES', 'PORSCHE', 'FORD', 'CHEVROLET',
                    'DODGE', 'VOLKSWAGEN', 'MAZDA', 'NISSAN', 'HONDA', 'PLYMOUTH',
                    'MITSUBISHI', 'PROTO', 'JAGUAR', 'ALFA ROMEO', 'DELOREAN',
                    'BUICK', 'CADILLAC', 'FERRARI', 'HUMMER', 'JEEP', 'MASERATI',
                    'MINI', 'PONTIAC', 'RENAULT', 'SHELBY', 'TOYOTA', 'ABARTH',
                    'ASTON MARTIN', 'BUGATTI', 'CHRYSLER', 'LANCIA', 'LAND ROVER'
                }
                
                for sheet_name in valid_categories:
                    if sheet_name in df:
                        sheet_data = df[sheet_name]
                        self.data[sheet_name] = {}
                        
                        # Find setting columns
                        setting_columns = {}
                        for col in sheet_data.columns:
                            col_str = str(col)
                            if any(setting in col_str for setting in setting_identifiers.keys()):
                                matched_setting = next(s for s in setting_identifiers.keys() if s in col_str)
                                setting_columns[col] = setting_identifiers[matched_setting]
                        
                        # Process each row
                        current_car = None
                        current_settings = {}
                        
                        for idx, row in sheet_data.iterrows():
                            # Check each column for car names or settings
                            for col in sheet_data.columns:
                                value = str(row[col]).strip()
                                if not value or value in skip_values:
                                    continue
                                
                                # Check if this is a car name
                                for mfr in manufacturers:
                                    if value.startswith(mfr):
                                        # Skip manufacturer grouping rows that contain "/"
                                        if "/" in value:
                                            break
                                            
                                        # Found a car, save previous car's settings if any
                                        if current_car and current_settings:
                                            mfr_name = next(m for m in manufacturers if current_car.startswith(m))
                                            if mfr_name not in self.data[sheet_name]:
                                                self.data[sheet_name][mfr_name] = {}
                                            self.data[sheet_name][mfr_name][current_car] = current_settings
                                        
                                        # Start new car
                                        current_car = value
                                        current_settings = {}
                                        break
                                
                                # If this is a setting column, try to get the value
                                if col in setting_columns:
                                    try:
                                        if value not in ['--', 'nan', 'NaN', '']:
                                            setting_value = pd.to_numeric(value)
                                            if pd.notna(setting_value):
                                                current_settings[setting_columns[col]] = float(setting_value)
                                    except:
                                        continue
                        
                        # Save last car's settings
                        if current_car and current_settings:
                            mfr_name = next(m for m in manufacturers if current_car.startswith(m))
                            if mfr_name not in self.data[sheet_name]:
                                self.data[sheet_name][mfr_name] = {}
                            self.data[sheet_name][mfr_name][current_car] = current_settings
                
                # Remove empty categories and manufacturers
                for sheet_name in list(self.data.keys()):
                    # Remove manufacturers with no models
                    self.data[sheet_name] = {mfr: models 
                                           for mfr, models in self.data[sheet_name].items() 
                                           if models}
                    # Remove empty sheets
                    if not self.data[sheet_name]:
                        del self.data[sheet_name]
                
                if not self.data:
                    raise ValueError("No valid vehicle data found in the file")
            else:
                raise ValueError("Only Excel files are supported")
                
        except Exception as e:
            raise ValueError(f"Error loading data: {str(e)}")

    def list_sheets(self):
        """List all available sheets/categories."""
        return list(self.data.keys())

    def list_cars(self, sheet_name: str):
        """List all cars in a specific sheet/category."""
        if sheet_name not in self.data:
            raise ValueError(f"Category '{sheet_name}' not found")
        
        output_lines = []
        for manufacturer in sorted(self.data[sheet_name].keys()):
            if manufacturer not in ['UNKNOWN']:  # Skip unknown manufacturer category
                models = self.data[sheet_name][manufacturer]
                if models:  # Only show manufacturers that have models
                    output_lines.append(f"\n{manufacturer}")
                    for model in sorted(models.keys()):
                        output_lines.append(f"  - {model}")
        
        return output_lines

    def get_car_setup(self, sheet_name: str, manufacturer: str, model: str) -> CarSetup:
        """Retrieve settings for a specific car."""
        if sheet_name not in self.data:
            raise ValueError(f"Category '{sheet_name}' not found")
        
        if manufacturer not in self.data[sheet_name]:
            raise ValueError(f"Manufacturer '{manufacturer}' not found in category '{sheet_name}'")
            
        if model not in self.data[sheet_name][manufacturer]:
            raise ValueError(f"Model '{model}' not found for manufacturer '{manufacturer}' in category '{sheet_name}'")
        
        return CarSetup(self.data[sheet_name][manufacturer][model])

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert car settings to AutoHotkey script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--settings-file", default=SETTINGS_FILE,
                      help="Path to settings Excel/CSV file")
    parser.add_argument("--category", 
                      help="Vehicle category (e.g., STREET TIER 1, RACING, DRIFT)")
    parser.add_argument("--manufacturer",
                      help="Vehicle manufacturer name")
    parser.add_argument("--model",
                      help="Car model name")
    parser.add_argument("--output", default="car_setup.ahk",
                      help="Output AutoHotkey script filename")
    parser.add_argument("--skip-settings", nargs='+', default=[],
                      help="Settings to skip (e.g., final_drive)")
    parser.add_argument("--list-categories", action="store_true",
                      help="List all available vehicle categories")
    parser.add_argument("--list-cars", action="store_true",
                      help="List all available cars in the specified category")

    try:
        args = parser.parse_args()
        converter = SettingsConverter(args.settings_file)

        if args.list_categories:
            print("\nAvailable vehicle categories:")
            for category in converter.list_sheets():
                print(f"  - {category}")
            return 0

        if args.list_cars:
            if not args.category:
                print("\nError: --category argument is required when using --list-cars")
                return 1
            try:
                cars = converter.list_cars(args.category)
                print(f"\nAvailable cars in category '{args.category}':")
                for line in cars:
                    print(line)
                return 0
            except ValueError as e:
                print(f"\nError: {str(e)}")
                return 1

        # Validate required arguments for script generation
        if not all([args.category, args.manufacturer, args.model]):
            print("\nError: --category, --manufacturer, and --model are required for script generation")
            parser.print_help()
            return 1

        setup = converter.get_car_setup(args.category, args.manufacturer, args.model)
        
        # Remove skipped settings
        setup.settings = [s for s in setup.settings if s.name not in args.skip_settings]
        
        # Generate and save script
        script = setup.generate_ahk_script()
        with open(args.output, 'w') as f:
            f.write(script)
        
        print(f"\nAutoHotkey script generated successfully: {args.output}")
        print(f"Settings applied: {len(setup.settings)}")
        if setup.auto_skipped_settings:
            print("\nThe following settings were automatically skipped (not available for this car):")
            for setting in setup.auto_skipped_settings:
                print(f"  - {setting}")
        print("\nHotkey: Ctrl+Alt+S")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())