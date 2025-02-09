#!/usr/bin/env python3
import threading
import time
import enum
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk

class SimulatorInput(enum.Enum):
    UP = "Up"
    DOWN = "Down"
    LEFT = "Left"
    RIGHT = "Right"

@dataclass
class SettingRange:
    min_value: float
    max_value: float
    increment: float
    default_value: float = 0.0
    description: str = ""

class ProSetting:
    def __init__(self, name: str, setting_range: SettingRange):
        self.name = name
        self.range = setting_range
        self._current_value = setting_range.default_value
    
    @property
    def current_value(self) -> float:
        return self._current_value
    
    @current_value.setter
    def current_value(self, value: float):
        # Clamp value to valid range
        self._current_value = max(
            self.range.min_value,
            min(self.range.max_value, value)
        )
    
    def adjust(self, direction: SimulatorInput) -> bool:
        """Adjust setting value based on input. Returns True if value changed."""
        if direction not in (SimulatorInput.LEFT, SimulatorInput.RIGHT):
            return False
            
        old_value = self.current_value
        new_value = old_value
        
        if direction == SimulatorInput.RIGHT:
            # Moving right decreases value for some settings
            if self.name in ("front_power_distrib", "front_brake_balance"):
                new_value = old_value - self.range.increment
            else:
                new_value = old_value + self.range.increment
        else:
            # Moving left increases value for some settings
            if self.name in ("front_power_distrib", "front_brake_balance"):
                new_value = old_value + self.range.increment
            else:
                new_value = old_value - self.range.increment
        
        self.current_value = new_value  # This will clamp to valid range
        return old_value != self.current_value

class SimulatorState:
    def __init__(self, settings: List[ProSetting]):
        self.settings = settings
        self.current_setting_index = 0
        self.last_input_time = time.time()
        self.start_time = time.time()
        
    def get_current_setting(self) -> Optional[ProSetting]:
        if not self.settings:
            return None
        return self.settings[self.current_setting_index]
        
    def handle_input(self, input_type: SimulatorInput) -> bool:
        """Handle input and return True if state changed."""
        self.last_input_time = time.time()
        
        if input_type == SimulatorInput.UP:
            if self.current_setting_index > 0:
                self.current_setting_index -= 1
                return True
        elif input_type == SimulatorInput.DOWN:
            if self.current_setting_index < len(self.settings) - 1:
                self.current_setting_index += 1
                return True
        else:
            current_setting = self.get_current_setting()
            if current_setting:
                return current_setting.adjust(input_type)
        return False
    
    def is_timed_out(self) -> Tuple[bool, str]:
        current_time = time.time()
        if current_time - self.last_input_time > 10:
            return True, "No input received for 10 seconds"
        if current_time - self.start_time > 30:
            return True, "UI open for more than 30 seconds"
        return False, ""

