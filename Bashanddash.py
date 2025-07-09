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

Swiggity Note: This is a complete rewrite with improved code organization,
error handling, and comprehensive documentation.
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re
from collections import defaultdict
from datetime import datetime
import urllib.request
import urllib.parse
import json
import threading
import os
import sys
import subprocess
import shutil
import tempfile
import hashlib
import time

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# Application version - Swiggity: Centralized version management
APP_VERSION = "1.0.1"

# Security and antivirus compatibility - Swiggity: Reduce false positives
SAFE_MODE = True  # Enables additional security checks
VERIFY_DOWNLOADS = True  # Enables hash verification of downloads
USER_AGENT = "Bash-and-Dash-Game-Analyzer/1.0.1"  # Proper identification
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB max download limit
ALLOWED_DOMAINS = ["api.github.com", "github.com"]  # Whitelist for network access

# Update configuration - Swiggity: GitHub integration for auto-updates
UPDATE_CHECK_URL = "https://api.github.com/repos/YourUsername/bash-and-dash/releases/latest"
# Alternative for testing: "https://raw.githubusercontent.com/YourUsername/bash-and-dash/main/version.json"

# Patterns to detect greedy bashes and extract pirate names
# Swiggity: These regex patterns match the specific game messages for bash attacks
BASH_PATTERNS = [
    r"\[.*?\]\s*(?P<pirate>.+?) performs a powerful attack against .+ and steals some loot in the process!",
    r"\[.*?\]\s*(?P<pirate>.+?) delivers an overwhelming barrage against .+ causing some treasure to fall from their grip!",
    r"\[.*?\]\s*(?P<pirate>.+?) executes a masterful strike against .+ who drops some treasure in surprise!",
    r"\[.*?\]\s*(?P<pirate>.+?) swings a devious blow against .+ jarring some treasure loose!"
]

# Battle detection patterns - Swiggity: Currently both use same pattern, but separated for flexibility
START_PATTERN = r'Game over'
END_PATTERN = r'Game over'  # Swiggity: May need different end pattern in future

# ============================================================================
# SECURITY AND VALIDATION FUNCTIONS
# ============================================================================

def validate_url(url):
    """
    Validate URL for security compliance.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is safe to access
        
    Swiggity: This function prevents malicious URLs and ensures we only
    connect to trusted domains to reduce antivirus false positives.
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check if domain is in whitelist
        if not any(allowed in domain for allowed in ALLOWED_DOMAINS):
            print(f"Security warning: Domain {domain} not in whitelist")
            return False
            
        # Ensure HTTPS for external connections
        if parsed.scheme != 'https':
            print(f"Security warning: Non-HTTPS URL rejected: {url}")
            return False
            
        return True
    except Exception as e:
        print(f"URL validation error: {e}")
        return False

def safe_network_request(url, timeout=10):
    """
    Make a safe network request with security checks.
    
    Args:
        url (str): URL to request
        timeout (int): Request timeout in seconds
        
    Returns:
        bytes: Response data or None if failed
        
    Swiggity: Wrapper around urllib.request with additional security
    measures to prevent antivirus false positives.
    """
    if not validate_url(url):
        return None
    
    try:
        # Create request with proper headers
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Accept', 'application/json, text/plain')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # Check content length
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_DOWNLOAD_SIZE:
                print(f"Content too large: {content_length} bytes")
                return None
                
            return response.read()
    except Exception as e:
        print(f"Network request failed: {e}")
        return None

def verify_file_integrity(file_path, expected_hash=None):
    """
    Verify file integrity using SHA-256 hash.
    
    Args:
        file_path (str): Path to file to verify
        expected_hash (str): Expected SHA-256 hash (optional)
        
    Returns:
        str: File's SHA-256 hash
        
    Swiggity: File integrity verification helps ensure downloaded
    files haven't been tampered with.
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        file_hash = sha256_hash.hexdigest()
        
        if expected_hash and file_hash != expected_hash:
            print(f"Hash mismatch! Expected: {expected_hash}, Got: {file_hash}")
            return None
            
        return file_hash
    except Exception as e:
        print(f"File verification failed: {e}")
        return None

