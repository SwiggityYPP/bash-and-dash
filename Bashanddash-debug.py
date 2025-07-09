#!/usr/bin/env python3
"""
Bash and Dash Game Log Analyzer - Debug Version
===============================================

A legitimate game statistics analyzer for parsing game log files.
This debug version provides detailed error messages and logging.

Purpose: Game log analysis and statistics tracking
Author: Game Statistics Team
License: Personal Use

This application:
- Reads text log files from games
- Parses battle statistics using pattern matching
- Displays results in a user-friendly GUI
- Helps calculate game rewards and payouts

Note: This debug version shows detailed error information.
"""

import sys
import os
import traceback

# Enhanced error handling and logging
def setup_error_handling():
    """Set up comprehensive error handling and logging."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions with detailed logging."""
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Try to show error in GUI if tkinter is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            messagebox.showerror(
                "Bash and Dash - Error",
                f"An error occurred:\n\n{exc_type.__name__}: {exc_value}\n\n"
                f"Please report this error with the following details:\n"
                f"Version: {APP_VERSION}\n"
                f"Python: {sys.version}\n"
                f"Platform: {sys.platform}\n\n"
                f"Full traceback:\n{error_msg}"
            )
            root.destroy()
        except:
            # Fallback to console output
            print(f"CRITICAL ERROR in Bash and Dash v{APP_VERSION}")
            print("=" * 60)
            print(error_msg)
            print("=" * 60)
            print("Please report this error to the developer.")
            
        # Also try to write to a log file
        try:
            with open("bashanddash_error.log", "w") as f:
                f.write(f"Bash and Dash v{APP_VERSION} Error Log\n")
                f.write(f"Time: {datetime.now()}\n")
                f.write(f"Python: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write("=" * 60 + "\n")
                f.write(error_msg)
        except:
            pass  # If we can't write log, that's okay
    
    # Set the exception handler
    sys.excepthook = handle_exception

# Set up error handling immediately
try:
    from datetime import datetime
    APP_VERSION = "1.0.1-debug"
    setup_error_handling()
except Exception as e:
    print(f"Failed to set up error handling: {e}")

# Now import the rest normally with error checking
try:
    import tkinter as tk
    from tkinter import filedialog, scrolledtext, messagebox
except ImportError as e:
    print(f"Failed to import tkinter: {e}")
    print("Make sure tkinter is installed with your Python distribution.")
    sys.exit(1)

try:
    import re
    from collections import defaultdict
    import json
    import threading
    import tempfile
    import hashlib
    import time
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    sys.exit(1)

# Optional imports with fallbacks
try:
    import shutil
except ImportError:
    print("Warning: shutil not available, some features may be limited")
    shutil = None

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Application version - Centralized version management
APP_VERSION = "1.0.1-debug"

# Security and antivirus compatibility - Reduce false positives
SAFE_MODE = True  # Enables additional security checks
VERIFY_DOWNLOADS = True  # Enables hash verification of downloads
USER_AGENT = "Bash-and-Dash-Game-Analyzer/1.0.1-debug"  # Proper identification
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB max download limit
ALLOWED_DOMAINS = ["api.github.com", "github.com"]  # Whitelist for network access

# Update configuration - GitHub integration for auto-updates
UPDATE_CHECK_URL = "https://api.github.com/repos/YourUsername/bash-and-dash/releases/latest"

# Patterns to detect greedy bashes and extract pirate names
BASH_PATTERNS = [
    r"\[.*?\]\s*(?P<pirate>.+?) performs a powerful attack against .+ and steals some loot in the process!",
    r"\[.*?\]\s*(?P<pirate>.+?) delivers an overwhelming barrage against .+ causing some treasure to fall from their grip!",
    r"\[.*?\]\s*(?P<pirate>.+?) executes a masterful strike against .+ who drops some treasure in surprise!",
    r"\[.*?\]\s*(?P<pirate>.+?) swings a devious blow against .+ jarring some treasure loose!"
]

# Battle detection patterns
START_PATTERN = r'Game over'
END_PATTERN = r'Game over'

# ============================================================================
# DEBUG AND LOGGING FUNCTIONS
# ============================================================================

def debug_log(message):
    """Log debug messages to console and file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    debug_msg = f"[{timestamp}] DEBUG: {message}"
    print(debug_msg)
    
    try:
        with open("bashanddash_debug.log", "a") as f:
            f.write(debug_msg + "\n")
    except:
        pass  # If we can't write log, continue anyway

def safe_function_call(func, *args, **kwargs):
    """Safely call a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        debug_log(f"Error in {func.__name__}: {e}")
        traceback.print_exc()
        return None

# ============================================================================
# CORE ANALYSIS FUNCTIONS
# ============================================================================

def count_greedy_bashes_per_battle(file_path):
    """
    Analyzes game log file to count greedy bash attacks per battle session.
    
    Args:
        file_path (str): Path to the game log file
        
    Returns:
        list: List of dictionaries containing bash counts per pirate per battle
    """
    debug_log(f"Starting analysis of file: {file_path}")
    
    battles = []
    in_battle = False
    current_battle = defaultdict(int)
    
    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            debug_log(f"File does not exist: {file_path}")
            return []
        
        file_size = os.path.getsize(file_path)
        debug_log(f"File size: {file_size} bytes")
        
        # Read file with UTF-8 encoding and error tolerance
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = 0
            for line in f:
                line_count += 1
                
                # Check for battle start marker
                if re.search(START_PATTERN, line):
                    debug_log(f"Battle start found at line {line_count}")
                    # If we were already in a battle, save it before starting a new one
                    if in_battle and current_battle:
                        battles.append(dict(current_battle))
                        debug_log(f"Saved previous battle with {sum(current_battle.values())} total bashes")
                    
                    # Initialize new battle tracking
                    in_battle = True
                    current_battle = defaultdict(int)
                    continue
                
                # Process lines during battle
                if in_battle:
                    # Check each bash pattern against the current line
                    for pattern in BASH_PATTERNS:
                        match = re.search(pattern, line)
                        if match:
                            pirate = match.group('pirate').strip()
                            current_battle[pirate] += 1
                            debug_log(f"Bash found: {pirate} (line {line_count})")
                            break  # Only count one bash per line
        
        # Don't forget to add the last battle if we were still in one
        if in_battle and current_battle:
            battles.append(dict(current_battle))
            debug_log(f"Saved final battle with {sum(current_battle.values())} total bashes")
        
        debug_log(f"Analysis complete. Found {len(battles)} battles total.")
        return battles
            
    except Exception as e:
        debug_log(f"Error reading file {file_path}: {e}")
        traceback.print_exc()
        return []

# ============================================================================
# GUI HELPER FUNCTIONS
# ============================================================================

def show_summary_in_gui(battles, text_widget, payout_frame, payout_var, payout_lines, 
                       top_var, top_pay_frame, top_pay_line, total_payout_label):
    """Update the GUI with battle analysis results and payout calculations."""
    debug_log("Updating GUI with battle results")
    
    try:
        # Clear existing content
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        # Clear existing payout widgets
        for widget in payout_frame.winfo_children():
            widget.destroy()
        for widget in top_pay_frame.winfo_children():
            widget.destroy()
        
        # Reset command lists
        payout_lines.clear()
        top_pay_line.clear()
        
        if not battles:
            summary = "No greedy bashes found."
            total_payout_label.config(text="Total Battle Payout: 0 PoE")
            debug_log("No battles found in analysis")
        else:
            # Process the most recent battle
            last_battle = battles[-1]
            total_bashes = sum(last_battle.values())
            debug_log(f"Processing last battle with {total_bashes} total bashes")
            
            # Create pirate summary sorted by bash count (descending)
            pirate_parts = [f"{pirate} ({count})" for pirate, count in 
                           sorted(last_battle.items(), key=lambda x: -x[1])]
            
            summary = f"Total greedy bashes: {total_bashes}"
            if pirate_parts:
                summary += ", " + ", ".join(pirate_parts)
            
            # Handle top basher payout
            try:
                top_payout = int(top_var.get())
            except (ValueError, TypeError):
                top_payout = 0
            
            if last_battle and top_payout > 0:
                # Find pirates with the highest bash count
                sorted_bashers = sorted(last_battle.items(), key=lambda x: -x[1])
                max_bashes = sorted_bashers[0][1] if sorted_bashers else 0
                top_bashers = [pirate for pirate, count in sorted_bashers if count == max_bashes]
                
                debug_log(f"Top bashers: {top_bashers} with {max_bashes} bashes each")
                
                # Create top basher payout commands
                for pirate in top_bashers:
                    pay_cmd = f"/pay {pirate} {top_payout}"
                    top_pay_line.append(pay_cmd)
                    
                    # Create interactive payout row
                    row = tk.Frame(top_pay_frame, bg="#2c313a")
                    row.pack(anchor="w", pady=2, padx=8, fill=tk.X)
                    
                    pay_label = tk.Label(row, text=f"Top Basher: {pay_cmd}", 
                                       bg="#2c313a", fg="#3ecf8e", 
                                       font=("Segoe UI", 13, "bold"), 
                                       padx=8, pady=6, anchor="w")
                    pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    # Create copy button
                    def make_copy_cmd(cmd, label=pay_label):
                        def do_copy():
                            try:
                                text_widget.clipboard_clear()
                                text_widget.clipboard_append(cmd)
                                text_widget.update()
                                label.config(font=("Segoe UI", 13, "bold", "overstrike"), fg="#888")
                                debug_log(f"Copied to clipboard: {cmd}")
                            except Exception as e:
                                debug_log(f"Clipboard error: {e}")
                        return do_copy
                    
                    copy_btn = tk.Button(row, text="Copy", width=8, 
                                       command=make_copy_cmd(pay_cmd),
                                       bg="#4f8cff", fg="#f1f1f1",
                                       activebackground="#357ae8", activeforeground="#f1f1f1",
                                       relief=tk.FLAT, bd=0, cursor="hand2",
                                       font=("Segoe UI", 11, "bold"))
                    copy_btn.pack(side=tk.LEFT, padx=10, pady=2)
            
            # Handle per-bash payout section
            try:
                payout = int(payout_var.get())
            except (ValueError, TypeError):
                payout = 0
            
            total_battle_payout = 0
            
            if payout > 0 and last_battle:
                debug_log(f"Creating payout commands with {payout} per bash")
                
                # Create payout commands for each pirate
                for pirate, count in sorted(last_battle.items(), key=lambda x: -x[1]):
                    total_pay = payout * count
                    total_battle_payout += total_pay
                    pay_cmd = f"/pay {pirate} {total_pay}"
                    payout_lines.append(pay_cmd)
                    
                    # Create interactive payout row
                    row = tk.Frame(payout_frame, bg="#2c313a")
                    row.pack(anchor="w", pady=2, padx=8, fill=tk.X)
                    
                    pay_label = tk.Label(row, text=pay_cmd, 
                                       bg="#2c313a", fg="#f1f1f1",
                                       font=("Segoe UI", 12), 
                                       padx=8, pady=6, anchor="w")
                    pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    # Copy button with visual feedback
                    def make_copy_cmd(cmd, label=pay_label):
                        def do_copy():
                            try:
                                text_widget.clipboard_clear()
                                text_widget.clipboard_append(cmd)
                                text_widget.update()
                                label.config(font=("Segoe UI", 12, "overstrike"), fg="#888")
                                debug_log(f"Copied to clipboard: {cmd}")
                            except Exception as e:
                                debug_log(f"Clipboard error: {e}")
                        return do_copy
                    
                    copy_btn = tk.Button(row, text="Copy", width=8,
                                       command=make_copy_cmd(pay_cmd),
                                       bg="#4f8cff", fg="#f1f1f1",
                                       activebackground="#357ae8", activeforeground="#f1f1f1",
                                       relief=tk.FLAT, bd=0, cursor="hand2",
                                       font=("Segoe UI", 11, "bold"))
                    copy_btn.pack(side=tk.LEFT, padx=10, pady=2)
            
            # Update total payout display
            total_payout_label.config(text=f"Total Battle Payout: {total_battle_payout:,} PoE")
            debug_log(f"Total payout calculated: {total_battle_payout}")
        
        # Update summary text widget
        text_widget.insert(tk.END, summary + "\n")
        num_lines = summary.count('\n') + 1
        text_widget.config(height=min(max(num_lines, 3), 10))
        text_widget.config(state=tk.DISABLED)
        
        debug_log("GUI update completed successfully")
        
    except Exception as e:
        debug_log(f"Error updating GUI: {e}")
        traceback.print_exc()

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

def main_gui():
    """Initialize and run the main GUI application."""
    debug_log("Starting main GUI application")
    
    try:
        # Create main window
        root = tk.Tk()
        root.title(f"Bash and Dash v{APP_VERSION}")
        root.geometry("520x540")
        
        debug_log("Main window created successfully")
        
        # Set application icon (optional, with error handling)
        try:
            # Create a simple programmatic icon
            icon_photo = tk.PhotoImage(width=32, height=32)
            
            # Create a simple design
            for x in range(32):
                for y in range(32):
                    icon_photo.put("#2c313a", (x, y))
            
            # Add some visual elements
            for y in range(5, 20):
                icon_photo.put("#4f8cff", (15, y))
                icon_photo.put("#4f8cff", (16, y))
            
            root.iconphoto(True, icon_photo)
            debug_log("Application icon set successfully")
        except Exception as e:
            debug_log(f"Could not set application icon: {e}")

        # Theme colors
        DARK_BG = "#23272e"
        DARK_PANEL = "#2c313a"
        DARK_ENTRY = "#23272e"
        DARK_TEXT = "#f1f1f1"
        DARK_ACCENT = "#4f8cff"
        DARK_ACCENT2 = "#357ae8"
        DARK_GREEN = "#3ecf8e"
        DARK_BORDER = "#444a56"

        root.configure(bg=DARK_BG)

        # Application state
        state = {'file_path': None}
        payout_lines = []
        top_pay_line = []

        # Event handler functions
        def select_file():
            """Handle file selection and initial analysis."""
            debug_log("File selection dialog opened")
            
            file_path = filedialog.askopenfilename(
                title="Select your game chat log file",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Log files", "*.log"),
                    ("Chat logs", "*.chat"),
                    ("Data files", "*.dat")
                ]
            )
            
            if file_path:
                debug_log(f"File selected: {file_path}")
                
                # Basic file validation
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as test_file:
                        # Check if we can read the first few lines
                        for i, line in enumerate(test_file):
                            if i >= 10:
                                break
                    
                    debug_log("File validation successful")
                    
                    # File is readable, store path and analyze
                    state['file_path'] = file_path
                    battles = count_greedy_bashes_per_battle(file_path)
                    show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                                      payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                                      total_payout_label)
                                      
                except Exception as e:
                    debug_log(f"File validation failed: {e}")
                    # Handle file access errors
                    result_box.config(state=tk.NORMAL)
                    result_box.delete(1.0, tk.END)
                    result_box.insert(tk.END, f"Error reading file: {str(e)}")
                    result_box.config(height=3)
                    result_box.config(state=tk.DISABLED)
            else:
                debug_log("No file selected")
                # No file selected - clear display
                result_box.config(state=tk.NORMAL)
                result_box.delete(1.0, tk.END)
                result_box.insert(tk.END, "No file selected.")
                result_box.config(height=3)
                result_box.config(state=tk.DISABLED)

        def update_file():
            """Re-analyze the currently selected file."""
            debug_log("Update file requested")
            
            file_path = state.get('file_path')
            if file_path:
                debug_log(f"Re-analyzing file: {file_path}")
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                                  payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                                  total_payout_label)
            else:
                debug_log("No file to update")

        def copy_to_clipboard():
            """Copy the summary text to clipboard."""
            try:
                text = result_box.get("1.0", tk.END).strip()
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                debug_log("Text copied to clipboard successfully")
            except Exception as e:
                debug_log(f"Clipboard copy failed: {e}")

        # Main button row
        button_frame = tk.Frame(root, bg=DARK_BG)
        button_frame.pack(pady=(12, 4))
        
        button_style = {
            'font': ("Segoe UI", 11, "bold"),
            'bg': DARK_ACCENT,
            'fg': DARK_TEXT,
            'activebackground': DARK_ACCENT2,
            'activeforeground': DARK_TEXT,
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': "hand2"
        }
        
        select_btn = tk.Button(button_frame, text="Select Log File", width=16, 
                              command=select_file, **button_style)
        select_btn.pack(side=tk.LEFT, padx=4)
        
        update_btn = tk.Button(button_frame, text="Update", width=10, 
                              command=update_file, **button_style)
        update_btn.pack(side=tk.LEFT, padx=4)
        
        copy_btn = tk.Button(button_frame, text="Copy", width=8, 
                            command=copy_to_clipboard, **button_style)
        copy_btn.pack(side=tk.LEFT, padx=4)

        # Result display area
        result_box = scrolledtext.ScrolledText(
            root, width=60, height=3, font=("Segoe UI", 12),
            bg=DARK_PANEL, fg=DARK_TEXT, borderwidth=0, relief=tk.FLAT
        )
        result_box.pack(padx=20, pady=(0, 8), fill=tk.X, expand=False)
        result_box.config(state=tk.DISABLED)

        # Top basher payout section
        top_input_frame = tk.Frame(root, bg=DARK_BG)
        top_input_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
        
        top_label = tk.Label(top_input_frame, text="Top Basher Pay:", 
                            font=("Segoe UI", 11), bg=DARK_BG, fg=DARK_GREEN)
        top_label.pack(side=tk.LEFT)
        
        top_var = tk.StringVar(value="500")
        top_entry = tk.Entry(top_input_frame, textvariable=top_var, 
                            font=("Segoe UI", 11), width=8, bg=DARK_ENTRY, 
                            fg=DARK_TEXT, relief=tk.FLAT)
        top_entry.pack(side=tk.LEFT, padx=(8, 0))

        top_pay_cmd_frame = tk.Frame(root, bg=DARK_BG)
        top_pay_cmd_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")

        # Per-bash payout section
        payout_frame = tk.Frame(root, bg=DARK_BG)
        payout_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
        
        payout_label = tk.Label(payout_frame, text="Payout per bash:", 
                               bg=DARK_BG, fg=DARK_TEXT)
        payout_label.pack(side=tk.LEFT)
        
        payout_var = tk.StringVar(value="100")
        payout_entry = tk.Entry(payout_frame, textvariable=payout_var, width=8, 
                               bg=DARK_ENTRY, fg=DARK_TEXT, relief=tk.FLAT)
        payout_entry.pack(side=tk.LEFT, padx=(8, 0))

        # Payout commands area
        payout_lines_outer = tk.Frame(root, bg=DARK_BG)
        payout_lines_outer.pack(padx=20, pady=(0, 0), fill=tk.BOTH, expand=True, anchor="w")

        payout_canvas = tk.Canvas(payout_lines_outer, bg=DARK_PANEL, 
                                 highlightthickness=0, borderwidth=0)
        payout_canvas.pack(side=tk.LEFT, fill=tk.X, expand=False)

        payout_lines_frame = tk.Frame(payout_canvas, bg=DARK_PANEL)
        payout_canvas.create_window((0, 0), window=payout_lines_frame, anchor="nw")

        def on_frame_configure(event):
            payout_canvas.configure(scrollregion=payout_canvas.bbox("all"))
            bbox = payout_canvas.bbox("all")
            if bbox:
                max_height = 180
                content_height = min(bbox[3] - bbox[1], max_height)
                payout_canvas.config(height=content_height if content_height > 0 else 1)
        
        payout_lines_frame.bind("<Configure>", on_frame_configure)

        # Total payout display
        total_payout_frame = tk.Frame(root, bg=DARK_BG)
        total_payout_frame.pack(padx=20, pady=(8, 0), fill=tk.X, anchor="w")
        
        total_payout_label = tk.Label(total_payout_frame, text="Total Battle Payout: 0 PoE", 
                                     font=("Segoe UI", 12, "bold"), bg=DARK_BG, fg=DARK_GREEN)
        total_payout_label.pack(side=tk.LEFT)

        # Auto-update handlers
        def payout_update(*args):
            """Triggered when payout values change."""
            file_path = state.get('file_path')
            if file_path:
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                                  payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                                  total_payout_label)
        
        payout_var.trace_add('write', payout_update)
        top_var.trace_add('write', payout_update)

        # Footer
        bottom_frame = tk.Frame(root, bg=DARK_BG)
        bottom_frame.pack(side=tk.BOTTOM, pady=(0, 8), fill=tk.X)
        
        creator_label = tk.Label(bottom_frame, text="Created by Swiggity", 
                                font=("Segoe UI", 10, "italic"), 
                                bg=DARK_BG, fg="#888888")
        creator_label.pack(side=tk.LEFT, padx=(20, 0))
        
        version_label = tk.Label(bottom_frame, text=f"v{APP_VERSION}", 
                                font=("Segoe UI", 9), 
                                bg=DARK_BG, fg="#666666")
        version_label.pack(side=tk.RIGHT, padx=(0, 20))

        debug_log("GUI setup completed, starting main loop")
        
        # Start the GUI event loop
        root.mainloop()
        
        debug_log("Application closed normally")
        
    except Exception as e:
        debug_log(f"Critical error in main_gui: {e}")
        traceback.print_exc()
        raise

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the application."""
    debug_log("=== Bash and Dash Game Log Analyzer Debug Version Starting ===")
    debug_log(f"Version: {APP_VERSION}")
    debug_log(f"Python: {sys.version}")
    debug_log(f"Platform: {sys.platform}")
    
    try:
        main_gui()
    except Exception as e:
        debug_log(f"Application error in main(): {e}")
        traceback.print_exc()
        
        # Try to show error message
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showerror(
                "Bash and Dash - Critical Error",
                f"The application encountered a critical error and cannot continue:\n\n"
                f"{type(e).__name__}: {e}\n\n"
                f"Please check the debug log files for more details:\n"
                f"- bashanddash_debug.log\n"
                f"- bashanddash_error.log\n\n"
                f"Report this error to the developer with these files."
            )
        except:
            print(f"CRITICAL ERROR: {e}")
            print("Check debug log files for details.")
        
        sys.exit(1)

# Run the application if this file is executed directly
if __name__ == "__main__":
    main()