def load_setting_ranges() -> Dict[str, SettingRange]:
    """Load setting ranges from CSV file."""
    settings_file = Path(__file__).parent / "pro_settings_description.csv"
    ranges = {}
    
    with open(settings_file, newline='', encoding='utf-8-sig') as csvfile:
        # Read first line to get column names
        first_line = csvfile.readline().strip()
        column_names = [col.strip() for col in first_line.split(',')]
        settings_column = next(col for col in column_names if 'Pro Settings' in col)
        
        # Reset file pointer and create reader
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                name = row[settings_column].lower().replace(" ", "_")
                range_str = row['Possible Values'].strip()
                desc = row['Description'].strip()
                
                # Parse range string (e.g., "-20% to 0%")
                min_str, max_str = range_str.split(" to ")
                min_val = float(min_str.strip("%")) / 100
                max_val = float(max_str.strip("%")) / 100
                
                # Set defaults for special cases
                default = 0.0
                if name == "power_distribution":
                    name = "front_power_distrib"  # Normalize name
                    default = 0.4  # 40%
                elif name == "brake_balance":
                    name = "front_brake_balance"  # Normalize name
                    default = 0.4  # 40%
                
                # Set increment
                increment = 0.01  # 1% for most settings
                if name in ("camber_front", "camber_rear"):
                    increment = 0.01  # Special increment for camber
                
                ranges[name] = SettingRange(
                    min_value=min_val,
                    max_value=max_val,
                    increment=increment,
                    default_value=default,
                    description=desc
                )
            except (ValueError, KeyError) as e:
                print(f"Warning: Could not parse setting {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
    
    if not ranges:
        raise ValueError("No valid settings found in CSV file")
    
    return ranges

class BaseSimulator:
    """Base class for both UI and CLI simulators."""
    def __init__(self, available_settings: List[str]):
        self.ranges = load_setting_ranges()
        self.settings = []
        
        # Create settings based on available ones
        for name in available_settings:
            norm_name = name.lower().replace(" ", "_")
            if norm_name in self.ranges:
                self.settings.append(ProSetting(norm_name, self.ranges[norm_name]))
        
        self.state = SimulatorState(self.settings)
        self.running = False
        self._timeout_thread = None
        self._timeout_lock = threading.Lock()
    
    def start(self):
        """Start the simulator and timeout monitoring."""
        with self._timeout_lock:
            self.running = True
            self._timeout_thread = threading.Thread(target=self._check_timeout)
            self._timeout_thread.daemon = True
            self._timeout_thread.start()
    
    def stop(self):
        """Stop the simulator."""
        with self._timeout_lock:
            if self.running:
                self.running = False
                if self._timeout_thread and self._timeout_thread.is_alive():
                    self._timeout_thread.join(timeout=1)
    
    def _check_timeout(self):
        """Monitor for timeouts."""
        while self.running:
            with self._timeout_lock:
                if not self.running:
                    break
                is_timeout, reason = self.state.is_timed_out()
                if is_timeout:
                    print(f"Timeout: {reason}")
                    self.handle_timeout(reason)
                    break
            time.sleep(0.1)
    
    def handle_input(self, input_type: SimulatorInput):
        """Handle input in the simulator."""
        if not self.running:
            return False
        return self.state.handle_input(input_type)
    
    def handle_timeout(self, reason: str):
        """Handle timeout event."""
        with self._timeout_lock:
            self.running = False
    
    def _display_current_setting(self):
        """Display the current setting state."""
        current = self.state.get_current_setting()
        if current:
            print(f"\r{current.name}: {current.current_value:.2%} ", end="")

class GUISimulator(BaseSimulator):
    """GUI version of the simulator."""
    def __init__(self, available_settings: List[str]):
        super().__init__(available_settings)
        self.root = tk.Tk()
        self.root.title("TCM Settings Simulator")
        
        # Setup ttk styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="white")
        self.style.configure("Highlight.TFrame", background="lightblue")
        
        # Create main frame
        self.frame = ttk.Frame(self.root, padding="10", style="TFrame")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create settings list
        self.settings_list = ttk.Frame(self.frame, style="TFrame")
        self.settings_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create sliders for each setting
        self.sliders = {}
        for i, setting in enumerate(self.settings):
            frame = ttk.Frame(self.settings_list, style="TFrame")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E))
            
            # Label
            label = ttk.Label(frame, text=setting.name.replace('_', ' ').title())
            label.grid(row=0, column=0, padx=5)
            
            # For power_distrib and brake_balance, flip min/max for intuitive slider direction
            if setting.name in ("front_power_distrib", "front_brake_balance"):
                from_val = setting.range.max_value
                to_val = setting.range.min_value
            else:
                from_val = setting.range.min_value
                to_val = setting.range.max_value
            
            # Slider
            slider = ttk.Scale(
                frame,
                from_=from_val,
                to=to_val,
                orient=tk.HORIZONTAL,
                value=setting.current_value
            )
            slider.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
            frame.grid_columnconfigure(1, weight=1)
            
            # Value label
            value_label = ttk.Label(frame, text=f"{setting.current_value:.2%}")
            value_label.grid(row=0, column=2, padx=5)
            
            # Store widgets
            self.sliders[setting.name] = (slider, value_label, frame)
            
            # Bind slider to update value
            def make_update_func(s=setting, sl=slider, vl=value_label):
                def update_value(event):
                    if self.running:
                        value = float(sl.get())  # Get current slider value
                        s.current_value = value
                        vl.configure(text=f"{s.current_value:.2%}")
                return update_value
            slider.bind("<ButtonRelease-1>", make_update_func())
        
        # Bind keyboard events
        self.root.bind('<Up>', lambda e: self._handle_key_event(SimulatorInput.UP))
        self.root.bind('<Down>', lambda e: self._handle_key_event(SimulatorInput.DOWN))
        self.root.bind('<Left>', lambda e: self._handle_key_event(SimulatorInput.LEFT))
        self.root.bind('<Right>', lambda e: self._handle_key_event(SimulatorInput.RIGHT))
        
        # Highlight current setting
        self._update_highlight()
    
    def _handle_key_event(self, input_type: SimulatorInput):
        """Handle keyboard input events."""
        if self.handle_input(input_type):
            current = self.state.get_current_setting()
            if current:
                # Update slider and value label
                slider, value_label, _ = self.sliders[current.name]
                slider.set(current.current_value)
                value_label.configure(text=f"{current.current_value:.2%}")
            self._update_highlight()
    
    def start(self):
        """Start the GUI simulator."""
        super().start()
        if self.running:
            self.root.mainloop()
    
    def stop(self):
        """Stop the GUI simulator."""
        super().stop()
        self.root.quit()
    
    def handle_input(self, input_type: SimulatorInput):
        """Handle input and update GUI."""
        if super().handle_input(input_type):
            current = self.state.get_current_setting()
            if current:
                # Update slider and value label
                slider, value_label, _ = self.sliders[current.name]
                slider.set(current.current_value)
                value_label.configure(text=f"{current.current_value:.2%}")
            self._update_highlight()
            return True
        return False
    
    def handle_timeout(self, reason: str):
        """Handle timeout in GUI."""
        super().handle_timeout(reason)
        self.root.quit()
    
    def _update_highlight(self):
        """Update the highlighted setting."""
        if not self.running:
            return
        current = self.state.get_current_setting()
        for name, (_, _, frame) in self.sliders.items():
            frame.configure(style='Highlight.TFrame' if name == current.name else 'TFrame')