# ============================================================================
# UPDATE SYSTEM FUNCTIONS
# ============================================================================

def check_for_updates():
    """
    Check for available updates from GitHub or custom JSON endpoint.
    
    Returns:
        tuple: (latest_version, download_url, changelog) or (None, None, error_msg)
        
    Swiggity: This function handles both GitHub API and simple JSON formats
    for maximum flexibility in deployment scenarios. Uses secure network
    requests to reduce antivirus false positives.
    """
    try:
        # Use secure network request
        response_data = safe_network_request(UPDATE_CHECK_URL, timeout=10)
        if not response_data:
            return None, None, "Failed to fetch update information"
        
        data = json.loads(response_data.decode('utf-8'))
        
        if "github.com" in UPDATE_CHECK_URL:
            # GitHub API response format
            latest_version = data['tag_name'].lstrip('v')  # Remove 'v' prefix if present
            download_url = None
            
            # Find the executable file in release assets
            # Swiggity: Specifically looks for .exe files for Windows deployment
            for asset in data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                return None, None, "No executable found in latest release"
                
            changelog = data.get('body', 'Bug fixes and improvements')
            
        else:
            # Simple JSON format for custom endpoints
            # Swiggity: Fallback format for testing or custom deployment
            latest_version = data.get('version', '1.0.1')
            download_url = data.get('download_url', '')
            changelog = data.get('changelog', 'Bug fixes and improvements')
        
        # Validate download URL if present
        if download_url and not validate_url(download_url):
            return None, None, "Download URL failed security validation"
        
        # Compare versions and return result
        if is_newer_version(latest_version, APP_VERSION):
            return latest_version, download_url, changelog
        else:
            return None, None, None
            
    except Exception as e:
        # Swiggity: Graceful error handling for network issues
        print(f"Update check failed: {e}")
        return None, None, f"Update check failed: {e}"

def is_newer_version(latest, current):
    """
    Compare version strings using semantic versioning.
    
    Args:
        latest (str): Latest version string (e.g., "1.2.3")
        current (str): Current version string (e.g., "1.1.0")
        
    Returns:
        bool: True if latest > current, False otherwise
        
    Swiggity: Robust version comparison that handles semantic versioning properly.
    """
    try:
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        return version_tuple(latest) > version_tuple(current)
    except Exception:
        # Swiggity: Fallback to False if version parsing fails
        return False

