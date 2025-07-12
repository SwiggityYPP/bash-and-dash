#!/usr/bin/env python3
"""
Bash and Dash Game Log Analyzer
===============================

A simple game log analyzer for counting bash attacks and calculating payouts.

Author: Swiggity
Version: 1.0.3
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re
from collections import defaultdict
import os
import urllib.request
import json
import webbrowser
import threading

# Configuration
APP_VERSION = "1.0.4"

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
                            break
        
        # Add the last battle if we were still in one
        if in_battle and current_battle:
            battles.append(dict(current_battle))
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return battles

def show_summary_in_gui(battles, text_widget, payout_frame, payout_var, top_var, total_label, root):
    """Update the GUI with battle analysis results."""
    # Clear existing content
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    
    # Clear existing payout widgets
    for widget in payout_frame.winfo_children():
        widget.destroy()
    
    # Helper function to bind mousewheel to new widgets
    def bind_mousewheel_to_new_widget(widget):
        def on_mousewheel(event):
            # Find the canvas by traversing up the widget hierarchy
            canvas = widget
            while canvas and not isinstance(canvas, tk.Canvas):
                canvas = canvas.master
            if canvas and hasattr(canvas, 'yview_scroll'):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        widget.bind("<MouseWheel>", on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_to_new_widget(child)
    
    if not battles:
        summary = "No greedy bashes found."
        total_label.config(text="Total Battle Payout: 0 PoE")
    else:
        # Process the most recent battle
        last_battle = battles[-1]
        total_bashes = sum(last_battle.values())
        
        # Create pirate summary sorted by bash count (descending)
        pirate_parts = [f"{pirate} ({count})" for pirate, count in 
                       sorted(last_battle.items(), key=lambda x: -x[1])]
        
        summary = f"Total greedy bashes: {total_bashes}"
        if pirate_parts:
            summary += ", " + ", ".join(pirate_parts)
        
        # Handle payouts
        try:
            payout = int(payout_var.get())
            top_payout = int(top_var.get())
        except (ValueError, TypeError):
            payout = 0
            top_payout = 0
        
        total_battle_payout = 0
        
        # Top basher payout
        if last_battle and top_payout > 0:
            sorted_bashers = sorted(last_battle.items(), key=lambda x: -x[1])
            max_bashes = sorted_bashers[0][1] if sorted_bashers else 0
            top_bashers = [pirate for pirate, count in sorted_bashers if count == max_bashes]
            
            for pirate in top_bashers:
                pay_cmd = f"/pay {pirate} {top_payout}"
                total_battle_payout += top_payout  # Add top basher payout to total
                
                row = tk.Frame(payout_frame, bg="#2f3136")
                row.pack(anchor="w", pady=3, padx=12, fill=tk.X)
                
                pay_label = tk.Label(row, text=f"🏆 {pay_cmd}", 
                                   bg="#2f3136", fg="#00d4aa", 
                                   font=("Consolas", 11, "bold"), 
                                   padx=8, pady=6, anchor="w")
                pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                copy_btn = tk.Button(row, text="📋", width=3,
                                   command=lambda cmd=pay_cmd, lbl=pay_label: copy_and_strikethrough(cmd, lbl, root),
                                   bg="#5865f2", fg="#ffffff",
                                   font=("Segoe UI", 10, "bold"),
                                   relief=tk.FLAT, bd=0, cursor="hand2")
                copy_btn.pack(side=tk.RIGHT, padx=8)
                
                # Bind mouse wheel to the new row and its children
                bind_mousewheel_to_new_widget(row)
        
        # Per-bash payouts
        if payout > 0 and last_battle:
            for pirate, count in sorted(last_battle.items(), key=lambda x: -x[1]):
                total_pay = payout * count
                total_battle_payout += total_pay
                pay_cmd = f"/pay {pirate} {total_pay}"
                
                row = tk.Frame(payout_frame, bg="#2f3136")
                row.pack(anchor="w", pady=2, padx=12, fill=tk.X)
                
                pay_label = tk.Label(row, text=f"⚔️ {pay_cmd}", 
                                   bg="#2f3136", fg="#dcddde",
                                   font=("Consolas", 10), 
                                   padx=8, pady=4, anchor="w")
                pay_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                copy_btn = tk.Button(row, text="📋", width=3,
                                   command=lambda cmd=pay_cmd, lbl=pay_label: copy_and_strikethrough(cmd, lbl, root),
                                   bg="#5865f2", fg="#ffffff",
                                   font=("Segoe UI", 9, "bold"),
                                   relief=tk.FLAT, bd=0, cursor="hand2")
                copy_btn.pack(side=tk.RIGHT, padx=8)
                
                # Bind mouse wheel to the new row and its children
                bind_mousewheel_to_new_widget(row)
        
        total_label.config(text=f"Total Battle Payout: {total_battle_payout:,} PoE")
    
    # Update summary text widget
    text_widget.insert(tk.END, summary + "\n")
    text_widget.config(state=tk.DISABLED)

def copy_to_clipboard(text, root):
    """Copy text to clipboard."""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    except:
        pass

def copy_and_strikethrough(text, label, root):
    """Copy text to clipboard and add strikethrough effect to label."""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        
        # Add strikethrough by changing font and color
        current_font = label.cget("font")
        if isinstance(current_font, str):
            # Parse font string to get family and size
            parts = current_font.split()
            if len(parts) >= 2:
                family = parts[0]
                size = parts[1]
                label.config(font=(family, size, "overstrike"), fg="#666666")
            else:
                label.config(font=("Arial", 11, "overstrike"), fg="#666666")
        elif isinstance(current_font, tuple):
            # Font is already a tuple
            family, size = current_font[0], current_font[1]
            label.config(font=(family, size, "overstrike"), fg="#666666")
        else:
            # Fallback
            label.config(font=("Arial", 11, "overstrike"), fg="#666666")
    except:
        pass

def check_for_updates():
    """Check for updates from GitHub releases."""
    try:
        url = "https://api.github.com/repos/SwiggityYPP/bash-and-dash/releases/latest"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest_version = data['tag_name'].lstrip('v')
            download_url = data['html_url']
            
            # Compare versions
            if latest_version != APP_VERSION:
                return latest_version, download_url
    except:
        pass
    return None, None

def show_update_dialog(latest_version, download_url, root):
    """Show update notification dialog."""
    result = messagebox.askyesno(
        "Update Available",
        f"A new version (v{latest_version}) is available!\n"
        f"Current version: v{APP_VERSION}\n\n"
        f"Would you like to download the update?",
        icon="info"
    )
    
    if result:
        try:
            webbrowser.open(download_url)
        except:
            messagebox.showinfo(
                "Update",
                f"Please visit: {download_url}\n\nTo download the latest version."
            )

def check_updates_background(root):
    """Check for updates in background thread."""
    def check():
        latest_version, download_url = check_for_updates()
        if latest_version:
            # Schedule the dialog to run in the main thread
            root.after(0, lambda: show_update_dialog(latest_version, download_url, root))
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()

def main_gui():
    """Initialize and run the main GUI application."""
    root = tk.Tk()
    root.title(f"Bash and Dash v{APP_VERSION}")
    root.geometry("550x700")
    root.configure(bg="#1e2124")
    root.resizable(True, True)
    
    # Application state
    state = {'file_path': None}
    
    def select_file():
        """Handle file selection and analysis."""
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
            try:
                state['file_path'] = file_path
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_frame, payout_var, top_var, total_label, root)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {str(e)}")
    
    def update_file():
        """Re-analyze the currently selected file."""
        file_path = state.get('file_path')
        if file_path:
            try:
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_frame, payout_var, top_var, total_label, root)
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {str(e)}")
    
    def copy_summary():
        """Copy the summary text to clipboard."""
        try:
            text = result_box.get("1.0", tk.END).strip()
            copy_to_clipboard(text, root)
        except:
            pass
    
    def payout_update(*args):
        """Triggered when payout values change."""
        file_path = state.get('file_path')
        if file_path:
            try:
                battles = count_greedy_bashes_per_battle(file_path)
                show_summary_in_gui(battles, result_box, payout_frame, payout_var, top_var, total_label, root)
            except:
                pass
    
    # Main buttons
    button_frame = tk.Frame(root, bg="#1e2124")
    button_frame.pack(pady=15)
    
    button_style = {
        'font': ("Segoe UI", 10, "bold"),
        'bg': "#5865f2",
        'fg': "#ffffff",
        'relief': tk.FLAT,
        'cursor': "hand2",
        'bd': 0,
        'padx': 12,
        'pady': 8
    }
    
    select_btn = tk.Button(button_frame, text="📁 Select Log File", width=18, 
                          command=select_file, **button_style)
    select_btn.pack(side=tk.LEFT, padx=6)
    
    update_btn = tk.Button(button_frame, text="🔄 Update", width=12, 
                          command=update_file, **button_style)
    update_btn.pack(side=tk.LEFT, padx=6)
    
    copy_btn = tk.Button(button_frame, text="📋 Copy", width=10, 
                        command=copy_summary, **button_style)
    copy_btn.pack(side=tk.LEFT, padx=6)
    
    # Battle summary
    summary_frame = tk.Frame(root, bg="#1e2124")
    summary_frame.pack(padx=25, pady=(0, 15), fill=tk.X)
    
    summary_label = tk.Label(summary_frame, text="📊 Battle Summary", 
                            font=("Segoe UI", 11, "bold"), 
                            bg="#1e2124", fg="#ffffff")
    summary_label.pack(anchor="w", pady=(0, 5))
    
    result_box = scrolledtext.ScrolledText(
        summary_frame, width=60, height=3, font=("Consolas", 11),
        bg="#2f3136", fg="#dcddde", borderwidth=1, relief=tk.SOLID,
        wrap=tk.WORD, insertbackground="#ffffff"
    )
    result_box.pack(fill=tk.X)
    result_box.config(state=tk.DISABLED)
    
    # Payout inputs
    input_container = tk.Frame(root, bg="#1e2124")
    input_container.pack(padx=25, pady=(0, 15), fill=tk.X)
    
    # Input section label
    input_label = tk.Label(input_container, text="💰 Payout Settings", 
                          font=("Segoe UI", 11, "bold"), 
                          bg="#1e2124", fg="#ffffff")
    input_label.pack(anchor="w", pady=(0, 8))
    
    # Input fields frame
    inputs_frame = tk.Frame(input_container, bg="#1e2124")
    inputs_frame.pack(fill=tk.X)
    
    # Top basher input
    top_input_frame = tk.Frame(inputs_frame, bg="#1e2124")
    top_input_frame.pack(side=tk.LEFT, padx=(0, 20))
    
    top_label = tk.Label(top_input_frame, text="🏆 Top Basher Pay:", 
                        font=("Segoe UI", 10), bg="#1e2124", fg="#00d4aa")
    top_label.pack(anchor="w")
    
    top_var = tk.StringVar(value="500")
    top_entry = tk.Entry(top_input_frame, textvariable=top_var, 
                        font=("Segoe UI", 11), width=10, bg="#40444b", 
                        fg="#ffffff", relief=tk.FLAT, bd=0,
                        insertbackground="#ffffff", selectbackground="#5865f2")
    top_entry.pack(pady=(5, 0))
    
    # Per bash input
    payout_input_frame = tk.Frame(inputs_frame, bg="#1e2124")
    payout_input_frame.pack(side=tk.LEFT)
    
    payout_label = tk.Label(payout_input_frame, text="⚔️ Payout per bash:", 
                           bg="#1e2124", fg="#ffffff", font=("Segoe UI", 10))
    payout_label.pack(anchor="w")
    
    payout_var = tk.StringVar(value="100")
    payout_entry = tk.Entry(payout_input_frame, textvariable=payout_var, width=10, 
                           bg="#40444b", fg="#ffffff", relief=tk.FLAT, bd=0,
                           insertbackground="#ffffff", selectbackground="#5865f2",
                           font=("Segoe UI", 11))
    payout_entry.pack(pady=(5, 0))
    
    # Scrollable payout commands area
    payout_container = tk.Frame(root, bg="#1e2124")
    payout_container.pack(padx=25, pady=(0, 15), fill=tk.BOTH, expand=True)
    
    payout_header = tk.Label(payout_container, text="💳 Payment Commands", 
                            font=("Segoe UI", 11, "bold"), 
                            bg="#1e2124", fg="#ffffff")
    payout_header.pack(anchor="w", pady=(0, 8))
    
    canvas_frame = tk.Frame(payout_container, bg="#1e2124")
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(canvas_frame, bg="#2f3136", highlightthickness=0, 
                      borderwidth=1, relief=tk.SOLID)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview, 
                            bg="#40444b", troughcolor="#2f3136", 
                            activebackground="#5865f2")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    payout_frame = tk.Frame(canvas, bg="#2f3136")
    canvas.create_window((0, 0), window=payout_frame, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def bind_mousewheel_to_widget(widget):
        """Recursively bind mouse wheel to widget and all its children."""
        widget.bind("<MouseWheel>", on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_to_widget(child)
    
    def bind_mousewheel(event):
        canvas.bind("<MouseWheel>", on_mousewheel)
        bind_mousewheel_to_widget(payout_frame)
    
    def unbind_mousewheel_from_widget(widget):
        """Recursively unbind mouse wheel from widget and all its children."""
        widget.unbind("<MouseWheel>")
        for child in widget.winfo_children():
            unbind_mousewheel_from_widget(child)
    
    def unbind_mousewheel(event):
        canvas.unbind("<MouseWheel>")
        unbind_mousewheel_from_widget(payout_frame)
    
    payout_frame.bind("<Configure>", on_frame_configure)
    canvas.bind('<Enter>', bind_mousewheel)
    canvas.bind('<Leave>', unbind_mousewheel)
    
    # Also bind to the payout_frame and its children initially
    bind_mousewheel_to_widget(payout_frame)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Total payout display
    total_frame = tk.Frame(root, bg="#1e2124")
    total_frame.pack(pady=15, padx=25, fill=tk.X)
    
    total_label = tk.Label(total_frame, text="Total Battle Payout: 0 PoE", 
                          font=("Segoe UI", 12, "bold"), bg="#1e2124", fg="#00d4aa")
    total_label.pack()
    
    # Separator line
    separator = tk.Frame(root, height=1, bg="#40444b")
    separator.pack(fill=tk.X, padx=25)
    
    # Footer
    footer_frame = tk.Frame(root, bg="#1e2124")
    footer_frame.pack(side=tk.BOTTOM, pady=12, fill=tk.X)
    
    creator_label = tk.Label(footer_frame, text="Created by Swiggity", 
                            font=("Segoe UI", 9, "italic"), 
                            bg="#1e2124", fg="#72767d")
    creator_label.pack(side=tk.LEFT, padx=(25, 0))
    
    version_label = tk.Label(footer_frame, text=f"v{APP_VERSION}", 
                            font=("Segoe UI", 9), 
                            bg="#1e2124", fg="#72767d")
    version_label.pack(side=tk.RIGHT, padx=(0, 25))
    
    # Auto-update handlers
    payout_var.trace_add('write', payout_update)
    top_var.trace_add('write', payout_update)
    
    # Check for updates on startup (in background)
    check_updates_background(root)
    
    root.mainloop()

def main():
    """Main entry point for the application."""
    try:
        main_gui()
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()