class CLISimulator(BaseSimulator):
    """Command-line version of the simulator."""
    def __init__(self, available_settings: List[str]):
        super().__init__(available_settings)
        self._key_thread = None
    
    def start(self):
        """Start the CLI simulator."""
        super().start()
        self._display_current_setting()
        
        # Start key input thread
        self._key_thread = threading.Thread(target=self._handle_key_input)
        self._key_thread.daemon = True
        self._key_thread.start()
        
        # Wait for simulator to stop
        while self.running:
            time.sleep(0.1)
    
    def stop(self):
        """Stop the CLI simulator."""
        super().stop()
        if self._key_thread:
            self._key_thread.join()
    
    def handle_input(self, input_type: SimulatorInput):
        """Handle input and update display."""
        if super().handle_input(input_type):
            self._display_current_setting()
    
    def _display_current_setting(self):
        """Display the current setting."""
        current = self.state.get_current_setting()
        if current:
            print(f"\r{current.name}: {current.current_value:.2%} ", end='')
    
    def _handle_key_input(self):
        """Handle keyboard input in CLI."""
        try:
            import msvcrt  # Windows
            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    self._process_key(key)
        except ImportError:
            import sys, tty, termios  # Unix
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                while self.running:
                    key = sys.stdin.read(1)
                    self._process_key(key)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _process_key(self, key):
        """Process a keyboard input."""
        key_mapping = {
            b'H': SimulatorInput.UP,    # Up arrow
            b'P': SimulatorInput.DOWN,  # Down arrow
            b'K': SimulatorInput.LEFT,  # Left arrow
            b'M': SimulatorInput.RIGHT, # Right arrow
            '\x1b[A': SimulatorInput.UP,    # Unix Up
            '\x1b[B': SimulatorInput.DOWN,  # Unix Down
            '\x1b[D': SimulatorInput.LEFT,  # Unix Left
            '\x1b[C': SimulatorInput.RIGHT, # Unix Right
        }
        
        if key in key_mapping:
            self.handle_input(key_mapping[key])

def main():
    """Main entry point for the simulator."""
    import argparse
    parser = argparse.ArgumentParser(description="TCM Settings Simulator")
    parser.add_argument('--cli', action='store_true', help="Use CLI interface")
    parser.add_argument('--settings', nargs='+', help="List of available settings")
    args = parser.parse_args()
    
    # Default settings if none provided
    if not args.settings:
        args.settings = [
            "final_drive",
            "front_power_distrib",
            "grip_front",
            "front_brake_balance"
        ]
    
    simulator = CLISimulator(args.settings) if args.cli else GUISimulator(args.settings)
    try:
        simulator.start()
    except KeyboardInterrupt:
        pass
    finally:
        simulator.stop()

if __name__ == "__main__":
    main()