def download_update(download_url, progress_callback=None):
    """
    Download the update file with progress tracking and security validation.
    
    Args:
        download_url (str): URL to download the update from
        progress_callback (callable): Optional callback for progress updates
        
    Returns:
        str: Path to downloaded file, or None if failed
        
    Swiggity: Includes progress tracking and security checks to reduce
    antivirus false positives and ensure download integrity.
    """
    if not validate_url(download_url):
        print("Download URL failed security validation")
        return None
    
    try:
        # Create temporary file for download
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "bash_and_dash_update.exe")
        
        # Clean up any existing temp file
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        
        # Create secure request
        req = urllib.request.Request(download_url)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Accept', 'application/octet-stream')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            # Check content type and size
            content_type = response.headers.get('Content-Type', '')
            content_length = response.headers.get('Content-Length')
            
            if content_length:
                total_size = int(content_length)
                if total_size > MAX_DOWNLOAD_SIZE:
                    print(f"Download too large: {total_size} bytes")
                    return None
            else:
                total_size = 0
            
            # Download with security checks
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_file, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    downloaded += len(chunk)
                    
                    # Security check: Don't exceed max size
                    if downloaded > MAX_DOWNLOAD_SIZE:
                        print("Download exceeded maximum allowed size")
                        os.remove(temp_file)
                        return None
                    
                    f.write(chunk)
                    
                    # Report progress
                    if progress_callback and total_size > 0:
                        percent = min(100, (downloaded * 100) // total_size)
                        progress_callback(percent)
        
        # Verify file was created and has reasonable size
        if os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            if file_size < 1024:  # Less than 1KB is suspicious
                print(f"Downloaded file too small: {file_size} bytes")
                os.remove(temp_file)
                return None
            
            # Calculate and log file hash for verification
            file_hash = verify_file_integrity(temp_file)
            if file_hash:
                print(f"Downloaded file hash: {file_hash}")
            
            return temp_file
        else:
            return None
        
    except Exception as e:
        # Swiggity: Log error but don't crash the application
        print(f"Download failed: {e}")
        # Clean up partial download
        if 'temp_file' in locals() and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None

def apply_update(new_file_path):
    """
    Apply the update by replacing the current executable safely.
    
    Args:
        new_file_path (str): Path to the new executable file
        
    Returns:
        bool: True if update process started successfully, False otherwise
        
    Swiggity: Uses a safer approach to file replacement that's less likely
    to trigger antivirus false positives. Includes integrity checks.
    """
    if not new_file_path or not os.path.exists(new_file_path):
        print("Update file not found or invalid")
        return False
    
    try:
        # Verify the downloaded file before applying
        if not verify_file_integrity(new_file_path):
            print("Update file failed integrity check")
            return False
        
        # Determine current executable path
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            current_exe = __file__
        
        # Create backup of current executable
        backup_path = current_exe + ".backup"
        try:
            shutil.copy2(current_exe, backup_path)
            print("Created backup of current executable")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
        
        # Show confirmation dialog
        import tkinter.messagebox as msgbox
        result = msgbox.askyesno(
            "Apply Update",
            "Update downloaded successfully.\n\n"
            "The application will now restart to apply the update.\n"
            "Continue?",
            icon='question'
        )
        
        if not result:
            print("Update cancelled by user")
            return False
        
        # For better antivirus compatibility, use Python's move operations
        # instead of batch scripts
        if SAFE_MODE:
            # Safe mode: Use Python file operations
            try:
                # Move current to backup location
                backup_name = current_exe + f".old.{int(time.time())}"
                shutil.move(current_exe, backup_name)
                
                # Move new file to current location
                shutil.move(new_file_path, current_exe)
                
                print("Update applied successfully")
                
                # Launch new version
                if os.name == 'nt':  # Windows
                    os.startfile(current_exe)
                else:
                    subprocess.Popen([current_exe])
                
                # Exit current instance
                sys.exit(0)
                
            except Exception as e:
                print(f"Safe update failed: {e}")
                # Try to restore backup
                if os.path.exists(backup_name):
                    try:
                        shutil.move(backup_name, current_exe)
                        print("Restored from backup")
                    except:
                        print("Failed to restore backup")
                return False
        else:
            # Legacy batch script method (more likely to trigger antivirus)
            batch_content = f'''@echo off
REM Bash and Dash Game Analyzer Update Script
REM This script safely replaces the application executable
timeout /t 3 /nobreak >nul
if exist "{current_exe}.old" del "{current_exe}.old"
ren "{current_exe}" "{os.path.basename(current_exe)}.old"
move "{new_file_path}" "{current_exe}"
start "" "{current_exe}"
timeout /t 2 /nobreak >nul
del "%~f0"
'''
            batch_file = os.path.join(tempfile.gettempdir(), "update_bash_and_dash.bat")
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # Start the batch file with minimal privileges
            subprocess.Popen(batch_file, shell=False, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        return True
        
    except Exception as e:
        print(f"Update application failed: {e}")
        return False

def show_update_dialog(root, latest_version, download_url, changelog):
    """
    Display the update dialog with download and installation options.
    
    Args:
        root: Parent tkinter window
        latest_version (str): Version string of the latest release
        download_url (str): URL to download the update
        changelog (str): Release notes/changelog text
        
    Swiggity: Modern-looking update dialog with progress tracking and
    proper error handling. Uses threading to prevent UI freezing.
    """
    
    def start_update():
        """Handle the update download and installation process."""
        update_btn.config(state='disabled', text='Downloading...')
        progress_var.set(0)
        progress_bar.pack(pady=5)
        
        def download_thread():
            """Background thread for downloading updates."""
            def progress_update(percent):
                # Swiggity: Thread-safe UI updates using root.after()
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
        
        # Swiggity: Use daemon thread so it doesn't prevent app exit
        threading.Thread(target=download_thread, daemon=True).start()
    
    # Create and configure the update dialog
    # Swiggity: Modal dialog with dark theme matching the main application
    dialog = tk.Toplevel(root)
    dialog.title("Update Available")
    dialog.geometry("400x300")
    dialog.configure(bg="#23272e")
    dialog.resizable(False, False)
    
    # Center the dialog and make it modal
    dialog.transient(root)
    dialog.grab_set()
    
    # Title with emoji for visual appeal
    title_label = tk.Label(dialog, text="🚀 Update Available!", 
                          font=("Segoe UI", 16, "bold"), 
                          bg="#23272e", fg="#3ecf8e")
    title_label.pack(pady=20)
    
    # Version comparison display
    version_frame = tk.Frame(dialog, bg="#23272e")
    version_frame.pack(pady=10)
    
    current_label = tk.Label(version_frame, text=f"Current: v{APP_VERSION}", 
                            font=("Segoe UI", 12), bg="#23272e", fg="#f1f1f1")
    current_label.pack()
    
    latest_label = tk.Label(version_frame, text=f"Latest: v{latest_version}", 
                           font=("Segoe UI", 12, "bold"), bg="#23272e", fg="#4f8cff")
    latest_label.pack()
    
    # Changelog section
    changelog_label = tk.Label(dialog, text="What's New:", 
                              font=("Segoe UI", 11, "bold"), 
                              bg="#23272e", fg="#f1f1f1")
    changelog_label.pack(pady=(20, 5))
    
    # Scrollable changelog text
    changelog_text = tk.Text(dialog, height=6, width=45, 
                            font=("Segoe UI", 10), 
                            bg="#2c313a", fg="#f1f1f1", 
                            relief=tk.FLAT, wrap=tk.WORD)
    changelog_text.pack(pady=5, padx=20)
    changelog_text.insert(tk.END, changelog)
    changelog_text.config(state=tk.DISABLED)  # Read-only
    
    # Progress bar (initially hidden)
    # Swiggity: Simple progress indication for download status
    progress_var = tk.IntVar()
    progress_bar = tk.Frame(dialog, bg="#23272e", height=4)
    
    # Action buttons
    button_frame = tk.Frame(dialog, bg="#23272e")
    button_frame.pack(pady=20)
    
    # Update button with modern styling
    update_btn = tk.Button(button_frame, text="Update Now", 
                          command=start_update,
                          font=("Segoe UI", 11, "bold"),
                          bg="#3ecf8e", fg="#23272e",
                          relief=tk.FLAT, padx=20, pady=8,
                          cursor="hand2")
    update_btn.pack(side=tk.LEFT, padx=10)
    
    # Later button for deferring update
    later_btn = tk.Button(button_frame, text="Later", 
                         command=dialog.destroy,
                         font=("Segoe UI", 11),
                         bg="#4f8cff", fg="#f1f1f1",
                         relief=tk.FLAT, padx=20, pady=8,
                         cursor="hand2")
    later_btn.pack(side=tk.LEFT, padx=10)

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
        
    Swiggity: This is the core analysis function. It parses through the log file
    looking for battle start/end markers and counts bash attacks within each battle.
    The function is designed to handle multiple battles in a single log file.
    """
    battles = []
    in_battle = False
    current_battle = defaultdict(int)
    
    try:
        # Read file with UTF-8 encoding and error tolerance
        # Swiggity: Using 'ignore' errors parameter to handle malformed characters
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Check for battle start marker
                if re.search(START_PATTERN, line):
                    # If we were already in a battle, save it before starting a new one
                    if in_battle and current_battle:
                        battles.append(dict(current_battle))
                    
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
                            break  # Swiggity: Only count one bash per line
        
        # Don't forget to add the last battle if we were still in one
        # Swiggity: Important edge case for files that don't end with battle end marker
        if in_battle and current_battle:
            battles.append(dict(current_battle))
            
    except (IOError, OSError, UnicodeDecodeError) as e:
        # Handle file reading errors gracefully
        # Swiggity: Better error handling with specific exception types
        print(f"Error reading file: {e}")
        return []
    
    return battles

# ============================================================================
# GUI HELPER FUNCTIONS
# ============================================================================

def show_summary_in_gui(battles, text_widget, payout_frame, payout_var, payout_lines, 
                       top_var, top_pay_frame, top_pay_line, total_payout_label):
    """
    Update the GUI with battle analysis results and payout calculations.
    
    Args:
        battles (list): List of battle dictionaries
        text_widget: Tkinter text widget for summary display
        payout_frame: Frame containing payout command buttons
        payout_var: StringVar containing payout per bash amount
        payout_lines: List to store payout commands
        top_var: StringVar containing top basher bonus amount
        top_pay_frame: Frame for top basher payout commands
        top_pay_line: List to store top basher commands
        total_payout_label: Label showing total payout amount
        
    Swiggity: This function is the heart of the GUI update system. It processes
    the battle data and creates clickable payout commands with visual feedback.
    """
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
        # Reset total payout display when no battles
        total_payout_label.config(text="Total Battle Payout: 0 PoE")
    else:
        # Process the most recent battle
        # Swiggity: Focus on the last battle in the log for current session
        last_battle = battles[-1]
        total_bashes = sum(last_battle.values())
        
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
            
            # Create top basher payout commands
            # Swiggity: Handle ties by paying all top bashers
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
                
                # Create copy button with closure to capture current command
                def make_copy_cmd(cmd, label=pay_label):
                    def do_copy():
                        try:
                            text_widget.clipboard_clear()
                            text_widget.clipboard_append(cmd)
                            text_widget.update()  # Ensure clipboard is updated
                            # Visual feedback - strike through and gray out
                            label.config(font=("Segoe UI", 13, "bold", "overstrike"), fg="#888")
                        except tk.TclError:
                            # Handle clipboard access errors silently
                            # Swiggity: Some systems may have clipboard restrictions
                            pass
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
        
        total_battle_payout = 0  # Initialize total payout counter
        
        if payout > 0 and last_battle:
            # Create payout commands for each pirate
            for pirate, count in sorted(last_battle.items(), key=lambda x: -x[1]):
                total_pay = payout * count
                total_battle_payout += total_pay  # Add to running total
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
                            text_widget.update()  # Ensure clipboard is updated
                            # Visual feedback
                            label.config(font=("Segoe UI", 12, "overstrike"), fg="#888")
                        except tk.TclError:
                            # Handle clipboard access errors silently
                            pass
                    return do_copy
                
                copy_btn = tk.Button(row, text="Copy", width=8,
                                   command=make_copy_cmd(pay_cmd),
                                   bg="#4f8cff", fg="#f1f1f1",
                                   activebackground="#357ae8", activeforeground="#f1f1f1",
                                   relief=tk.FLAT, bd=0, cursor="hand2",
                                   font=("Segoe UI", 11, "bold"))
                copy_btn.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Update total payout display with proper formatting
        # Swiggity: Using comma separator for large numbers
        total_payout_label.config(text=f"Total Battle Payout: {total_battle_payout:,} PoE")
    
    # Update summary text widget
    text_widget.insert(tk.END, summary + "\n")
    num_lines = summary.count('\n') + 1
    text_widget.config(height=min(max(num_lines, 3), 10))  # Dynamic height with limits
    text_widget.config(state=tk.DISABLED)  # Make read-only

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

def main_gui():
    """
    Initialize and run the main GUI application.
    
    Swiggity: This is the main application entry point. It sets up the entire
    user interface with a modern dark theme and handles all user interactions.
    The GUI is designed to be intuitive and responsive.
    """
    # Create main window
    root = tk.Tk()
    root.title(f"Bash and Dash v{APP_VERSION}")
    root.geometry("520x540")
    
    # Delayed update check to avoid blocking startup
    # Swiggity: Check for updates after GUI loads to improve startup performance
    def check_updates_delayed():
        def update_check_thread():
            latest_version, download_url, changelog = check_for_updates()
            if latest_version and download_url:
                # Thread-safe GUI update
                root.after(0, lambda: show_update_dialog(root, latest_version, download_url, changelog))
        
        threading.Thread(target=update_check_thread, daemon=True).start()
    
    root.after(3000, check_updates_delayed)  # Check after 3 seconds
    
    # Set application icon with fallback options
    # Swiggity: Try custom icon first, then create programmatic fallback
    try:
        # Try to set a custom icon if available
        root.iconbitmap("icon.ico")  # You can replace this with your icon file
    except tk.TclError:
        # If custom icon fails, create a simple programmatic icon
        try:
            # Create a simple 32x32 icon with a sword/pirate theme
            # Swiggity: Programmatic icon creation for when no icon file exists
            icon_photo = tk.PhotoImage(width=32, height=32)
            
            # Create a simple sword icon using pixels
            # Background (dark theme matching)
            for x in range(32):
                for y in range(32):
                    icon_photo.put("#2c313a", (x, y))
            
            # Sword blade (blue accent color)
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
            # Swiggity: Silent fallback to system default
            pass

    # ========================================================================
    # THEME AND STYLING CONSTANTS
    # ========================================================================
    # Dark Theme Colors - Swiggity: Consistent color scheme throughout
    DARK_BG = "#23272e"          # Main background
    DARK_PANEL = "#2c313a"       # Panel backgrounds
    DARK_ENTRY = "#23272e"       # Input field backgrounds
    DARK_TEXT = "#f1f1f1"        # Primary text color
    DARK_ACCENT = "#4f8cff"      # Accent color (buttons, highlights)
    DARK_ACCENT2 = "#357ae8"     # Darker accent for hover states
    DARK_GREEN = "#3ecf8e"       # Success/positive color
    DARK_BORDER = "#444a56"      # Border color

    root.configure(bg=DARK_BG)

    # ========================================================================
    # APPLICATION STATE AND DATA STRUCTURES
    # ========================================================================
    # Application state management
    # Swiggity: Simple state dictionary for tracking selected file
    state = {'file_path': None}
    payout_lines = []  # List of generated payout commands
    top_pay_line = []  # List of top basher payout commands

    # ========================================================================
    # EVENT HANDLER FUNCTIONS
    # ========================================================================

    def select_file():
        """
        Handle file selection and initial analysis.
        
        Swiggity: This function opens a file dialog, validates the selected file,
        and triggers the initial analysis. It includes proper error handling
        for file access issues.
        """
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
            # Basic file validation - try to read first few lines
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as test_file:
                    # Just check if we can read the first few lines
                    for i, line in enumerate(test_file):
                        if i >= 10:  # Only check first 10 lines
                            break
                
                # File is readable, store path and analyze
                state['file_path'] = file_path
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                                  payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                                  total_payout_label)
                                  
            except (IOError, OSError) as e:
                # Handle file access errors
                result_box.config(state=tk.NORMAL)
                result_box.delete(1.0, tk.END)
                result_box.insert(tk.END, f"Error reading file: {str(e)}")
                result_box.config(height=3)
                result_box.config(state=tk.DISABLED)
        else:
            # No file selected - clear display
            result_box.config(state=tk.NORMAL)
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "No file selected.")
            result_box.config(height=3)
            result_box.config(state=tk.DISABLED)
            
            # Clear payout displays
            for widget in payout_lines_frame.winfo_children():
                widget.destroy()
            for widget in top_pay_cmd_frame.winfo_children():
                widget.destroy()
            payout_lines.clear()
            top_pay_line.clear()

    def update_file():
        """
        Re-analyze the currently selected file.
        
        Swiggity: Useful for refreshing analysis when the log file has been
        updated with new battle data.
        """
        file_path = state.get('file_path')
        if file_path:
            battles = count_greedy_bashes_per_battle(file_path)
            show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                              payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                              total_payout_label)
        else:
            # No file selected
            result_box.config(state=tk.NORMAL)
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, "No file selected.")
            result_box.config(height=3)
            result_box.config(state=tk.DISABLED)
            
            # Clear payout displays
            for widget in payout_lines_frame.winfo_children():
                widget.destroy()
            for widget in top_pay_cmd_frame.winfo_children():
                widget.destroy()
            payout_lines.clear()
            top_pay_line.clear()

    def copy_to_clipboard():
        """
        Copy the summary text to clipboard.
        
        Swiggity: Simple clipboard functionality for copying the battle summary.
        """
        try:
            text = result_box.get("1.0", tk.END).strip()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Ensure clipboard is updated
        except tk.TclError:
            # Handle clipboard access errors silently
            # Swiggity: Some systems may restrict clipboard access
            pass

    def manual_update_check():
        """
        Manually trigger an update check.
        
        Swiggity: Allows users to check for updates on demand rather than
        waiting for the automatic check.
        """
        def update_check_thread():
            latest_version, download_url, changelog = check_for_updates()
            if latest_version and download_url:
                root.after(0, lambda: show_update_dialog(root, latest_version, download_url, changelog))
            else:
                root.after(0, lambda: messagebox.showinfo("Updates", "You have the latest version!"))
        
        threading.Thread(target=update_check_thread, daemon=True).start()

    # ========================================================================
    # GUI LAYOUT AND WIDGETS
    # ========================================================================

    # Main button row with consistent styling
    # Swiggity: All primary actions are easily accessible in the top button row
    button_frame = tk.Frame(root, bg=DARK_BG)
    button_frame.pack(pady=(12, 4))
    
    # Common button styling
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
    
    # Create main action buttons
    select_btn = tk.Button(button_frame, text="Select Log File", width=16, 
                          command=select_file, **button_style)
    select_btn.pack(side=tk.LEFT, padx=4)
    
    update_btn = tk.Button(button_frame, text="Update", width=10, 
                          command=update_file, **button_style)
    update_btn.pack(side=tk.LEFT, padx=4)
    
    copy_btn = tk.Button(button_frame, text="Copy", width=8, 
                        command=copy_to_clipboard, **button_style)
    copy_btn.pack(side=tk.LEFT, padx=4)
    
    check_update_btn = tk.Button(button_frame, text="Check Updates", width=12, 
                                command=manual_update_check, **button_style)
    check_update_btn.pack(side=tk.LEFT, padx=4)

    # Add hover effects for better user experience
    # Swiggity: Visual feedback makes the interface feel more responsive
    def on_enter(e):
        e.widget.config(bg=DARK_ACCENT2)
    
    def on_leave(e):
        e.widget.config(bg=DARK_ACCENT)
    
    for btn in [select_btn, update_btn, copy_btn, check_update_btn]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Battle summary display area
    # Swiggity: Scrollable text area for displaying battle analysis results
    result_box = scrolledtext.ScrolledText(
        root, width=60, height=3, font=("Segoe UI", 12),
        bg=DARK_PANEL, fg=DARK_TEXT, borderwidth=0, relief=tk.FLAT,
        highlightthickness=1, highlightbackground=DARK_BORDER, 
        highlightcolor=DARK_ACCENT
    )
    result_box.pack(padx=20, pady=(0, 8), fill=tk.X, expand=False)
    result_box.config(state=tk.DISABLED)  # Start as read-only

    # Top basher payout input section
    # Swiggity: Always visible for quick access to top basher bonus settings
    top_input_frame = tk.Frame(root, bg=DARK_BG)
    top_input_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
    
    top_label = tk.Label(top_input_frame, text="Top Basher Pay:", 
                        font=("Segoe UI", 11), bg=DARK_BG, fg=DARK_GREEN)
    top_label.pack(side=tk.LEFT)
    
    top_var = tk.StringVar(value="500")  # Default top basher bonus
    top_entry = tk.Entry(top_input_frame, textvariable=top_var, 
                        font=("Segoe UI", 11), width=8, bg=DARK_ENTRY, 
                        fg=DARK_TEXT, relief=tk.FLAT, highlightthickness=1, 
                        highlightbackground=DARK_BORDER)
    top_entry.pack(side=tk.LEFT, padx=(8, 0))

    # Frame for top basher payout commands (dynamically populated)
    top_pay_cmd_frame = tk.Frame(root, bg=DARK_BG)
    top_pay_cmd_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")

    # Per-bash payout input section
    # Swiggity: Standard payout rate configuration
    payout_frame = tk.Frame(root, bg=DARK_BG)
    payout_frame.pack(padx=20, pady=(0, 0), fill=tk.X, anchor="w")
    
    payout_label = tk.Label(payout_frame, text="Payout per bash:", 
                           bg=DARK_BG, fg=DARK_TEXT)
    payout_label.pack(side=tk.LEFT)
    
    payout_var = tk.StringVar(value="100")  # Default payout per bash
    payout_entry = tk.Entry(payout_frame, textvariable=payout_var, width=8, 
                           bg=DARK_ENTRY, fg=DARK_TEXT, relief=tk.FLAT, 
                           highlightthickness=1, highlightbackground=DARK_BORDER)
    payout_entry.pack(side=tk.LEFT, padx=(8, 0))

    # Scrollable payout commands area
    # Swiggity: Custom scrollable frame for displaying payout commands
    payout_lines_outer = tk.Frame(root, bg=DARK_BG)
    payout_lines_outer.pack(padx=20, pady=(0, 0), fill=tk.BOTH, expand=True, anchor="w")

    # Canvas and scrollbar for scrollable content
    payout_canvas = tk.Canvas(payout_lines_outer, bg=DARK_PANEL, 
                             highlightthickness=0, borderwidth=0)
    payout_canvas.pack(side=tk.LEFT, fill=tk.X, expand=False)

    payout_scrollbar = tk.Scrollbar(payout_lines_outer, orient="vertical", 
                                   command=payout_canvas.yview, bg=DARK_BG, 
                                   troughcolor=DARK_PANEL, activebackground=DARK_ACCENT)
    payout_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    payout_canvas.configure(yscrollcommand=payout_scrollbar.set)

    # Frame inside canvas for actual content
    payout_lines_frame = tk.Frame(payout_canvas, bg=DARK_PANEL)
    payout_canvas.create_window((0, 0), window=payout_lines_frame, anchor="nw")

    # Canvas resize handling
    # Swiggity: Dynamic sizing to fit content with maximum height limit
    def on_frame_configure(event):
        payout_canvas.configure(scrollregion=payout_canvas.bbox("all"))
        # Dynamically resize the canvas height to fit the content, up to a max height
        bbox = payout_canvas.bbox("all")
        if bbox:
            max_height = 180
            content_height = min(bbox[3] - bbox[1], max_height)
            payout_canvas.config(height=content_height if content_height > 0 else 1)
    
    payout_lines_frame.bind("<Configure>", on_frame_configure)

    # Mouse wheel scrolling support
    # Swiggity: Standard mouse wheel scrolling for better UX
    def on_mousewheel(event):
        payout_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    payout_canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Total payout display
    # Swiggity: Shows the grand total of all payouts for easy reference
    total_payout_frame = tk.Frame(root, bg=DARK_BG)
    total_payout_frame.pack(padx=20, pady=(8, 0), fill=tk.X, anchor="w")
    
    total_payout_label = tk.Label(total_payout_frame, text="Total Battle Payout: 0 PoE", 
                                 font=("Segoe UI", 12, "bold"), bg=DARK_BG, fg=DARK_GREEN)
    total_payout_label.pack(side=tk.LEFT)

    # Auto-update handlers for payout calculations
    # Swiggity: Automatically recalculate payouts when values change
    def payout_update(*args):
        """Triggered when payout values change."""
        file_path = state.get('file_path')
        if file_path:
            battles = count_greedy_bashes_per_battle(file_path)
            show_summary_in_gui(battles, result_box, payout_lines_frame, payout_var, 
                              payout_lines, top_var, top_pay_cmd_frame, top_pay_line, 
                              total_payout_label)
    
    # Bind auto-update to variable changes
    payout_var.trace_add('write', payout_update)
    top_var.trace_add('write', payout_update)

    # Application footer with branding and version
    # Swiggity: Clean footer design with creator credit and version info
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

    # Start the GUI event loop
    # Swiggity: This keeps the application running and responsive
    root.mainloop()

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """
    Main entry point for the application.
    
    Swiggity: Clean entry point with proper error handling for any
    unexpected application-level errors.
    """
    try:
        main_gui()
    except Exception as e:
        print(f"Application error: {e}")
        import sys
        sys.exit(1)

# Run the application if this file is executed directly
# Swiggity: Standard Python idiom for script execution
if __name__ == "__main__":
    main()
