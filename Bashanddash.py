#!/usr/bin/env python3
"""
Bash and Dash Game Log Analyzer
===============================

A legitimate game statistics analyzer for parsing game log files.
This tool analyzes battle logs to count specific game events and calculate payouts.

Purpose: Game log analysis and statistics tracking
Author: Swiggity
License: Personal Use

This application:
- Reads text log files from games
- Parses battle statistics using pattern matching
- Displays results in a user-friendly GUI
- Helps calculate game rewards and payouts
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re
from collections import defaultdict
from datetime import datetime
import urllib.request
import json
import threading
import os
import sys
import subprocess
import shutil
import tempfile

# Application version
APP_VERSION = "1.0.0"

# Update configuration
UPDATE_CHECK_URL = "https://api.github.com/repos/YourUsername/bash-and-dash/releases/latest"  # Replace with your GitHub repo
# For testing, you can use a simple JSON file:
# UPDATE_CHECK_URL = "https://raw.githubusercontent.com/YourUsername/bash-and-dash/main/version.json"

# Patterns to detect greedy bashes and extract pirate names
BASH_PATTERNS = [
    r"\[.*?\]\s*(?P<pirate>.+?) performs a powerful attack against .+ and steals some loot in the process!",
    r"\[.*?\]\s*(?P<pirate>.+?) delivers an overwhelming barrage against .+ causing some treasure to fall from their grip!",
    r"\[.*?\]\s*(?P<pirate>.+?) executes a masterful strike against .+ who drops some treasure in surprise!",
    r"\[.*?\]\s*(?P<pirate>.+?) swings a devious blow against .+ jarring some treasure loose!"
]

START_PATTERN = r'Game over'
END_PATTERN = r'Game over'

def check_for_updates():
    """Check for available updates"""
    try:
        with urllib.request.urlopen(UPDATE_CHECK_URL, timeout=10) as response:
            if "github.com" in UPDATE_CHECK_URL:
                # GitHub API response
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data['tag_name'].lstrip('v')
                download_url = None
                
                # Find the executable file in assets
                for asset in data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                if not download_url:
                    return None, None, "No executable found in latest release"
                    
                changelog = data.get('body', 'Bug fixes and improvements')
                
            else:
                # Simple JSON format
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get('version', '1.0.0')
                download_url = data.get('download_url', '')
                changelog = data.get('changelog', 'Bug fixes and improvements')
            
            if is_newer_version(latest_version, APP_VERSION):
                return latest_version, download_url, changelog
            else:
                return None, None, None
                
    except Exception as e:
        print(f"Update check failed: {e}")
        return None, None, f"Update check failed: {e}"

def is_newer_version(latest, current):
    """Compare version strings"""
    try:
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        return version_tuple(latest) > version_tuple(current)
    except:
        return False

def download_update(download_url, progress_callback=None):
    """Download the update file"""
    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "bash_and_dash_update.exe")
        
        # Download with progress
        def reporthook(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, (downloaded * 100) // total_size)
                progress_callback(percent)
        
        urllib.request.urlretrieve(download_url, temp_file, reporthook)
        return temp_file
        
    except Exception as e:
        return None

def apply_update(new_file_path):
    """Apply the update by replacing current executable"""
    try:
        current_exe = sys.executable if getattr(sys, 'frozen', False) else __file__
        
        # Create batch script to handle the update
        batch_content = f'''@echo off
timeout /t 2 /nobreak > nul
move "{new_file_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
'''
        
        batch_file = os.path.join(tempfile.gettempdir(), "update_bash_and_dash.bat")
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # Start the batch file and exit current application
        subprocess.Popen(batch_file, shell=True)
        return True
        
    except Exception as e:
        print(f"Update application failed: {e}")
        return False

def show_update_dialog(root, latest_version, download_url, changelog):
    """Show update dialog with download option"""
    
    def start_update():
        update_btn.config(state='disabled', text='Downloading...')
        progress_var.set(0)
        progress_bar.pack(pady=5)
        
        def download_thread():
            def progress_update(percent):
                root.after(0, lambda: progress_var.set(percent))
                root.after(0, lambda: update_btn.config(text=f'Downloading... {percent}%'))
            
            temp_file = download_update(download_url, progress_update)
            
            if temp_file:
                root.after(0, lambda: update_btn.config(text='Installing...'))
                if apply_update(temp_file):
                    root.after(0, lambda: messagebox.showinfo("Update", "Update will be applied after restart."))
                    root.after(0, lambda: dialog.destroy())
                    root.after(100, lambda: root.quit())  # Close application
                else:
                    root.after(0, lambda: messagebox.showerror("Error", "Failed to apply update."))
                    root.after(0, lambda: update_btn.config(state='normal', text='Update Now'))
                    root.after(0, lambda: progress_bar.pack_forget())
            else:
                root.after(0, lambda: messagebox.showerror("Error", "Failed to download update."))
                root.after(0, lambda: update_btn.config(state='normal', text='Update Now'))
                root.after(0, lambda: progress_bar.pack_forget())
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    # Create update dialog
    dialog = tk.Toplevel(root)
    dialog.title("Update Available")
    dialog.geometry("400x300")
    dialog.configure(bg="#23272e")
    dialog.resizable(False, False)
    
    # Center the dialog
    dialog.transient(root)
    dialog.grab_set()
    
    # Title
    title_label = tk.Label(dialog, text="🚀 Update Available!", 
                          font=("Segoe UI", 16, "bold"), 
                          bg="#23272e", fg="#3ecf8e")
    title_label.pack(pady=20)
    
    # Version info
    version_frame = tk.Frame(dialog, bg="#23272e")
    version_frame.pack(pady=10)
    
    current_label = tk.Label(version_frame, text=f"Current: v{APP_VERSION}", 
                            font=("Segoe UI", 12), bg="#23272e", fg="#f1f1f1")
    current_label.pack()
    
    latest_label = tk.Label(version_frame, text=f"Latest: v{latest_version}", 
                           font=("Segoe UI", 12, "bold"), bg="#23272e", fg="#4f8cff")
    latest_label.pack()
    
    # Changelog
    changelog_label = tk.Label(dialog, text="What's New:", 
                              font=("Segoe UI", 11, "bold"), 
                              bg="#23272e", fg="#f1f1f1")
    changelog_label.pack(pady=(20, 5))
    
    changelog_text = tk.Text(dialog, height=6, width=45, 
                            font=("Segoe UI", 10), 
                            bg="#2c313a", fg="#f1f1f1", 
                            relief=tk.FLAT, wrap=tk.WORD)
    changelog_text.pack(pady=5, padx=20)
    changelog_text.insert(tk.END, changelog)
    changelog_text.config(state=tk.DISABLED)
    
    # Progress bar (hidden initially)
    progress_var = tk.IntVar()
    progress_bar = tk.Frame(dialog, bg="#23272e", height=4)
    
    # Buttons
    button_frame = tk.Frame(dialog, bg="#23272e")
    button_frame.pack(pady=20)
    
    update_btn = tk.Button(button_frame, text="Update Now", 
                          command=start_update,
                          font=("Segoe UI", 11, "bold"),
                          bg="#3ecf8e", fg="#23272e",
                          relief=tk.FLAT, padx=20, pady=8,
                          cursor="hand2")
    update_btn.pack(side=tk.LEFT, padx=10)
    
    later_btn = tk.Button(button_frame, text="Later", 
                         command=dialog.destroy,
                         font=("Segoe UI", 11),
                         bg="#4f8cff", fg="#f1f1f1",
                         relief=tk.FLAT, padx=20, pady=8,
                         cursor="hand2")
    later_btn.pack(side=tk.LEFT, padx=10)

def count_greedy_bashes_per_battle(file_path):
    """
    Analyzes game log file to count greedy bash attacks per battle session.
    
    Args:
        file_path (str): Path to the game log file
        
    Returns:
        list: List of dictionaries containing bash counts per pirate per battle
    """
    battles = []
    in_battle = False
    current_battle = defaultdict(int)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if re.search(START_PATTERN, line):
                    # If we were already in a battle, save it before starting a new one
                    if in_battle and current_battle:
                        battles.append(dict(current_battle))
                    # Start a new battle
                    in_battle = True
                    current_battle = defaultdict(int)
                    continue
                if in_battle:
                    for pattern in BASH_PATTERNS:
                        match = re.search(pattern, line)
                        if match:
                            pirate = match.group('pirate').strip()
                            current_battle[pirate] += 1
        
        # Don't forget to add the last battle if we were still in one
        if in_battle and current_battle:
            battles.append(dict(current_battle))
            
    except (IOError, OSError, UnicodeDecodeError) as e:
        # Handle file reading errors gracefully
        print(f"Error reading file: {e}")
        return []
    
    return battles

def show_summary_in_gui(battles, text_widget, payout_frame, payout_var, payout_lines, top_var, top_pay_frame, top_pay_line, total_payout_label):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    for widget in payout_frame.winfo_children():
        widget.destroy()
    for widget in top_pay_frame.winfo_children():
        widget.destroy()
    payout_lines.clear()
    top_pay_line.clear()
    if not battles:
        summary = "No greedy bashes found."
        # Reset total payout display when no battles
        total_payout_label.config(text="Total Battle Payout: 0 PoE")
    else:
        last_battle = battles[-1]
        total_bashes = sum(last_battle.values())
        pirate_parts = [f"{pirate} ({count})" for pirate, count in sorted(last_battle.items(), key=lambda x: -x[1])]
        summary = f"Total greedy bashes: {total_bashes}"
        if pirate_parts:
            summary += ", " + ", ".join(pirate_parts)
        # Top basher payout
        try:
            top_payout = int(top_var.get())
        except Exception:
            top_payout = 0
        if last_battle and top_payout > 0:
            sorted_bashers = sorted(last_battle.items(), key=lambda x: -x[1])
            max_bashes = sorted_bashers[0][1] if sorted_bashers else 0
            top_bashers = [pirate for pirate, count in sorted_bashers if count == max_bashes]
            for pirate in top_bashers:
                pay_cmd = f"/pay {pirate} {top_payout}"
                top_pay_line.append(pay_cmd)
                row = tk.Frame(top_pay_frame, bg="#2c313a")
                row.pack(anchor="w", pady=2, padx=8, fill=tk.X)
                pay_label = tk.Label(row, text=f"Top Basher: {pay_cmd}", bg="#2c313a", fg="#3ecf8e", font=("Segoe UI", 13, "bold"), padx=8, pady=6, anchor="w")
                pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                def make_copy_cmd(cmd, label=pay_label):
                    def do_copy():
                        try:
                            text_widget.clipboard_clear()
                            text_widget.clipboard_append(cmd)
                            text_widget.update()  # Ensure clipboard is updated
                            label.config(font=("Segoe UI", 13, "bold", "overstrike"), fg="#888")
                        except tk.TclError:
                            # Handle clipboard access errors silently
                            pass
                    return do_copy
                copy_btn = tk.Button(row, text="Copy", width=8, command=make_copy_cmd(pay_cmd), bg="#4f8cff", fg="#f1f1f1", activebackground="#357ae8", activeforeground="#f1f1f1", relief=tk.FLAT, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"))
                copy_btn.pack(side=tk.LEFT, padx=10, pady=2)
        # payout section
        try:
            payout = int(payout_var.get())
        except Exception:
            payout = 0
        
        total_battle_payout = 0  # Initialize total payout counter
        
        if payout > 0 and last_battle:
            for pirate, count in sorted(last_battle.items(), key=lambda x: -x[1]):
                total_pay = payout * count
                total_battle_payout += total_pay  # Add to total
                pay_cmd = f"/pay {pirate} {total_pay}"
                payout_lines.append(pay_cmd)
                row = tk.Frame(payout_frame, bg="#2c313a")
                row.pack(anchor="w", pady=2, padx=8, fill=tk.X)
                pay_label = tk.Label(row, text=pay_cmd, bg="#2c313a", fg="#f1f1f1", font=("Segoe UI", 12), padx=8, pady=6, anchor="w")
                pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                def make_copy_cmd(cmd, label=pay_label):
                    def do_copy():
                        try:
                            text_widget.clipboard_clear()
                            text_widget.clipboard_append(cmd)
                            text_widget.update()  # Ensure clipboard is updated
                            label.config(font=("Segoe UI", 12, "overstrike"), fg="#888")
                        except tk.TclError:
                            # Handle clipboard access errors silently
                            pass
                    return do_copy
                copy_btn = tk.Button(row, text="Copy", width=8, command=make_copy_cmd(pay_cmd), bg="#4f8cff", fg="#f1f1f1", activebackground="#357ae8", activeforeground="#f1f1f1", relief=tk.FLAT, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"))
                copy_btn.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Update total payout display
        total_payout_label.config(text=f"Total Battle Payout: {total_battle_payout:,} PoE")
    text_widget.insert(tk.END, summary + "\n")
    num_lines = summary.count('\n') + 1
    text_widget.config(height=min(max(num_lines, 3), 10))
    text_widget.config(state=tk.DISABLED)

def main_gui():
    root = tk.Tk()
    root.title(f"Bash and Dash v{APP_VERSION}")
    root.geometry("520x540")
    
    # Check for updates after GUI loads
    def check_updates_delayed():
        def update_check_thread():
            latest_version, download_url, changelog = check_for_updates()
            if latest_version and download_url:
                root.after(0, lambda: show_update_dialog(root, latest_version, download_url, changelog))
        
        threading.Thread(target=update_check_thread, daemon=True).start()
    
    root.after(3000, check_updates_delayed)  # Check after 3 seconds
    
    # Set window icon (works for both title bar and taskbar)
    try:
        # Try to set a custom icon if available
        root.iconbitmap("icon.ico")  # You can replace this with your icon file
    except tk.TclError:
        # If custom icon fails, create a simple programmatic icon
        try:
            # Create a simple 32x32 icon with a sword/pirate theme
            icon_photo = tk.PhotoImage(width=32, height=32)
            
            # Create a simple sword icon using pixels
            # Background (transparent/dark)
            for x in range(32):
                for y in range(32):
                    icon_photo.put("#2c313a", (x, y))
            
            # Sword blade (blue)
            for y in range(5, 20):
                icon_photo.put("#4f8cff", (15, y))
                icon_photo.put("#4f8cff", (16, y))
            
            # Sword guard (silver)
            for x in range(12, 20):
                icon_photo.put("#f1f1f1", (x, 19))
                icon_photo.put("#f1f1f1", (x, 20))
            
            # Sword handle (brown)
            for y in range(21, 27):
                icon_photo.put("#8b4513", (15, y))
                icon_photo.put("#8b4513", (16, y))
            
            # Pommel (gold)
            icon_photo.put("#ffd700", (15, 27))
            icon_photo.put("#ffd700", (16, 27))
            icon_photo.put("#ffd700", (14, 28))
            icon_photo.put("#ffd700", (15, 28))
            icon_photo.put("#ffd700", (16, 28))
            icon_photo.put("#ffd700", (17, 28))
            
            root.iconphoto(True, icon_photo)
        except Exception:
            # If all else fails, just use default icon
            pass

    # --- Dark Theme Colors ---
    DARK_BG = "#23272e"
    DARK_PANEL = "#2c313a"
    DARK_ENTRY = "#23272e"
    DARK_TEXT = "#f1f1f1"
    DARK_ACCENT = "#4f8cff"
    DARK_ACCENT2 = "#357ae8"
    DARK_GREEN = "#3ecf8e"
    DARK_BORDER = "#444a56"

    root.configure(bg=DARK_BG)

    state = {'file_path': None}
    payout_lines = []
    top_pay_line = []

    def select_file():
        """Select and validate game log file"""
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
            # Basic file validation
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as test_file:
                    # Just check if we can read the first few lines
                    for i, line in enumerate(test_file):
                        if i >= 10:  # Only check first 10 lines
                            break
                
                state['file_path'] = file_path
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, payout_lines, top_var, top_pay_cmd_frame, top_pay_line, total_payout_label)
            except (IOError, OSError) as e:
                result_box.config(state=tk.NORMAL)
                result_box.delete(1.0, tk.END)
                result_box.insert(tk.END, f"Error reading file: {str(e)}")
                result_box.config(height=3)
                result_box.config(state=tk.DISABLED)
        else:
            result_box.config(state=tk.NORMAL)
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "No file selected.")
            result_box.config(height=3)
            result_box.config(state=tk.DISABLED)
            for widget in payout_lines_frame.winfo_children():
                widget.destroy()
            for widget in top_pay_cmd_frame.winfo_children():
                widget.destroy()
            payout_lines.clear()
            top_pay_line.clear()

    def update_file():
        file_path = state.get('file_path')
        if file_path:
            battles = count_greedy_bashes_per_battle(file_path)
            show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, payout_lines, top_var, top_pay_cmd_frame, top_pay_line, total_payout_label)
        else:
            result_box.config(state=tk.NORMAL)
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "No file selected.")
            result_box.config(height=3)
            result_box.config(state=tk.DISABLED)
            for widget in payout_lines_frame.winfo_children():
                widget.destroy()
            for widget in top_pay_cmd_frame.winfo_children():
                widget.destroy()
            payout_lines.clear()
            top_pay_line.clear()

    def copy_to_clipboard():
        try:
            text = result_box.get("1.0", tk.END).strip()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Ensure clipboard is updated
        except tk.TclError:
            # Handle clipboard access errors silently
            pass

    def manual_update_check():
        """Manual update check triggered by button"""
        def update_check_thread():
            latest_version, download_url, changelog = check_for_updates()
            if latest_version and download_url:
                root.after(0, lambda: show_update_dialog(root, latest_version, download_url, changelog))
            else:
                root.after(0, lambda: messagebox.showinfo("Updates", "You have the latest version!"))
        
        threading.Thread(target=update_check_thread, daemon=True).start()

    # Button row (moved above result_box)
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
        'cursor': "hand2",
        'highlightthickness': 1,
        'highlightbackground': DARK_BORDER,
        'highlightcolor': DARK_ACCENT2
    }
    select_btn = tk.Button(button_frame, text="Select Log File", width=16, command=select_file, **button_style)
    select_btn.pack(side=tk.LEFT, padx=4)
    update_btn = tk.Button(button_frame, text="Update", width=10, command=update_file, **button_style)
    update_btn.pack(side=tk.LEFT, padx=4)
    copy_btn = tk.Button(button_frame, text="Copy", width=8, command=copy_to_clipboard, **button_style)
    copy_btn.pack(side=tk.LEFT, padx=4)
    check_update_btn = tk.Button(button_frame, text="Check Updates", width=12, command=manual_update_check, **button_style)
    check_update_btn.pack(side=tk.LEFT, padx=4)

    # Add hover effect for buttons
    def on_enter(e):
        e.widget.config(bg=DARK_ACCENT2)
    def on_leave(e):
        e.widget.config(bg=DARK_ACCENT)
    for btn in [select_btn, update_btn, copy_btn, check_update_btn]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    result_box = scrolledtext.ScrolledText(
        root, width=60, height=3, font=("Segoe UI", 12),
        bg=DARK_PANEL, fg=DARK_TEXT, borderwidth=0, relief=tk.FLAT,
        highlightthickness=1, highlightbackground=DARK_BORDER, highlightcolor=DARK_ACCENT
    )
    result_box.pack(padx=20, pady=(0, 8), fill=tk.X, expand=False)
    result_box.config(state=tk.DISABLED)

    # Top basher payout input (always visible)
    top_input_frame = tk.Frame(root, bg=DARK_BG)
    top_input_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
    top_label = tk.Label(top_input_frame, text="Top Basher Pay:", font=("Segoe UI", 11), bg=DARK_BG, fg=DARK_GREEN)
    top_label.pack(side=tk.LEFT)
    top_var = tk.StringVar(value="500")
    top_entry = tk.Entry(top_input_frame, textvariable=top_var, font=("Segoe UI", 11), width=8, bg=DARK_ENTRY, fg=DARK_TEXT, relief=tk.FLAT, highlightthickness=1, highlightbackground=DARK_BORDER)
    top_entry.pack(side=tk.LEFT, padx=(8, 0))

    # Frame for top basher payout command (dynamically updated)
    top_pay_cmd_frame = tk.Frame(root, bg=DARK_BG)
    top_pay_cmd_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")

    payout_frame = tk.Frame(root, bg=DARK_BG)
    payout_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
    payout_label = tk.Label(payout_frame, text="Payout per bash:", bg=DARK_BG, fg=DARK_TEXT)
    payout_label.pack(side=tk.LEFT)
    payout_var = tk.StringVar(value="100")
    payout_entry = tk.Entry(payout_frame, textvariable=payout_var, width=8, bg=DARK_ENTRY, fg=DARK_TEXT, relief=tk.FLAT, highlightthickness=1, highlightbackground=DARK_BORDER)
    payout_entry.pack(side=tk.LEFT, padx=(8, 0))

    payout_lines_outer = tk.Frame(root, bg=DARK_BG)
    payout_lines_outer.pack(padx=20, pady=(0, 0), fill=tk.BOTH, expand=True, anchor="w")

    payout_canvas = tk.Canvas(payout_lines_outer, bg=DARK_PANEL, highlightthickness=0, borderwidth=0)
    payout_canvas.pack(side=tk.LEFT, fill=tk.X, expand=False)

    payout_scrollbar = tk.Scrollbar(payout_lines_outer, orient="vertical", command=payout_canvas.yview, bg=DARK_BG, troughcolor=DARK_PANEL, activebackground=DARK_ACCENT)
    payout_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    payout_canvas.configure(yscrollcommand=payout_scrollbar.set)

    payout_lines_frame = tk.Frame(payout_canvas, bg=DARK_PANEL)
    payout_canvas.create_window((0, 0), window=payout_lines_frame, anchor="nw")

    def on_frame_configure(event):
        payout_canvas.configure(scrollregion=payout_canvas.bbox("all"))
        # Dynamically resize the canvas height to fit the content, up to a max height
        bbox = payout_canvas.bbox("all")
        if bbox:
            max_height = 180
            content_height = min(bbox[3] - bbox[1], max_height)
            payout_canvas.config(height=content_height if content_height > 0 else 1)
    payout_lines_frame.bind("<Configure>", on_frame_configure)

    def on_mousewheel(event):
        payout_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    payout_canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Total payout display below the scroll box
    total_payout_frame = tk.Frame(root, bg=DARK_BG)
    total_payout_frame.pack(padx=20, pady=(8, 0), fill=tk.X, anchor="w")
    total_payout_label = tk.Label(total_payout_frame, text="Total Battle Payout: 0 PoE", font=("Segoe UI", 12, "bold"), bg=DARK_BG, fg=DARK_GREEN)
    total_payout_label.pack(side=tk.LEFT)

    def payout_update(*args):
        file_path = state.get('file_path')
        if file_path:
            battles = count_greedy_bashes_per_battle(file_path)
            show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, payout_lines, top_var, top_pay_cmd_frame, top_pay_line, total_payout_label)
    payout_var.trace_add('write', payout_update)
    top_var.trace_add('write', payout_update)

    # Add creator tag and version at the bottom
    bottom_frame = tk.Frame(root, bg=DARK_BG)
    bottom_frame.pack(side=tk.BOTTOM, pady=(0, 8), fill=tk.X)
    
    creator_label = tk.Label(bottom_frame, text="Created by Swiggity", font=("Segoe UI", 10, "italic"), bg=DARK_BG, fg="#888888")
    creator_label.pack(side=tk.LEFT, padx=(20, 0))
    
    version_label = tk.Label(bottom_frame, text=f"v{APP_VERSION}", font=("Segoe UI", 9), bg=DARK_BG, fg="#666666")
    version_label.pack(side=tk.RIGHT, padx=(0, 20))

    root.mainloop()

def main():
    """Main entry point for the application"""
    try:
        main_gui()
    except Exception as e:
        print(f"Application error: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
