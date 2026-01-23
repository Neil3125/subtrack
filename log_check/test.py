# log_check.py

# Performance Optimization 1: Lazy imports and startup optimization
import customtkinter as ctk
import threading
import time
import datetime
from datetime import datetime, timedelta
import sys
import json
import os
import math
import random

# Import modules needed for exe compatibility
try:
    from tkinter import messagebox, simpledialog
    import tkinter as tk
    import pyautogui
    import keyboard
    import pyperclip
    import hashlib
    import ctypes
    import ctypes.wintypes
    import re
    import shutil
except ImportError as e:
    print(f"Warning: Some modules may not be available: {e}")

# Optimization 2: Cache for frequently used modules
_module_cache = {}

def lazy_import(module_name, attribute=None):
    """Lazy import optimization to reduce startup time"""
    if module_name not in _module_cache:
        _module_cache[module_name] = __import__(module_name)
    module = _module_cache[module_name]
    return getattr(module, attribute) if attribute else module

# Optimization 3: Performance monitoring
class PerformanceProfiler:
    def __init__(self):
        self.timings = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def time_function(self, func_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                self.timings[func_name] = self.timings.get(func_name, []) + [end - start]
                return result
            return wrapper
        return decorator
    
    def get_stats(self):
        stats = {}
        for func, times in self.timings.items():
            stats[func] = {
                'avg': sum(times) / len(times),
                'total': sum(times),
                'calls': len(times)
            }
        return stats

# Global profiler instance
profiler = PerformanceProfiler()

# Enhanced color constants and theme system
COLOR_PRIMARY = "#2563eb"
COLOR_SUCCESS = "#4ade80"
COLOR_WARNING = "#f59e42"
COLOR_DANGER = "#ef4444"
COLOR_INFO = "#06b6d4"
COLOR_PURPLE = "#8b5cf6"
COLOR_BACKGROUND = "#16181d"
COLOR_SURFACE = "#1a1d22"
COLOR_BORDER = "#334155"
COLOR_TEXT_PRIMARY = "#f1f5f9"
COLOR_TEXT_SECONDARY = "#7b8ca7"
COLOR_ACCENT = "#60a5fa"

# Animation constants
ANIMATION_DURATION = 200
FADE_STEPS = 20
HOVER_SCALE = 1.05
CLICK_SCALE = 0.95

def get_app_dir():
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        return os.path.dirname(os.path.abspath(__file__))

# Define the messages for each type of check
log_messages = {
    'b': "Logged onto Servers. Checked backup jobs. Checked data integrity and verified that all jobs finished successfully.",
    's': "Logged onto Servers. Checked system logs, DNS and DHCP entries, disk health and usage. Checked ESET logs. Checked volume shadow copies."
}

# Default categories for custom checks
import json
import os

def load_categories():
    """Load categories from categories.json in app directory or use defaults"""
    categories_file = os.path.join(get_app_dir(), "categories.json")
    try:
        if os.path.exists(categories_file):
            with open(categories_file, "r") as f:
                data = json.load(f)
                # If the file is a dict (with 'categories' key), return the list
                if isinstance(data, dict) and "categories" in data:
                    return data["categories"]
                # If it's already a list, return as is
                if isinstance(data, list):
                    return data
    except Exception:
        pass  # Fall back to defaults if any error occurs
    # Default categories
    return ["On-Site", "Remote", "Maintenance", "Other"]

def save_categories(categories):
    categories_file = os.path.join(get_app_dir(), "categories.json")
    try:
        descriptions = None
        try:
            if os.path.exists(categories_file):
                with open(categories_file, "r") as f:
                    existing = json.load(f)
                if isinstance(existing, dict):
                    descriptions = existing.get("descriptions")
        except Exception:
            descriptions = None

        data = {"categories": categories}
        if isinstance(descriptions, dict):
            data["descriptions"] = descriptions
        with open(categories_file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# Load categories
categories = load_categories()

# Windows-compatible date formatting (no leading zeros)
def format_date(dt):
    return f"{dt.month}/{dt.day}/{dt.year}"

def format_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0").replace("AM", "a.m").replace("PM", "p.m")

def round_down_to_quarter(dt):
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)

# Enhanced animation utilities
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors"""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    result = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * factor) for i in range(3))
    return rgb_to_hex(result)

def create_gradient_effect(widget, start_color, end_color, duration=300, steps=30):
    """Create smooth gradient animation effect"""
    def animate_step(step):
        if step <= steps:
            factor = step / steps
            current_color = interpolate_color(start_color, end_color, factor)
            try:
                widget.configure(fg_color=current_color)
                widget.after(duration // steps, lambda: animate_step(step + 1))
            except:
                pass  # Widget might be destroyed
    animate_step(0)

def create_pulse_effect(widget, base_color, pulse_color, duration=1000):
    """Create pulsing color effect"""
    def pulse_step(step, direction=1):
        if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
            factor = (step / 50) * direction
            if factor >= 1:
                direction = -1
                factor = 1
            elif factor <= 0:
                direction = 1
                factor = 0
            
            current_color = interpolate_color(base_color, pulse_color, factor)
            try:
                widget.configure(fg_color=current_color)
                widget.after(duration // 100, lambda: pulse_step((step + direction) % 100, direction))
            except:
                pass
    pulse_step(0)

# Only import pyperclip and ctypes when needed for faster startup
# Optimization 4: Smart caching system
class SmartCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
    
    def get(self, key):
        if key in self.cache:
            self.access_times[key] = time.time()
            profiler.cache_hits += 1
            return self.cache[key]
        profiler.cache_misses += 1
        return None
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()

# Global cache instances
log_cache = SmartCache(50)
ui_cache = SmartCache(30)

# Optimization 5: Faster save_log with caching
@profiler.time_function('save_log')
def save_log(minutes, check_type, category=None, custom_message=None, customer=None):
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=minutes)
    start_str = format_time(start_time)
    end_str = format_time(end_time)
    date_str = format_date(start_time)
    
    if check_type == 'c' and custom_message:
        message = custom_message
        check_name = category if category else "Custom Check"
    else:
        message = log_messages[check_type]
        check_name = 'Service Check' if check_type == 's' else 'Backup Check'
    
    entry = (
        f"[{date_str}][Start: {start_str}]"
        f"[{check_name}] "
        f"{message} "
        f"[End: {end_str}] [Duration {minutes} mins]\n"
    )
    # Always use the same Desktop path logic as show_history
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(desktop_path, exist_ok=True)
    file_path = os.path.join(desktop_path, "check_log.txt")
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(entry)
    pyperclip.copy(entry)
    
    # --- customer metadata ------------------------------------
    if customer and customer != "No Customer":
        meta_path = os.path.join(desktop_path, "log_metadata.json")
        try:
            metadata = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        except json.JSONDecodeError:
            metadata = {}

        log_hash = hashlib.md5(entry.strip().encode("utf-8")).hexdigest()  # use entry.strip()
        metadata[log_hash] = customer
        json.dump(metadata, open(meta_path, "w"), indent=2)
    # -----------------------------------------------------------
    
    return file_path, entry

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # You can change to "green" or "dark-blue" for different accents

# Custom dialog for custom check message
class CustomCheckDialog(ctk.CTkToplevel):
    last_custom_message = ""  # Class variable for draft persistence
    category_descriptions = {}  # category: description

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Custom Check")
        dialog_w, dialog_h = 520, 640
        self.geometry(f"{dialog_w}x{dialog_h}")
        self.resizable(False, False)
        try:
            theme = parent.themes.get(parent.current_theme, parent.themes.get('dark', {})) if hasattr(parent, 'themes') else {}
            self.configure(fg_color=theme.get('surface', "#23272f"))
        except Exception:
            self.configure(fg_color="#23272f")
        self.grab_set()  # Make dialog modal
        x = parent.winfo_x() + (parent.winfo_width() - dialog_w) // 2
        y = parent.winfo_y() + (parent.winfo_height() - dialog_h) // 2
        self.geometry(f"+{x}+{y}")
        try:
            if hasattr(parent, '_popup_fade_in'):
                parent._popup_fade_in(self)
            else:
                self.attributes('-alpha', 0.97)
        except Exception:
            self.attributes('-alpha', 0.97)
        self.result = None
        self.category = None
        self.parent = parent
        self.categories_list = categories.copy()  # Use a copy of the global categories
        # Load category descriptions if present
        self._load_category_descriptions()
        self.selected_category = None
        self._last_auto_filled_desc = ""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Custom Check",
            font=("Segoe UI Semibold", 20),
            text_color="#f1f5f9"
        )
        self.title_label.pack(pady=(25, 15))
        # Category management frame
        self.category_mgmt_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.category_mgmt_frame.pack(pady=(0, 5), fill="x", padx=20)
        self.category_label = ctk.CTkLabel(
            self.category_mgmt_frame,
            text="Categories:",
            font=("Segoe UI", 14, "bold"),
            text_color="#f1f5f9"
        )
        self.category_label.pack(side="left", pady=(0, 5))
        # Categories scrollable frame
        self.categories_container = ctk.CTkScrollableFrame(
            self,
            width=450,
            height=120,
            fg_color="#18181b",
            corner_radius=10,
            border_width=1,
            border_color="#374151",
            scrollbar_fg_color="#18181b",
            scrollbar_button_color="#2563eb"
        )
        self.categories_container.pack(pady=(0, 10), padx=20, fill="x")
        self.category_buttons = []
        # Add new category frame
        self.add_category_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_category_frame.pack(pady=(10, 10), fill="x", padx=20)
        self.new_category_entry = ctk.CTkEntry(
            self.add_category_frame,
            width=200,
            font=("Segoe UI", 14),
            fg_color="#18181b",
            text_color="#f1f5f9",
            border_width=1,
            border_color="#374151",
            placeholder_text="Enter new category name"
        )
        self.new_category_entry.pack(side="left", padx=(0, 10))
        self.add_category_btn = ctk.CTkButton(
            self.add_category_frame,
            text="Add Category",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.add_category
        )
        self.add_category_btn.pack(side="left")
        # Message instructions
        self.instructions = ctk.CTkLabel(
            self,
            text="Enter your custom check message:",
            font=("Segoe UI", 14),
            text_color="#a3a3a3"
        )
        self.instructions.pack(pady=(10, 5))
        # Text entry
        self.text_entry = ctk.CTkTextbox(
            self,
            width=450,
            height=120,
            font=("Segoe UI", 14),
            fg_color="#18181b",
            text_color="#f1f5f9",
            border_width=1,
            border_color="#374151"
        )
        self.text_entry.pack(pady=5, padx=20, fill="both", expand=True)
        # Restore last draft if present
        if CustomCheckDialog.last_custom_message:
            self.text_entry.insert("0.0", CustomCheckDialog.last_custom_message)
        # Save draft on every keypress
        self.text_entry.bind("<KeyRelease>", self._save_draft)
        # Now refresh categories (after text_entry is created)
        self.category_buttons = []
        self.selected_category = None  # No category selected by default
        self._last_auto_filled_desc = ""
        # Do NOT auto-fill message
        # Refresh categories
        self.refresh_categories()
        # Buttons frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", pady=15)
        self.ok_btn = ctk.CTkButton(
            self.btn_frame,
            text="OK",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.submit
        )
        self.ok_btn.pack(side="left", padx=10)
        self.cancel_btn = ctk.CTkButton(
            self.btn_frame,
            text="Cancel",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#6b7280",
            hover_color="#4b5563",
            text_color="#f1f5f9",
            command=self.cancel
        )
        self.cancel_btn.pack(side="left", padx=10)
        self.bind("<Return>", lambda event: self.submit())
        self.bind("<Escape>", lambda event: self.cancel())
        self.after(100, lambda: self.text_entry.focus())

    def _save_draft(self, event=None):
        CustomCheckDialog.last_custom_message = self.text_entry.get("0.0", "end").strip()

    def _load_category_descriptions(self):
        # Try to load from categories.json if present
        categories_file = os.path.join(get_app_dir(), "categories.json")
        try:
            if os.path.exists(categories_file):
                with open(categories_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "descriptions" in data:
                        CustomCheckDialog.category_descriptions = data["descriptions"]
        except Exception:
            pass

    def _save_category_descriptions(self):
        # Save to categories.json, preserving list and adding descriptions
        categories_file = os.path.join(get_app_dir(), "categories.json")
        try:
            data = {"categories": self.categories_list, "descriptions": CustomCheckDialog.category_descriptions}
            with open(categories_file, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def refresh_categories(self):
        for widget in self.categories_container.winfo_children():
            widget.destroy()
        self.category_buttons = []
        for i, category in enumerate(self.categories_list):
            category_frame = ctk.CTkFrame(self.categories_container, fg_color="transparent")
            category_frame.pack(fill="x", pady=2)
            # Category button
            def make_select_callback(c=category, idx=i):
                return lambda: self.select_category(c, idx)
            category_btn = ctk.CTkButton(
                category_frame,
                text=category,
                width=250,
                height=30,
                corner_radius=8,
                font=("Segoe UI", 13),
                fg_color="#2563eb" if (self.selected_category == category) else "#374151",
                hover_color="#1d4ed8",
                text_color="#f1f5f9",
                command=make_select_callback()
            )
            category_btn.pack(side="left", padx=(0, 5))
            # Edit description button
            def edit_desc(cat=category):
                desc_win = ctk.CTkToplevel(self)
                desc_win.title(f"Edit Description for {cat}")
                desc_win.geometry("400x200")
                try:
                    theme = self.parent.themes.get(self.parent.current_theme, self.parent.themes.get('dark', {})) if hasattr(self.parent, 'themes') else {}
                    desc_win.configure(fg_color=theme.get('surface', "#23272f"))
                except Exception:
                    desc_win.configure(fg_color="#23272f")
                desc_win.transient(self)
                desc_win.attributes('-topmost', True)
                desc_win.lift()
                desc_win.after(200, lambda: desc_win.attributes('-topmost', False))
                try:
                    desc_win.grab_set()
                except Exception:
                    pass
                try:
                    x = self.winfo_x() + (self.winfo_width() - 400) // 2
                    y = self.winfo_y() + (self.winfo_height() - 200) // 2
                    desc_win.geometry(f"+{x}+{y}")
                except Exception:
                    pass
                label = ctk.CTkLabel(desc_win, text=f"Description for {cat}", font=("Segoe UI", 14, "bold"), text_color="#f1f5f9")
                label.pack(pady=(20, 10))
                desc_box = ctk.CTkTextbox(desc_win, width=340, height=60, font=("Segoe UI", 12), fg_color="#18181b", text_color="#f1f5f9", border_width=1, border_color="#374151")
                desc_box.pack(padx=20, pady=10)
                desc_box.insert("0.0", CustomCheckDialog.category_descriptions.get(cat, ""))
                def save_desc():
                    CustomCheckDialog.category_descriptions[cat] = desc_box.get("0.0", "end").strip()
                    self._save_category_descriptions()
                    desc_win.destroy()

                btn_row = ctk.CTkFrame(desc_win, fg_color="transparent")
                btn_row.pack(pady=(0, 18))
                ok_btn = ctk.CTkButton(desc_win, text="OK", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=save_desc)
                ok_btn.pack(in_=btn_row, side="left", padx=8)
                cancel_btn = ctk.CTkButton(desc_win, text="Cancel", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#6b7280", hover_color="#4b5563", text_color="#f1f5f9", command=desc_win.destroy)
                cancel_btn.pack(in_=btn_row, side="left", padx=8)
                try:
                    desc_win.bind("<Return>", lambda e: save_desc())
                    desc_win.bind("<Escape>", lambda e: desc_win.destroy())
                except Exception:
                    pass
            edit_btn = ctk.CTkButton(
                category_frame,
                text="Edit",
                width=40,
                height=30,
                corner_radius=8,
                font=("Segoe UI", 13),
                fg_color="#f59e42",
                hover_color="#ea580c",
                text_color="#f1f5f9",
                command=edit_desc
            )
            edit_btn.pack(side="left", padx=(0, 5))
            # Delete button
            delete_btn = ctk.CTkButton(
                category_frame,
                text="X",
                width=30,
                height=30,
                corner_radius=8,
                font=("Segoe UI", 13, "bold"),
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="#f1f5f9",
                command=lambda c=category: self.delete_category(c)
            )
            delete_btn.pack(side="left")
            self.category_buttons.append((category_btn, edit_btn, delete_btn))
        # Do NOT select any category by default
        # self.selected_category = None is already set in __init__
        # Do NOT auto-fill message

    def select_category(self, category, index):
        self.selected_category = category
        # Update button colors
        for i, (btn, _, _) in enumerate(self.category_buttons):
            btn.configure(fg_color="#2563eb" if i == index else "#374151")
        # If user hasn't typed, auto-fill message with description
        self._auto_fill_message(category)

    def _auto_fill_message(self, category):
        # Only fill if the box is empty or matches the last description
        current = self.text_entry.get("0.0", "end").strip()
        desc = CustomCheckDialog.category_descriptions.get(category, "")
        if (not current) or (current == self._last_auto_filled_desc):
            self.text_entry.delete("0.0", "end")
            self.text_entry.insert("0.0", desc)
            self._last_auto_filled_desc = desc
        # Don't overwrite if user has started typing

    def delete_category(self, category):
        if len(self.categories_list) <= 1:
            self.show_status("Cannot delete the last category", is_error=True)
            return
        if category in self.categories_list:
            self.categories_list.remove(category)
            if category in CustomCheckDialog.category_descriptions:
                del CustomCheckDialog.category_descriptions[category]
            global categories
            categories = self.categories_list.copy()
            save_categories(categories)
            self._save_category_descriptions()
            self.refresh_categories()
            self.show_status(f"Category '{category}' deleted")

    def add_category(self):
        new_category = self.new_category_entry.get().strip()
        if not new_category:
            self.show_status("Please enter a category name", is_error=True)
            return
        if new_category in self.categories_list:
            self.show_status(f"Category '{new_category}' already exists", is_error=True)
            return
        self.categories_list.append(new_category)
        global categories
        categories = self.categories_list.copy()
        save_categories(categories)
        self._save_category_descriptions()
        self.new_category_entry.delete(0, 'end')
        self.refresh_categories()
        self.show_status(f"Category '{new_category}' added")
        self.select_category(new_category, len(self.categories_list) - 1)

    def show_status(self, message, is_error=False):
        import tkinter.messagebox as messagebox
        if is_error:
            messagebox.showerror('Error', message)
        else:
            messagebox.showinfo('Status', message)

    def submit(self):
        message = self.text_entry.get("0.0", "end").strip()
        if not message:
            self.show_status("Please enter a message", is_error=True)
            return
        if not self.selected_category:
            self.show_status("Please select a category", is_error=True)
            return
        self.category = self.selected_category
        self.result = message
        CustomCheckDialog.last_custom_message = ""  # Clear draft on submit
        self.destroy()

    def cancel(self):
        self.result = None
        self.category = None
        self.destroy()

# --- On-Site Dialog ---
class OnSiteDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("On-Site Action")
        self.geometry("400x300")
        self.resizable(False, False)
        try:
            theme = parent.themes.get(parent.current_theme, parent.themes.get('dark', {})) if hasattr(parent, 'themes') else {}
            self.configure(fg_color=theme.get('surface', "#23272f"))
        except Exception:
            self.configure(fg_color="#23272f")
        self.grab_set()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")
        try:
            if hasattr(parent, '_popup_fade_in'):
                parent._popup_fade_in(self)
            else:
                self.attributes('-alpha', 0.98)
        except Exception:
            self.attributes('-alpha', 0.98)
        self.result = None
        self.parent = parent
        self.option_var = ctk.StringVar(value="Changed Backup Drive")
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="On-Site Action",
            font=("Segoe UI Semibold", 20),
            text_color="#f1f5f9"
        )
        self.title_label.pack(pady=(25, 15))
        # Radio options
        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack(pady=(10, 10), padx=20, fill="x")
        self.rb1 = ctk.CTkRadioButton(
            self.radio_frame,
            text="Changed Backup Drive",
            variable=self.option_var,
            value="Changed Backup Drive",
            font=("Segoe UI", 15)
        )
        self.rb1.pack(anchor="w", pady=5)
        self.rb2 = ctk.CTkRadioButton(
            self.radio_frame,
            text="Changed Image Drive",
            variable=self.option_var,
            value="Changed Image Drive",
            font=("Segoe UI", 15)
        )
        self.rb2.pack(anchor="w", pady=5)
        self.rb3 = ctk.CTkRadioButton(
            self.radio_frame,
            text="Changed Backup and Image Drive",
            variable=self.option_var,
            value="Changed Backup and Image Drive",
            font=("Segoe UI", 15)
        )
        self.rb3.pack(anchor="w", pady=5)
        # Okay button
        self.ok_btn = ctk.CTkButton(
            self,
            text="Okay",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.submit
        )
        self.ok_btn.pack(pady=(20, 10))
        # Bind Enter/Escape
        self.bind("<Return>", lambda event: self.submit())
        self.bind("<Escape>", lambda event: self.cancel())
        self.after(100, lambda: self.ok_btn.focus())

    def submit(self):
        self.result = self.option_var.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

# --- Time Entry Dialog ---
class TimeEntryDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.result = None
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (380 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (200 // 2)
        self.geometry(f"380x200+{int(x)}+{int(y)}")
        self.resizable(False, False)
        self.lift()
        self.attributes('-topmost', True)
        self.after(200, lambda: self.attributes('-topmost', False))
        self.focus_force()
        msg_label = ctk.CTkLabel(self, text=message, font=("Segoe UI", 15, "bold"), text_color="#f1f5f9")
        msg_label.pack(pady=(18, 8))
        time_frame = ctk.CTkFrame(self, fg_color="#23272f")
        time_frame.pack(pady=10, padx=18, fill="x")
        now = datetime.now()
        default_hour = now.strftime("%I")
        default_minute = now.strftime("%M")
        default_period = now.strftime("%p")
        ctk.CTkLabel(time_frame, text="Hour", font=("Segoe UI", 13), text_color="#f1f5f9").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.hour_var = ctk.StringVar(value=default_hour)
        self.hour_entry = ctk.CTkEntry(time_frame, width=50, textvariable=self.hour_var, font=("Segoe UI", 15))
        self.hour_entry.grid(row=0, column=1, padx=5, pady=8)
        ctk.CTkLabel(time_frame, text="Minute", font=("Segoe UI", 13), text_color="#f1f5f9").grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.minute_var = ctk.StringVar(value=default_minute)
        self.minute_entry = ctk.CTkEntry(time_frame, width=50, textvariable=self.minute_var, font=("Segoe UI", 15))
        self.minute_entry.grid(row=0, column=3, padx=5, pady=8)
        ctk.CTkLabel(time_frame, text="AM/PM", font=("Segoe UI", 13), text_color="#f1f5f9").grid(row=0, column=4, padx=5, pady=8, sticky="e")
        self.period_var = ctk.StringVar(value=default_period)
        self.period_combo = ctk.CTkComboBox(time_frame, values=["AM", "PM"], variable=self.period_var, width=70, font=("Segoe UI", 15), fg_color="#18181b", border_color="#374151", text_color="#f1f5f9")
        self.period_combo.grid(row=0, column=5, padx=5, pady=8)
        submit_button = ctk.CTkButton(self, text="OK", width=120, height=38, corner_radius=10, font=("Segoe UI", 15, "bold"), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=self.on_submit)
        submit_button.pack(pady=(18, 10))
        self.bind("<Return>", lambda event: self.on_submit())
        self.after(100, lambda: self.hour_entry.focus())

    def on_submit(self):
        hour = self.hour_var.get().zfill(2)
        minute = self.minute_var.get().zfill(2)
        period = self.period_var.get().upper()
        try:
            h = int(hour)
            m = int(minute)
            if not (1 <= h <= 12 and 0 <= m <= 59):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid hour (1-12) and minute (0-59).")
            return
        time_str = f"{hour}:{minute}"
        self.result = (time_str, period)
        self.destroy()

# --- Customer Management ---
class CustomerManager:
    def __init__(self):
        self.customers = []
        self.load_customers()

    def load_customers(self):
        """Load customers from customers.json in app directory or use empty list"""
        customers_file = os.path.join(get_app_dir(), "customers.json")
        try:
            if os.path.exists(customers_file):
                with open(customers_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # If it's a list of strings (old format)
                        if all(isinstance(item, str) for item in data):
                            self.customers = data
                        # If it's a list of dicts with 'name' (and possibly 'notes')
                        elif all(isinstance(item, dict) and "name" in item for item in data):
                            self.customers = [item["name"] for item in data]
                        else:
                            self.customers = []
                    else:
                        self.customers = []
        except Exception:
            self.customers = []
        return self.customers

    def save_customers(self):
        """Save customers to customers.json in app directory"""
        customers_file = os.path.join(get_app_dir(), "customers.json")
        try:
            with open(customers_file, "w") as f:
                json.dump(self.customers, f)
        except Exception:
            pass  # Silently fail if we can't save

    def get_customers(self):
        return sorted(list(set(customer.strip() for customer in self.customers if customer.strip())))

    def add_customer(self, customer):
        if customer and customer not in self.customers:
            self.customers.append(customer)
            self.save_customers()

    def remove_customer(self, customer):
        if customer in self.customers:
            self.customers.remove(customer)
            self.save_customers()

    def edit_customer(self, old_name, new_name):
        if old_name in self.customers:
            index = self.customers.index(old_name)
            self.customers[index] = new_name
            self.save_customers()

class CustomerManagementDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Customer Management")
        self.geometry("650x520")
        self.resizable(True, True)
        self.configure(fg_color="#23272f")
        self.grab_set()
        x = parent.winfo_x() + (parent.winfo_width() - 650) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 520) // 2
        self.geometry(f"+{x}+{y}")
        self.attributes('-alpha', 0.98)
        self.parent = parent
        self.customer_mgr = CustomerManager()
        current = None
        try:
            current = parent.selected_customer.get() if hasattr(parent, 'selected_customer') else None
        except Exception:
            current = None
        self.selected_customer = current if current and current != "No Customer" else None
        self.customer_buttons = []
        self._all_customers = []
        self._filtered_customers = []
        self._needs_reload = True
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Customer Management",
            font=("Segoe UI Semibold", 20),
            text_color="#f1f5f9"
        )
        self.title_label.pack(pady=(25, 15))
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(pady=(0, 10), padx=20, fill="x")
        self.search_var = ctk.StringVar(value="")
        self.search_entry = ctk.CTkEntry(
            search_row,
            font=("Segoe UI", 14),
            fg_color="#18181b",
            text_color="#f1f5f9",
            border_width=1,
            border_color="#374151",
            placeholder_text="Search customers...",
            textvariable=self.search_var
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.clear_search_btn = ctk.CTkButton(
            search_row,
            text="Clear",
            width=70,
            height=34,
            corner_radius=10,
            font=("Segoe UI", 13),
            fg_color="#6b7280",
            hover_color="#4b5563",
            text_color="#f1f5f9",
            command=lambda: self.search_var.set("")
        )
        self.clear_search_btn.pack(side="left")
        self.results_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        )
        self.results_label.pack(pady=(0, 10), padx=20, anchor="w")
        # Customer list
        self.customer_list = ctk.CTkFrame(
            self,
            fg_color="#18181b",
            corner_radius=10,
            border_width=1,
            border_color="#374151",
        )
        self.customer_list.pack(pady=(0, 10), padx=20, fill="both", expand=True)
        self.customer_list.grid_columnconfigure(0, weight=1)
        self.customer_list.grid_rowconfigure(0, weight=1)
        self.listbox = tk.Listbox(
            self.customer_list,
            activestyle='none',
            exportselection=False,
            background="#18181b",
            foreground="#f1f5f9",
            selectbackground="#2563eb",
            selectforeground="#f1f5f9",
            highlightthickness=0,
            borderwidth=0,
            font=("Segoe UI", 13)
        )
        self.list_scrollbar = tk.Scrollbar(self.customer_list, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.list_scrollbar.set)
        self.listbox.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.list_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
        self.listbox.bind('<<ListboxSelect>>', self._on_list_select)
        self.listbox.bind('<Double-Button-1>', lambda e: self.confirm_selection())
        self.listbox.bind('<Return>', lambda e: self.confirm_selection())
        self.listbox.bind('<Delete>', lambda e: self.delete_selected())
        self.search_entry.bind('<Down>', lambda e: self._focus_listbox())
        self.search_entry.bind('<Return>', lambda e: self._search_enter())
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Control-f>', lambda e: self._focus_search())
        self.bind('<Control-F>', lambda e: self._focus_search())
        self.bind('<F2>', lambda e: self.edit_selected())
        self._update_customer_list()
        self.search_var.trace_add("write", self._on_search_change)
        self.after(120, lambda: self._focus_search())
        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.pack(pady=(0, 10), padx=20, fill="x")
        self.select_btn = ctk.CTkButton(
            action_row,
            text="Select",
            width=110,
            height=36,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.confirm_selection
        )
        self.select_btn.pack(side="left", padx=(0, 8))
        self.edit_btn = ctk.CTkButton(
            action_row,
            text="Edit",
            width=110,
            height=36,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#334155",
            hover_color="#2563eb",
            text_color="#f1f5f9",
            command=self.edit_selected
        )
        self.edit_btn.pack(side="left", padx=(0, 8))
        self.delete_btn = ctk.CTkButton(
            action_row,
            text="Delete",
            width=110,
            height=36,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#f1f5f9",
            command=self.delete_selected
        )
        self.delete_btn.pack(side="left")
        # Add new customer frame
        self.add_customer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_customer_frame.pack(pady=(10, 10), fill="x", padx=20)
        self.new_customer_entry = ctk.CTkEntry(
            self.add_customer_frame,
            width=200,
            font=("Segoe UI", 14),
            fg_color="#18181b",
            text_color="#f1f5f9",
            border_width=1,
            border_color="#374151",
            placeholder_text="Enter new customer name"
        )
        self.new_customer_entry.pack(side="left", padx=(0, 10))
        self.new_customer_entry.bind('<Return>', lambda e: self.add_customer())
        self.add_customer_btn = ctk.CTkButton(
            self.add_customer_frame,
            text="Add Customer",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.add_customer
        )
        self.add_customer_btn.pack(side="left")
        # Close button
        self.close_btn = ctk.CTkButton(
            self,
            text="Close",
            width=120,
            height=35,
            corner_radius=10,
            font=("Segoe UI", 14),
            fg_color="#6b7280",
            hover_color="#4b5563",
            text_color="#f1f5f9",
            command=self.destroy
        )
        self.close_btn.pack(pady=(10, 10))

    def _focus_search(self):
        try:
            self.search_entry.focus()
            self.search_entry.select_range(0, 'end')
        except Exception:
            pass

    def _focus_listbox(self):
        try:
            self.listbox.focus_set()
            if self.listbox.size() > 0 and not self.listbox.curselection():
                self.listbox.selection_set(0)
                self.listbox.activate(0)
                self.listbox.see(0)
                self._on_list_select(None)
        except Exception:
            pass

    def _search_enter(self):
        try:
            if len(self._filtered_customers) == 1:
                self.selected_customer = self._filtered_customers[0]
                self.confirm_selection()
                return
        except Exception:
            pass
        self._focus_listbox()

    def _on_search_change(self, *args):
        self._update_customer_list()

    def _on_list_select(self, event=None):
        try:
            name = self.get_selected_customer()
            if name:
                self.selected_customer = name
        except Exception:
            pass

    def get_selected_customer(self):
        try:
            sel = self.listbox.curselection()
            if not sel:
                return None
            idx = int(sel[0])
            if idx < 0 or idx >= len(self._filtered_customers):
                return None
            return self._filtered_customers[idx]
        except Exception:
            return None

    def confirm_selection(self):
        name = self.get_selected_customer()
        if name:
            self.selected_customer = name
            self.destroy()

    def delete_selected(self):
        name = self.get_selected_customer()
        if not name:
            return
        try:
            if not messagebox.askyesno("Delete Customer", f"Delete '{name}'?", parent=self):
                return
        except Exception:
            return
        self.remove_customer(name)

    def edit_selected(self):
        name = self.get_selected_customer()
        if not name:
            return
        self.edit_customer(name)

    def add_customer(self):
        new_customer = self.new_customer_entry.get().strip()
        if new_customer and new_customer not in self.customer_mgr.get_customers():
            self.customer_mgr.add_customer(new_customer)
            self.new_customer_entry.delete(0, 'end')
            self.search_var.set("")
            self.selected_customer = new_customer
            self._needs_reload = True
            self._update_customer_list()

    def remove_customer(self, customer):
        self.customer_mgr.remove_customer(customer)
        self._needs_reload = True
        self._update_customer_list()

    def edit_customer(self, customer):
        new_name = simpledialog.askstring("Edit Customer", f"Enter new name for {customer}:", parent=self)
        if new_name and new_name.strip() and new_name != customer and new_name not in self.customer_mgr.get_customers():
            self.customer_mgr.edit_customer(customer, new_name.strip())
            self.selected_customer = new_name.strip()
            self._needs_reload = True
            self._update_customer_list()

    def _update_customer_list(self):
        self.customer_buttons = []
        if self._needs_reload or not self._all_customers:
            self._all_customers = self.customer_mgr.get_customers()
            self._needs_reload = False
        q = ""
        try:
            q = (self.search_var.get() or "").strip().lower()
        except Exception:
            q = ""
        if q:
            self._filtered_customers = [c for c in self._all_customers if q in c.lower()]
        else:
            self._filtered_customers = list(self._all_customers)
        try:
            self.results_label.configure(text=f"{len(self._filtered_customers)} of {len(self._all_customers)}")
        except Exception:
            pass
        try:
            self.listbox.delete(0, 'end')
            for customer in self._filtered_customers:
                self.listbox.insert('end', customer)
        except Exception:
            pass
        if self.selected_customer and self.selected_customer in self._filtered_customers:
            idx = self._filtered_customers.index(self.selected_customer)
            try:
                self.listbox.selection_clear(0, 'end')
                self.listbox.selection_set(idx)
                self.listbox.activate(idx)
                self.listbox.see(idx)
            except Exception:
                pass
        elif self._filtered_customers:
            try:
                self.listbox.selection_clear(0, 'end')
                self.listbox.selection_set(0)
                self.listbox.activate(0)
                self.listbox.see(0)
            except Exception:
                pass

    def destroy(self):
        if hasattr(self.parent, 'selected_customer') and self.selected_customer:
            try:
                self.parent.selected_customer.set(self.selected_customer)
            except Exception:
                pass
        super().destroy()

    def _highlight_customer_by_name(self, customer_name):
        # Reset all buttons to default color
        for btn, _, _ in self.customer_buttons:
            btn.configure(fg_color="#2563eb")

# --- Tkinter UI ---
class LogCheckApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Log Check Pro")
        self.geometry("1000x700")  # UI Improvement 1: Optimized startup size
        self.resizable(True, True)  # UI Improvement 2: Resizable window
        self.configure(fg_color=COLOR_BACKGROUND)
        self.app_alpha = 0.95
        self.attributes('-alpha', self.app_alpha)  # UI Improvement 3: Better transparency
        
        # Feature 1: Window state management
        self.window_state = "normal"
        
        # Feature 2: Auto-save settings
        self.settings_file = os.path.join(get_app_dir(), "app_settings.json")
        
        # Feature 3: Theme management
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg": COLOR_BACKGROUND,
                "surface": COLOR_SURFACE,
                "surface2": "#20242b",
                "border": COLOR_BORDER,
                "text": COLOR_TEXT_PRIMARY,
                "text_secondary": COLOR_TEXT_SECONDARY,
                "accent": COLOR_ACCENT,
            },
            "blue": {
                "bg": "#0f172a",
                "surface": "#1e293b",
                "surface2": "#23324a",
                "border": "#334155",
                "text": COLOR_TEXT_PRIMARY,
                "text_secondary": COLOR_TEXT_SECONDARY,
                "accent": "#3b82f6",
            },
            "forest": {
                "bg": "#0b1410",
                "surface": "#122419",
                "surface2": "#163022",
                "border": "#2a4b3a",
                "text": COLOR_TEXT_PRIMARY,
                "text_secondary": "#8fb3a1",
                "accent": "#22c55e",
            },
            "purple": {
                "bg": "#141019",
                "surface": "#1c1526",
                "surface2": "#241b33",
                "border": "#3a2b55",
                "text": COLOR_TEXT_PRIMARY,
                "text_secondary": "#b7a4d6",
                "accent": "#a855f7",
            },
            "sunset": {
                "bg": "#170f10",
                "surface": "#241416",
                "surface2": "#2f1a1d",
                "border": "#4a2a2f",
                "text": COLOR_TEXT_PRIMARY,
                "text_secondary": "#f3b3a7",
                "accent": "#fb7185",
            },
        }

        self.background_effects_enabled = True
        self.reduce_motion = False

        self.tooltip_delay_ms = 450
        self.toast_duration_ms = 2200
        self.particle_density = 1.0
        self.particle_speed = 1.0
        self.border_animation_enabled = True

        self._toasts = []
        self._hover_anims = {}
        self._bg_anim_id = None
        self._configure_job = None
        self._tooltip_job = None
        self._tooltip_win = None

        self._load_app_settings()
        try:
            self.attributes('-alpha', float(self.app_alpha))
        except Exception:
            pass

        # Feature 4: Performance monitor
        self.performance_data = {"logs_created": 0, "session_time": datetime.now()}
        
        # Feature 5: Notification system
        self.notification_queue = []
        
        # --- Border Animation Canvas ---
        self.border_canvas = ctk.CTkCanvas(self, bg=COLOR_BACKGROUND, highlightthickness=0, borderwidth=0)
        self.border_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_border_animation()

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, fg_color="#191b22", width=120, corner_radius=18, border_width=0)
        self.sidebar.place(relx=0, rely=0, relheight=1, relwidth=0.16)

        self.sidebar_bg_canvas = ctk.CTkCanvas(self.sidebar, bg="#191b22", highlightthickness=0, borderwidth=0)
        self.sidebar_bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.time_label = ctk.CTkLabel(
            self.sidebar,
            text="",
            font=("Segoe UI", 20, "bold"),
            text_color="#e0e7ef"
        )
        self.time_label.pack(pady=(38, 2))
        self.date_label = ctk.CTkLabel(
            self.sidebar,
            text="",
            font=("Segoe UI", 13),
            text_color="#7b8ca7"
        )
        self.date_label.pack(pady=(0, 22))

        self.app_info = ctk.CTkLabel(
            self.sidebar,
            text="Log Check",
            font=("Segoe UI", 22, "bold"),
            text_color="#60a5fa"
        )
        self.app_info.pack(pady=(0, 2))
        self.version_info = ctk.CTkLabel(
            self.sidebar,
            text="v4.1",
            font=("Segoe UI", 12),
            text_color="#64748b"
        )
        self.version_info.pack(pady=(0, 18))

        self.timer_open_btn = ctk.CTkButton(
            self.sidebar,
            text="⏱ Open Timer",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.open_quickbooks_timer
        )
        self.timer_open_btn.pack(pady=(8, 0))
        self.timer_close_btn = ctk.CTkButton(
            self.sidebar,
            text="✖ Close Timer",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="#f1f5f9",
            command=self.close_quickbooks_timer
        )
        self.timer_close_btn.pack(pady=(8, 18))

        self.settings_label = ctk.CTkLabel(
            self.sidebar,
            text="Settings",
            font=("Segoe UI", 15, "bold"),
            text_color="#7b8ca7"
        )
        self.settings_label.pack(pady=(10, 2))

        self.sidebar_divider = ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a2d36")
        self.sidebar_divider.pack(fill="x", padx=14, pady=(10, 8))

        self.theme_btn = ctk.CTkButton(
            self.sidebar,
            text="🎨 Theme",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14),
            fg_color="#334155",
            hover_color="#2563eb",
            text_color="#f1f5f9",
            command=self.open_settings
        )
        self.theme_btn.pack(pady=(6, 0))
        self.history_btn = ctk.CTkButton(
            self.sidebar,
            text="🕑 View History",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14),
            fg_color="#334155",
            hover_color="#2563eb",
            text_color="#f1f5f9",
            command=self.show_history
        )
        self.history_btn.pack(pady=(8, 0))

        # --- New 'Run QB Macro' button ---
        self.run_macro_btn = ctk.CTkButton(
            self.sidebar,
            text="Run QB Macro",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#f59e42",
            hover_color="#ea580c",
            text_color="#f1f5f9",
            command=self.run_qb_macro
        )
        self.run_macro_btn.pack(pady=(8, 18))

        # --- New 'Set QB Coordinates' button ---
        self.set_coord_btn = ctk.CTkButton(
            self.sidebar,
            text="Set QB Coordinates",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#4ade80",
            hover_color="#22c55e",
            text_color="#f1f5f9",
            command=self.set_qb_coordinates
        )
        self.set_coord_btn.pack(pady=(8, 18))

        # --- Main Frame ---
        self.frame = ctk.CTkFrame(self, corner_radius=24, fg_color="#1a1d22", border_width=0)
        self.frame.place(relx=0.19, rely=0.5, anchor="w", relwidth=0.78, relheight=0.93)

        self.main_bg_canvas = ctk.CTkCanvas(self.frame, bg=COLOR_SURFACE, highlightthickness=0, borderwidth=0)
        self.main_bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Customer selector (top of the main frame) -----------
        self.customer_mgr = CustomerManager()
        self.selected_customer = ctk.StringVar(value="No Customer")

        customer_row = ctk.CTkFrame(self.frame, fg_color="transparent")
        customer_row.pack(pady=(10, 10), padx=10, fill="x")

        ctk.CTkLabel(customer_row, text="Customer:", font=("Segoe UI", 15, "bold"), text_color="#f1f5f9").pack(side="left", padx=(0, 10))

        self.customer_display = ctk.CTkLabel(
            customer_row,
            textvariable=self.selected_customer,
            width=250,
            height=35,
            font=("Segoe UI", 14),
            text_color="#f1f5f9",
            fg_color="#18181b",
            corner_radius=10,
            anchor="w",
            padx=10
        )
        self.customer_display.pack(side="left", padx=(0, 10))

        ctk.CTkButton(customer_row, text="Select Customer", width=120, height=35, corner_radius=10, font=("Segoe UI", 14), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=self.open_customer_dialog).pack(side="left", padx=(0, 10))
        ctk.CTkButton(customer_row, text="Clear Selection", width=120, height=35, corner_radius=10, font=("Segoe UI", 14), fg_color="#6b7280", hover_color="#4b5563", text_color="#f1f5f9", command=self.clear_customer_selection).pack(side="left")
        # -----------------------------------------------------------

        self.title_label = ctk.CTkLabel(
            self.frame,
            text="Log Check",
            font=("Segoe UI Semibold", 38),
            text_color="#e0e7ef"
        )
        self.title_label.pack(pady=(32, 12))

        # --- Mode selector ---
        self.mode_var = ctk.StringVar(value="Automatic")
        self.mode_frame = ctk.CTkFrame(self.frame, fg_color="#1a1d22")
        self.mode_frame.pack(pady=(0, 18))
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Mode:", font=("Segoe UI", 17), text_color="#7b8ca7")
        self.mode_label.pack(side="left", padx=(10, 5), pady=12)
        self.automatic_radio = ctk.CTkRadioButton(self.mode_frame, text="Automatic", variable=self.mode_var, value="Automatic", command=self.on_mode_change, font=("Segoe UI", 16, "bold"), fg_color="#2563eb", border_color="#334155")
        self.automatic_radio.pack(side="left", padx=10)
        self.manual_radio = ctk.CTkRadioButton(self.mode_frame, text="Manual/Custom", variable=self.mode_var, value="Manual", command=self.on_mode_change, font=("Segoe UI", 16, "bold"), fg_color="#10b981", border_color="#334155")
        self.manual_radio.pack(side="left", padx=10)

        # --- Duration (Hours and Minutes) menu ---
        self.duration_frame = ctk.CTkFrame(self.frame, fg_color="#1a1d22")
        self.duration_frame.pack(pady=(0, 18))
        self.duration_label = ctk.CTkLabel(self.duration_frame, text="Duration:", font=("Segoe UI", 16), text_color="#7b8ca7")
        self.duration_label.pack(side="left", padx=(10, 5), pady=10)
        self.hours_var = ctk.StringVar(value="0")
        self.hours_menu = ctk.CTkComboBox(self.duration_frame, variable=self.hours_var, values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], width=60, font=("Segoe UI", 16), fg_color="#23272f", border_color="#334155", text_color="#e0e7ef")
        self.hours_menu.pack(side="left", padx=5)
        self.minutes_var = ctk.StringVar(value="30")
        self.minutes_menu = ctk.CTkComboBox(self.duration_frame, variable=self.minutes_var, values=["15", "30", "45", "60", "90", "120"], width=110, font=("Segoe UI", 16), fg_color="#23272f", border_color="#334155", text_color="#e0e7ef")
        self.minutes_menu.pack(side="left", padx=5)

        # --- Manual mode widgets ---
        self.manual_frame = ctk.CTkFrame(self.frame, fg_color="#23272f", corner_radius=18, border_width=1, border_color="#334155")
        self.manual_frame.grid_columnconfigure(0, weight=1)
        self.manual_frame.grid_columnconfigure(1, weight=1)
        self.manual_frame.grid_columnconfigure(2, weight=1)
        self.start_time_label = ctk.CTkLabel(self.manual_frame, text="Start Time:", font=("Segoe UI", 14, "bold"), text_color="#7b8ca7", padx=6, pady=6)
        self.start_time_label.grid(row=0, column=0, padx=6, pady=8, sticky="e")
        self.start_time_entry = ctk.CTkEntry(self.manual_frame, width=80, height=30, placeholder_text="HH:MM", font=("Segoe UI", 14), fg_color="#23272f", border_color="#60a5fa", text_color="#e0e7ef")
        self.start_time_entry.grid(row=0, column=1, padx=6, pady=8)
        self.start_time_period = ctk.StringVar(value="AM")
        self.start_time_period_menu = ctk.CTkComboBox(self.manual_frame, variable=self.start_time_period, values=["AM", "PM"], width=55, height=30, font=("Segoe UI", 14), fg_color="#23272f", border_color="#60a5fa", text_color="#e0e7ef")
        self.start_time_period_menu.grid(row=0, column=2, padx=6, pady=8)
        self.end_time_label = ctk.CTkLabel(self.manual_frame, text="End Time:", font=("Segoe UI", 14, "bold"), text_color="#7b8ca7", padx=6, pady=6)
        self.end_time_label.grid(row=1, column=0, padx=6, pady=8, sticky="e")
        self.end_time_entry = ctk.CTkEntry(self.manual_frame, width=80, height=30, placeholder_text="HH:MM", font=("Segoe UI", 14), fg_color="#23272f", border_color="#60a5fa", text_color="#e0e7ef")
        self.end_time_entry.grid(row=1, column=1, padx=6, pady=8)
        self.end_time_period = ctk.StringVar(value="AM")
        self.end_time_period_menu = ctk.CTkComboBox(self.manual_frame, variable=self.end_time_period, values=["AM", "PM"], width=55, height=30, font=("Segoe UI", 14), fg_color="#23272f", border_color="#60a5fa", text_color="#e0e7ef")
        self.end_time_period_menu.grid(row=1, column=2, padx=6, pady=8)
        # Date input
        self.manual_date_label = ctk.CTkLabel(self.manual_frame, text="Date (MM/DD/YYYY):", font=("Segoe UI", 14, "bold"), text_color="#7b8ca7", padx=6, pady=6)
        self.manual_date_label.grid(row=2, column=0, padx=6, pady=8, sticky="e")
        self.date_entry = ctk.CTkEntry(self.manual_frame, width=110, height=30, placeholder_text="MM/DD/YYYY", font=("Segoe UI", 14), fg_color="#23272f", border_color="#60a5fa", text_color="#e0e7ef")
        self.date_entry.grid(row=2, column=1, padx=6, pady=8, columnspan=2)
        self.manual_frame.pack_forget()
        # Buttons frame
        self.btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.btn_frame.pack(pady=22)
        self.svc_btn = ctk.CTkButton(
            self.btn_frame,
            text="Service Check",
            width=140,
            height=44,
            corner_radius=14,
            font=("Segoe UI", 15, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=lambda: self.submit('s')
        )
        self.svc_btn.pack(side="left", padx=12)
        self.bak_btn = ctk.CTkButton(
            self.btn_frame,
            text="Backup Check",
            width=140,
            height=44,
            corner_radius=14,
            font=("Segoe UI", 15, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#f1f5f9",
            command=lambda: self.submit('b')
        )
        self.bak_btn.pack(side="left", padx=12)
        self.onsite_btn = ctk.CTkButton(
            self.btn_frame,
            text="On-Site",
            width=140,
            height=44,
            corner_radius=14,
            font=("Segoe UI", 15, "bold"),
            fg_color="#f59e42",
            hover_color="#ea580c",
            text_color="#f1f5f9",
            command=self.onsite_check
        )
        self.onsite_btn.pack(side="left", padx=12)
        self.custom_btn = ctk.CTkButton(
            self.btn_frame,
            text="Custom Check",
            width=140,
            height=44,
            corner_radius=14,
            font=("Segoe UI", 15, "bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            text_color="#f1f5f9",
            command=self.custom_check
        )
        self.custom_btn.pack(side="left", padx=12)

        # --- Log preview section ---
        self.preview_label = ctk.CTkLabel(
            self.frame,
            text="Log Preview",
            font=("Segoe UI", 18, "bold"),
            text_color="#7b8ca7"
        )
        self.preview_label.pack(pady=(24, 8))
        self.log_preview = ctk.CTkTextbox(
            self.frame,
            width=800,
            height=80,  # Reduced height
            font=("Consolas", 14),
            fg_color="#181b20",
            text_color="#e0e7ef",
            border_width=0,
            corner_radius=16
        )
        self.log_preview.pack(pady=(0, 14), padx=30, fill="x")
        self.log_preview.insert("0.0", "Log preview will appear here...")
        self.log_preview.configure(state="disabled")
        self.log_preview.bind("<Control-c>", self.copy_log_text)
        self.log_preview.bind("<Button-1>", self.show_edit_dialog)
        # Remove the edit button
        # self.edit_log_btn = ... (removed)
        # Add hover/click logic for manual mode only
        self._log_preview_animating = False
        self._log_preview_target_color = "#181b20"
        self._log_preview_current_color = "#181b20"
        self.log_preview.bind("<Enter>", self._on_log_preview_enter)
        self.log_preview.bind("<Leave>", self._on_log_preview_leave)
        self.log_preview.bind("<Button-1>", self._on_log_preview_click)

        # --- Status frame ---
        self.status_frame = ctk.CTkFrame(
            self.frame,
            fg_color="#21242a",
            corner_radius=16,
            border_width=0,
            height=44
        )
        self.status_frame.pack(pady=(8, 18), fill="x", padx=30)
        self.status = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=("Segoe UI", 15, "bold"),
            text_color="#6ee7b7",
            wraplength=520,
            anchor="center",
            justify="center",
            padx=10,
            pady=10
        )
        self.status.pack(fill="both", expand=True)
        
        # Ensure correct initial state for manual/custom mode
        self.on_mode_change()
        # Initialize app

        # Add help button
        self.help_btn = ctk.CTkButton(
            self.sidebar,
            text="? Help",
            width=100,
            height=35,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLOR_PRIMARY,  # Use constant for color
            hover_color="#1d4ed8",
            text_color="#f1f5f9",
            command=self.show_help
        )
        self.help_btn.pack(pady=(8, 18))

        # --- Set Date Coord Button ---
        self.set_date_coord_btn = ctk.CTkButton(
            self.sidebar,
            text="Set Date Coord",
            width=120,
            height=35,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#f59e42",
            hover_color="#ea580c",
            text_color="#f1f5f9",
            command=self.set_qb_date_coord
        )
        self.set_date_coord_btn.pack(pady=(2, 2))

        # Bind keyboard shortcuts to buttons
        self.bind_all("<F1>", lambda event: self.show_help())  # F1 for help
        self.bind_all("<F2>", lambda event: self.run_qb_macro())  # F2 for run macro
        self.bind_all("<F3>", lambda event: self.set_qb_coordinates())  # F3 for set coordinates
        
        # Feature 6: Auto-save coordinates on app close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Feature 7: Periodic auto-save (every 5 minutes)
        self.auto_save_timer()

        self.apply_theme(self.current_theme, save=False)
        self._setup_smooth_hovers()
        self._setup_focus_effects()
        self._setup_tooltips()
        self.after(250, self._start_background_effects)

        self.bind("<Configure>", self._on_window_configure)
        
        print("Log Check Pro initialized successfully!")

    def _start_rgb_animation(self):
        """Start RGB color cycling animation"""
        threading.Thread(target=self._rgb_animation_thread, daemon=True).start()

    def _rgb_animation_thread(self):
        """Thread for smooth RGB color cycling animation"""
        # Define color transitions
        transitions = [
            [(255, 0, 0), (255, 255, 0)],  # Red to Yellow
            [(255, 255, 0), (0, 255, 0)],   # Yellow to Green
            [(0, 255, 0), (0, 255, 255)],   # Green to Cyan
            [(0, 255, 255), (0, 0, 255)],   # Cyan to Blue
            [(0, 0, 255), (255, 0, 255)],   # Blue to Magenta
            [(255, 0, 255), (255, 0, 0)]    # Magenta to Red
        ]
        
        # Number of steps for each transition
        steps = 60
        
        while True:
            for start_color, end_color in transitions:
                # Calculate the increment for each color component
                r_step = (end_color[0] - start_color[0]) / steps
                g_step = (end_color[1] - start_color[1]) / steps
                b_step = (end_color[2] - start_color[2]) / steps
                
                # Create intermediate colors
                for i in range(steps + 1):
                    r = int(start_color[0] + r_step * i)
                    g = int(start_color[1] + g_step * i)
                    b = int(start_color[2] + b_step * i)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.after(0, lambda c=color: self._draw_border_animation(c))
                    time.sleep(0.05)  # Slower transition time

    def _draw_border_animation(self):
        if hasattr(self, '_animation_id'):
            self.after_cancel(self._animation_id)
        self.border_canvas.delete("border")
        thickness = 3
        offset = 1
        w, h = self.winfo_width(), self.winfo_height()
        # Draw border with animation
        border_color = self._get_next_color()
        self.border_canvas.create_rectangle(
            offset, offset, w - offset, h - offset, outline=border_color, width=thickness, tags="border"
        )
        # Schedule next animation frame
        self._animation_id = self.after(30, self._draw_border_animation)

    def _update_time(self):
        """Update current time display"""
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%I:%M:%S %p").lstrip("0"))
        self.date_label.configure(text=now.strftime("%A, %B %d").replace(" 0", " "))
        self.after(1000, self._update_time)  # Update every second

    def _load_app_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                theme = data.get('theme')
                if theme in getattr(self, 'themes', {}):
                    self.current_theme = theme
                self.background_effects_enabled = bool(data.get('background_effects_enabled', True))
                self.reduce_motion = bool(data.get('reduce_motion', False))
                try:
                    self.tooltip_delay_ms = int(data.get('tooltip_delay_ms', self.tooltip_delay_ms))
                except Exception:
                    pass
                try:
                    self.toast_duration_ms = int(data.get('toast_duration_ms', self.toast_duration_ms))
                except Exception:
                    pass
                try:
                    self.particle_density = float(data.get('particle_density', self.particle_density))
                except Exception:
                    pass
                try:
                    self.particle_speed = float(data.get('particle_speed', self.particle_speed))
                except Exception:
                    pass
                self.border_animation_enabled = bool(data.get('border_animation_enabled', self.border_animation_enabled))
                alpha = data.get('app_alpha', self.app_alpha)
                try:
                    alpha = float(alpha)
                    if 0.75 <= alpha <= 1.0:
                        self.app_alpha = alpha
                except Exception:
                    pass
        except Exception:
            pass

    def _save_app_settings(self):
        try:
            data = {
                'theme': self.current_theme,
                'background_effects_enabled': bool(self.background_effects_enabled),
                'reduce_motion': bool(self.reduce_motion),
                'app_alpha': float(self.app_alpha),
                'tooltip_delay_ms': int(getattr(self, 'tooltip_delay_ms', 450)),
                'toast_duration_ms': int(getattr(self, 'toast_duration_ms', 2200)),
                'particle_density': float(getattr(self, 'particle_density', 1.0)),
                'particle_speed': float(getattr(self, 'particle_speed', 1.0)),
                'border_animation_enabled': bool(getattr(self, 'border_animation_enabled', True)),
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("420x520")
        win.resizable(False, False)
        try:
            win.grab_set()
        except Exception:
            pass

        self._popup_fade_in(win)

        theme = self.themes.get(self.current_theme, self.themes['dark'])
        win.configure(fg_color=theme['surface'])

        title = ctk.CTkLabel(win, text="Appearance", font=("Segoe UI", 20, "bold"), text_color=theme['text'])
        title.pack(pady=(18, 8))

        theme_row = ctk.CTkFrame(win, fg_color="transparent")
        theme_row.pack(padx=18, pady=(10, 6), fill="x")
        ctk.CTkLabel(theme_row, text="Theme", font=("Segoe UI", 14, "bold"), text_color=theme['text_secondary']).pack(side="left")

        theme_var = ctk.StringVar(value=self.current_theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_row,
            variable=theme_var,
            values=list(self.themes.keys()),
            width=180,
            fg_color=theme['surface2'],
            button_color=theme['accent'],
            button_hover_color=theme['accent'],
            text_color=theme['text'],
        )
        theme_menu.pack(side="right")

        opts = ctk.CTkFrame(win, fg_color=theme['surface2'], corner_radius=14)
        opts.pack(padx=18, pady=(10, 10), fill="x")

        bg_var = ctk.BooleanVar(value=bool(self.background_effects_enabled))
        motion_var = ctk.BooleanVar(value=bool(self.reduce_motion))
        border_var = ctk.BooleanVar(value=bool(getattr(self, 'border_animation_enabled', True)))

        bg_switch = ctk.CTkSwitch(opts, text="Background effects", variable=bg_var, font=("Segoe UI", 14), text_color=theme['text'])
        bg_switch.pack(anchor="w", padx=14, pady=(14, 6))
        motion_switch = ctk.CTkSwitch(opts, text="Reduce motion", variable=motion_var, font=("Segoe UI", 14), text_color=theme['text'])
        motion_switch.pack(anchor="w", padx=14, pady=(6, 6))
        border_switch = ctk.CTkSwitch(opts, text="Animated border", variable=border_var, font=("Segoe UI", 14), text_color=theme['text'])
        border_switch.pack(anchor="w", padx=14, pady=(6, 10))

        alpha_row = ctk.CTkFrame(opts, fg_color="transparent")
        alpha_row.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(alpha_row, text="Transparency", font=("Segoe UI", 13, "bold"), text_color=theme['text_secondary']).pack(side="left")

        alpha_var = ctk.DoubleVar(value=float(self.app_alpha))
        alpha_slider = ctk.CTkSlider(alpha_row, from_=0.75, to=1.0, number_of_steps=25, variable=alpha_var)
        alpha_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

        fx = ctk.CTkFrame(win, fg_color=theme['surface2'], corner_radius=14)
        fx.pack(padx=18, pady=(0, 10), fill="x")

        tip_row = ctk.CTkFrame(fx, fg_color="transparent")
        tip_row.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(tip_row, text="Tooltip delay", font=("Segoe UI", 13, "bold"), text_color=theme['text_secondary']).pack(side="left")
        tip_var = ctk.DoubleVar(value=float(getattr(self, 'tooltip_delay_ms', 450)))
        tip_slider = ctk.CTkSlider(tip_row, from_=150, to=800, number_of_steps=26, variable=tip_var)
        tip_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

        toast_row = ctk.CTkFrame(fx, fg_color="transparent")
        toast_row.pack(fill="x", padx=14, pady=(6, 6))
        ctk.CTkLabel(toast_row, text="Toast duration", font=("Segoe UI", 13, "bold"), text_color=theme['text_secondary']).pack(side="left")
        toast_var = ctk.DoubleVar(value=float(getattr(self, 'toast_duration_ms', 2200)))
        toast_slider = ctk.CTkSlider(toast_row, from_=1200, to=5000, number_of_steps=19, variable=toast_var)
        toast_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

        dens_row = ctk.CTkFrame(fx, fg_color="transparent")
        dens_row.pack(fill="x", padx=14, pady=(6, 6))
        ctk.CTkLabel(dens_row, text="Particle density", font=("Segoe UI", 13, "bold"), text_color=theme['text_secondary']).pack(side="left")
        dens_var = ctk.DoubleVar(value=float(getattr(self, 'particle_density', 1.0)))
        dens_slider = ctk.CTkSlider(dens_row, from_=0.6, to=1.8, number_of_steps=12, variable=dens_var)
        dens_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

        spd_row = ctk.CTkFrame(fx, fg_color="transparent")
        spd_row.pack(fill="x", padx=14, pady=(6, 12))
        ctk.CTkLabel(spd_row, text="Particle speed", font=("Segoe UI", 13, "bold"), text_color=theme['text_secondary']).pack(side="left")
        spd_var = ctk.DoubleVar(value=float(getattr(self, 'particle_speed', 1.0)))
        spd_slider = ctk.CTkSlider(spd_row, from_=0.6, to=1.8, number_of_steps=12, variable=spd_var)
        spd_slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

        def apply_all(*_):
            old_density = float(getattr(self, 'particle_density', 1.0))
            self.background_effects_enabled = bool(bg_var.get())
            self.reduce_motion = bool(motion_var.get())
            self.border_animation_enabled = bool(border_var.get())
            try:
                self.tooltip_delay_ms = int(tip_var.get())
            except Exception:
                pass
            try:
                self.toast_duration_ms = int(toast_var.get())
            except Exception:
                pass
            try:
                self.particle_density = float(dens_var.get())
            except Exception:
                pass
            try:
                self.particle_speed = float(spd_var.get())
            except Exception:
                pass
            self.app_alpha = float(alpha_var.get())
            try:
                self.attributes('-alpha', float(self.app_alpha))
            except Exception:
                pass
            self.apply_theme(theme_var.get(), save=False)

            try:
                if not self.border_animation_enabled:
                    if getattr(self, '_animation_id', None) is not None:
                        self.after_cancel(self._animation_id)
                        self._animation_id = None
                    self.border_canvas.delete("border")
                    w, h = self.winfo_width(), self.winfo_height()
                    t = self.themes.get(self.current_theme, self.themes['dark'])
                    self.border_canvas.create_rectangle(1, 1, w - 1, h - 1, outline=t.get('accent', COLOR_ACCENT), width=3, tags="border")
                else:
                    if getattr(self, '_animation_id', None) is None:
                        self._draw_border_animation()
            except Exception:
                pass

            try:
                if abs(float(getattr(self, 'particle_density', 1.0)) - old_density) > 0.01:
                    self._bg_particles = []
                    self._sb_particles = []
                    try:
                        self.main_bg_canvas.delete('bg')
                    except Exception:
                        pass
                    try:
                        self.sidebar_bg_canvas.delete('bg')
                    except Exception:
                        pass
            except Exception:
                pass

            self._save_app_settings()

        theme_var.trace_add("write", apply_all)
        bg_var.trace_add("write", apply_all)
        motion_var.trace_add("write", apply_all)
        border_var.trace_add("write", apply_all)
        alpha_var.trace_add("write", apply_all)
        tip_var.trace_add("write", apply_all)
        toast_var.trace_add("write", apply_all)
        dens_var.trace_add("write", apply_all)
        spd_var.trace_add("write", apply_all)

        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(padx=18, pady=(8, 14), fill="x")
        close_btn = ctk.CTkButton(
            btns,
            text="Close",
            height=38,
            corner_radius=12,
            fg_color=theme['accent'],
            hover_color=theme['accent'],
            text_color=theme['text'],
            command=lambda: self._popup_fade_out(win),
        )
        close_btn.pack(side="right")

    def apply_theme(self, theme_name: str, save: bool = True):
        if theme_name not in self.themes:
            return
        self.current_theme = theme_name
        t = self.themes[theme_name]

        try:
            self.configure(fg_color=t['bg'])
        except Exception:
            pass
        try:
            self.border_canvas.configure(bg=t['bg'])
        except Exception:
            pass
        try:
            self.sidebar.configure(fg_color=t['surface'])
        except Exception:
            pass
        try:
            self.sidebar_bg_canvas.configure(bg=t['surface'])
        except Exception:
            pass
        try:
            self.frame.configure(fg_color=t['surface'])
        except Exception:
            pass
        try:
            self.main_bg_canvas.configure(bg=t['surface'])
        except Exception:
            pass

        for name in (
            'mode_frame',
            'duration_frame',
        ):
            w = getattr(self, name, None)
            if w is not None:
                try:
                    w.configure(fg_color=t['surface'])
                except Exception:
                    pass
        for name in (
            'manual_frame',
            'status_frame',
        ):
            w = getattr(self, name, None)
            if w is not None:
                try:
                    w.configure(fg_color=t['surface2'], border_color=t['border'])
                except Exception:
                    pass

        for name in (
            'history_btn',
            'theme_btn',
        ):
            b = getattr(self, name, None)
            if b is not None:
                try:
                    b.configure(fg_color=t['surface2'], hover_color=t['accent'])
                except Exception:
                    pass

        for name in (
            'time_label',
            'date_label',
            'settings_label',
            'mode_label',
            'duration_label',
            'preview_label',
        ):
            w = getattr(self, name, None)
            if w is not None:
                try:
                    w.configure(text_color=t['text_secondary'])
                except Exception:
                    pass
        for name in (
            'title_label',
            'status',
            'customer_display',
        ):
            w = getattr(self, name, None)
            if w is not None:
                try:
                    w.configure(text_color=t['text'])
                except Exception:
                    pass

        if save:
            self._save_app_settings()

        self._refresh_background_palette()
        self._start_background_effects()

    def _on_window_configure(self, event=None):
        try:
            if self._configure_job is not None:
                self.after_cancel(self._configure_job)
        except Exception:
            pass

        self._configure_job = self.after(120, self._flush_window_configure)

    def _flush_window_configure(self):
        self._configure_job = None
        self._reposition_toasts()
        self._start_background_effects()

    def _setup_tooltips(self):
        def bind_tip(widget, text: str):
            if widget is None:
                return

            def show():
                self._show_tooltip(widget, text)

            def on_enter(_):
                self._cancel_tooltip()
                delay = int(getattr(self, 'tooltip_delay_ms', 450))
                self._tooltip_job = self.after(delay, show)

            def on_leave(_):
                self._cancel_tooltip()
                self._hide_tooltip()

            try:
                widget.bind("<Enter>", on_enter, add="+")
                widget.bind("<Leave>", on_leave, add="+")
            except Exception:
                pass

        bind_tip(getattr(self, 'timer_open_btn', None), "Open QuickBooks timer")
        bind_tip(getattr(self, 'timer_close_btn', None), "Close QuickBooks timer")
        bind_tip(getattr(self, 'theme_btn', None), "Change theme + animation settings")
        bind_tip(getattr(self, 'history_btn', None), "View saved log history")
        bind_tip(getattr(self, 'run_macro_btn', None), "Run QuickBooks macro (F2)")
        bind_tip(getattr(self, 'set_coord_btn', None), "Set QuickBooks field coords (F3)")
        bind_tip(getattr(self, 'set_date_coord_btn', None), "Set QuickBooks date field coord")

    def _cancel_tooltip(self):
        try:
            if self._tooltip_job is not None:
                self.after_cancel(self._tooltip_job)
        except Exception:
            pass
        self._tooltip_job = None

    def _show_tooltip(self, widget, text: str):
        self._hide_tooltip()
        try:
            t = self.themes.get(self.current_theme, self.themes['dark'])
            tip = ctk.CTkToplevel(self)
            tip.overrideredirect(True)
            tip.attributes('-topmost', True)

            frame = ctk.CTkFrame(tip, fg_color=t['surface2'], corner_radius=12, border_width=1, border_color=t['border'])
            frame.pack(fill="both", expand=True)
            label = ctk.CTkLabel(frame, text=text, font=("Segoe UI", 12), text_color=t['text'])
            label.pack(padx=10, pady=8)

            x = self.winfo_pointerx() + 12
            y = self.winfo_pointery() + 12
            tip.geometry(f"+{x}+{y}")

            self._tooltip_win = tip
        except Exception:
            self._tooltip_win = None

    def _hide_tooltip(self):
        try:
            if self._tooltip_win is not None and self._tooltip_win.winfo_exists():
                self._tooltip_win.destroy()
        except Exception:
            pass
        self._tooltip_win = None

    def _refresh_background_palette(self):
        t = self.themes.get(self.current_theme, self.themes['dark'])
        accent = t.get('accent', COLOR_ACCENT)
        try:
            r, g, b = hex_to_rgb(accent)
            def mix(frac):
                rr = int(r + (255 - r) * frac)
                gg = int(g + (255 - g) * frac)
                bb = int(b + (255 - b) * frac)
                return rgb_to_hex((rr, gg, bb))
            self._bg_palette = [accent, mix(0.25), mix(0.45), mix(0.65)]
        except Exception:
            self._bg_palette = [COLOR_ACCENT, "#93c5fd", "#dbeafe", "#60a5fa"]

    def _popup_fade_in(self, win):
        if self.reduce_motion:
            return
        try:
            win.attributes('-alpha', 0.0)
            def step(i=0):
                if not win.winfo_exists():
                    return
                a = min(1.0, i / 10)
                try:
                    win.attributes('-alpha', a)
                except Exception:
                    return
                if a < 1.0:
                    win.after(15, lambda: step(i + 1))
            step(0)
        except Exception:
            pass

    def _popup_fade_out(self, win):
        if self.reduce_motion:
            try:
                win.destroy()
            except Exception:
                pass
            return
        try:
            def step(i=10):
                if not win.winfo_exists():
                    return
                a = max(0.0, i / 10)
                try:
                    win.attributes('-alpha', a)
                except Exception:
                    try:
                        win.destroy()
                    except Exception:
                        pass
                    return
                if a > 0.0:
                    win.after(15, lambda: step(i - 1))
                else:
                    win.destroy()
            step(10)
        except Exception:
            try:
                win.destroy()
            except Exception:
                pass

    def show_toast(self, message: str, kind: str = "info"):
        try:
            t = self.themes.get(self.current_theme, self.themes['dark'])
            colors = {
                'info': t.get('accent', COLOR_ACCENT),
                'success': COLOR_SUCCESS,
                'warning': COLOR_WARNING,
                'error': COLOR_DANGER,
            }
            bg = colors.get(kind, t.get('accent', COLOR_ACCENT))

            toast = ctk.CTkToplevel(self)
            toast.overrideredirect(True)
            toast.attributes('-topmost', True)

            width = 280
            height = 52
            x = self.winfo_x() + self.winfo_width() - width - 18
            y = self.winfo_y() + 18 + (len(self._toasts) * (height + 10))
            toast.geometry(f"{width}x{height}+{x}+{y}")

            frame = ctk.CTkFrame(toast, fg_color=bg, corner_radius=14)
            frame.pack(fill="both", expand=True)
            label = ctk.CTkLabel(frame, text=message, font=("Segoe UI", 13, "bold"), text_color="#ffffff")
            label.pack(padx=14, pady=12, anchor="w")

            self._toasts.append(toast)

            def close():
                try:
                    if toast in self._toasts:
                        self._toasts.remove(toast)
                    toast.destroy()
                except Exception:
                    pass
                self._reposition_toasts()

            toast.after(int(getattr(self, 'toast_duration_ms', 2200)), close)
            self._reposition_toasts()
        except Exception:
            pass

    def _reposition_toasts(self):
        try:
            width = 280
            height = 52
            for i, toast in enumerate(list(self._toasts)):
                if not toast.winfo_exists():
                    continue
                x = self.winfo_x() + self.winfo_width() - width - 18
                y = self.winfo_y() + 18 + (i * (height + 10))
                toast.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def _setup_focus_effects(self):
        t = self.themes.get(self.current_theme, self.themes['dark'])
        focus = t.get('accent', COLOR_ACCENT)
        normal = t.get('border', COLOR_BORDER)

        def bind_focus(w):
            if w is None:
                return
            try:
                w.bind("<FocusIn>", lambda e: w.configure(border_color=focus))
                w.bind("<FocusOut>", lambda e: w.configure(border_color=normal))
            except Exception:
                pass

        for w in (
            getattr(self, 'start_time_entry', None),
            getattr(self, 'end_time_entry', None),
            getattr(self, 'date_entry', None),
            getattr(self, 'hours_menu', None),
            getattr(self, 'minutes_menu', None),
        ):
            bind_focus(w)

    def _setup_smooth_hovers(self):
        buttons = []
        for name in (
            'timer_open_btn',
            'timer_close_btn',
            'theme_btn',
            'history_btn',
            'run_macro_btn',
            'set_coord_btn',
            'help_btn',
            'set_date_coord_btn',
            'svc_btn',
            'bak_btn',
            'onsite_btn',
            'custom_btn',
        ):
            b = getattr(self, name, None)
            if b is not None:
                buttons.append(b)

        for b in buttons:
            try:
                base = b.cget('fg_color')
                hover = b.cget('hover_color')
                b.configure(hover_color=base)
                b.bind("<Enter>", lambda e, w=b, a=base, h=hover: self._hover_to(w, a, h), add="+")
                b.bind("<Leave>", lambda e, w=b, a=base, h=hover: self._hover_to(w, h, a), add="+")
            except Exception:
                pass

    def _hover_to(self, widget, start_color: str, end_color: str):
        if self.reduce_motion:
            try:
                widget.configure(fg_color=end_color)
            except Exception:
                pass
            return
        wid = str(widget)
        try:
            if wid in self._hover_anims:
                self.after_cancel(self._hover_anims[wid])
        except Exception:
            pass

        steps = 10
        delay = 12

        try:
            sr, sg, sb = hex_to_rgb(start_color)
            er, eg, eb = hex_to_rgb(end_color)
        except Exception:
            try:
                widget.configure(fg_color=end_color)
            except Exception:
                pass
            return

        def step(i=0):
            if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
                return
            f = i / steps
            r = int(sr + (er - sr) * f)
            g = int(sg + (eg - sg) * f)
            b = int(sb + (eb - sb) * f)
            try:
                widget.configure(fg_color=rgb_to_hex((r, g, b)))
            except Exception:
                return
            if i < steps:
                self._hover_anims[wid] = self.after(delay, lambda: step(i + 1))

        step(0)

    def _start_background_effects(self):
        if not getattr(self, 'background_effects_enabled', True):
            try:
                if self._bg_anim_id is not None:
                    self.after_cancel(self._bg_anim_id)
                    self._bg_anim_id = None
            except Exception:
                pass
            try:
                self.main_bg_canvas.delete('bg')
            except Exception:
                pass
            try:
                self.sidebar_bg_canvas.delete('bg')
            except Exception:
                pass
            return

        if not hasattr(self, '_bg_palette'):
            self._refresh_background_palette()

        if not hasattr(self, '_bg_particles'):
            self._bg_particles = []
        if not hasattr(self, '_sb_particles'):
            self._sb_particles = []
        density = float(getattr(self, 'particle_density', 1.0))
        if density < 0.3:
            density = 0.3
        if density > 2.5:
            density = 2.5

        if len(self._bg_particles) == 0:
            self._init_particles(self.main_bg_canvas, self._bg_particles, count=max(8, int(22 * density)), tag='bg')
        if len(self._sb_particles) == 0:
            self._init_particles(self.sidebar_bg_canvas, self._sb_particles, count=max(3, int(8 * density)), tag='bg')

        if self._bg_anim_id is None:
            self._animate_background()

    def _init_particles(self, canvas, store, count: int, tag: str):
        try:
            w = max(1, canvas.winfo_width())
            h = max(1, canvas.winfo_height())
        except Exception:
            w, h = 1, 1

        for _ in range(count):
            try:
                x = random.uniform(0, w)
                y = random.uniform(0, h)
                r = random.uniform(1.4, 3.2) if canvas is self.main_bg_canvas else random.uniform(1.0, 2.3)
                vx = random.uniform(-0.35, 0.35)
                vy = random.uniform(-0.35, 0.35)
                color = random.choice(self._bg_palette)
                pid = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline='', tags=(tag,))
                store.append({'id': pid, 'x': x, 'y': y, 'r': r, 'vx': vx, 'vy': vy})
            except Exception:
                pass

    def _animate_background(self):
        if not getattr(self, 'background_effects_enabled', True):
            self._bg_anim_id = None
            return

        if not hasattr(self, '_bg_palette'):
            self._refresh_background_palette()

        self._tick_canvas_particles(self.main_bg_canvas, self._bg_particles)
        self._tick_canvas_particles(self.sidebar_bg_canvas, self._sb_particles)

        delay = 45 if self.reduce_motion else 33
        self._bg_anim_id = self.after(delay, self._animate_background)

    def _tick_canvas_particles(self, canvas, store):
        try:
            w = max(1, canvas.winfo_width())
            h = max(1, canvas.winfo_height())
        except Exception:
            return

        speed = float(getattr(self, 'particle_speed', 1.0))
        if speed < 0.3:
            speed = 0.3
        if speed > 3.0:
            speed = 3.0

        for p in list(store):
            try:
                p['x'] += p['vx'] * speed
                p['y'] += p['vy'] * speed
                if p['x'] <= 0 or p['x'] >= w:
                    p['vx'] *= -1
                if p['y'] <= 0 or p['y'] >= h:
                    p['vy'] *= -1
                r = p['r']
                canvas.coords(p['id'], p['x'] - r, p['y'] - r, p['x'] + r, p['y'] + r)
            except Exception:
                pass

    def _tick_wave(self, canvas, is_sidebar: bool):
        return

    def custom_check(self):
        """Show custom check dialog and process input"""
        dialog = CustomCheckDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            self.submit('c', dialog.result, dialog.category)

    def onsite_check(self):
        dialog = OnSiteDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.submit('c', dialog.result, category="On-Site")

    def on_mode_change(self, event=None):
        self.manual_frame.pack_forget()
        if self.mode_var.get() == "Manual":
            self.manual_frame.pack(after=self.duration_frame, pady=(20, 20), padx=30, fill="x")
            # Enable log preview hover/click
            self.log_preview.configure(cursor="hand2")
        else:
            self.manual_frame.pack_forget()
            # Reset log preview color and disable hover/click
            self.log_preview.configure(fg_color="#181b20", cursor="arrow")

    def on_start_time_combo(self, event=None):
        if self.start_time_var.get() == "Custom":
            self.start_time_entry.grid()
        else:
            self.start_time_entry.grid_remove()

    def submit(self, check_type, custom_message=None, category=None):
        # Ensure latest widget values are read (fix for AM/PM/date bug)
        try:
            self.focus()
        except Exception:
            pass
        self.update_idletasks()
        mode = self.mode_var.get()
        customer = self.selected_customer.get()
        if mode == "Manual":
            # Get and clean inputs
            start_time = self.start_time_entry.get().strip()
            start_period = self.start_time_period.get().strip().upper()
            end_time = self.end_time_entry.get().strip()
            end_period = self.end_time_period.get().strip().upper()
            date_str = self.date_entry.get().strip()

            # Helper function to validate and correct time
            def validate_and_correct_time(time_str, period, field_name):
                if not time_str.strip():
                    dialog = TimeEntryDialog(self, f"Enter {field_name} Time", f"Please enter a valid {field_name} time (HH:MM):")
                    self.wait_window(dialog)
                    if dialog.result:
                        t, p = dialog.result
                        return t, p
                    return None, None
                if ':' in time_str:
                    hour, minute = time_str.split(':', 1)
                    if len(hour) == 1:
                        hour = '0' + hour
                    if len(minute) == 1:
                        minute = '0' + minute
                    time_str = f"{hour}:{minute}"
                try:
                    test_time = f"{time_str} {period}"
                    datetime.strptime(test_time, "%I:%M %p")
                    return time_str, period
                except ValueError:
                    dialog = TimeEntryDialog(self, f"Enter {field_name} Time", f"Please enter a valid {field_name} time (HH:MM):")
                    self.wait_window(dialog)
                    if dialog.result:
                        t, p = dialog.result
                        return t, p
                    return None, None

            # Validate start time
            start_time, start_period = validate_and_correct_time(start_time, start_period, "Start")
            if start_time is None:
                self.status.configure(text="Start time is required", text_color="#ef4444")
                return
            # Validate end time
            end_time, end_period = validate_and_correct_time(end_time, end_period, "End")
            if end_time is None:
                self.status.configure(text="End time is required", text_color="#ef4444")
                return
            # Validate date format if provided (MM/DD/YYYY)
            if date_str:
                date_pattern = r"^(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}$"
                if not re.match(date_pattern, date_str):
                    self.status.configure(text="Invalid date format", text_color="#ef4444")
                    return
            else:
                date_str = datetime.now().strftime("%m/%d/%Y")

            # Parse times and calculate duration
            try:
                start_dt_str = f"{date_str} {start_time} {start_period}"
                end_dt_str = f"{date_str} {end_time} {end_period}"
                start_dt = datetime.strptime(start_dt_str, "%m/%d/%Y %I:%M %p")
                end_dt = datetime.strptime(end_dt_str, "%m/%d/%Y %I:%M %p")
                if end_dt <= start_dt:
                    self.status.configure(text="End time must be after start time", text_color="#ef4444")
                    return
                duration = (end_dt - start_dt).total_seconds() / 60
                duration_str = f"{duration:.0f} minutes"
                current_time = f"{start_dt.strftime('%m/%d/%Y')} {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
            except ValueError:
                self.status.configure(text="Invalid date or time", text_color="#ef4444")
                return
        else:  # Automatic mode
            now = datetime.now()
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            total_minutes = (hours * 60) + minutes
            
            # Calculate end time
            start_time = now
            end_time = now + timedelta(minutes=total_minutes)
            
            # Format times
            current_time = f"{start_time.strftime('%m/%d/%Y %I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            
            # Format duration string - only show hours if > 0
            if hours > 0:
                duration_str = f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                duration_str = f"{minutes} minute{'s' if minutes != 1 else ''}"

        customer = self.selected_customer.get()
        if customer == "No Customer":
            customer = ""

        log_entry = self.generate_log_entry(check_type, current_time, duration_str, custom_message, category)
        self.log_preview.configure(state="normal")
        self.log_preview.delete("0.0", "end")
        self.log_preview.insert("0.0", log_entry)
        self.log_preview.configure(state="disabled")

        if mode == "Automatic":
            self.status.configure(text="Log entry generated! Click to edit or submit again.", text_color="#6ee7b7")
        else:
            self.status.configure(text="Log entry generated with custom times!", text_color="#6ee7b7")

        # Save log entry
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desktop_path, exist_ok=True)
        file_path = os.path.join(desktop_path, "check_log.txt")

        with open(file_path, "a") as f:
            f.write(log_entry + "\n\n")

        # Save customer association if selected
        if customer:
            log_hash = hashlib.md5(log_entry.encode()).hexdigest()
            metadata = {"customer": customer}
            metadata_file = os.path.join(desktop_path, "log_metadata.json")
            try:
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as mf:
                        existing_metadata = json.load(mf)
                else:
                    existing_metadata = {}

                existing_metadata[log_hash] = metadata

                with open(metadata_file, "w") as mf:
                    json.dump(existing_metadata, mf, indent=2)
            except Exception as e:
                print(f"Error saving metadata: {e}")

        # Show success indicator
        self.status.configure(text="Log entry saved successfully!", text_color="#6ee7b7")
        pyperclip.copy(log_entry)
        self.after(3000, lambda: self.status.configure(text=""))

    def get_timer_path(self):
        """Get the QuickBooks Timer path from config or prompt the user if not set or invalid."""
        config_file = os.path.join(get_app_dir(), "timer_path.json")
        timer_path = None
        # Try to load from config
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    timer_path = json.load(f).get("timer_path")
            except Exception:
                timer_path = None
        # If not set or invalid, prompt the user
        # Updated default_dir to the correct path
        default_dir = r"C:\\Program Files (x86)\\Intuit\\QuickBooks\\QuickBooks Pro Timer"
        while not timer_path or not os.path.exists(timer_path):
            from tkinter import filedialog, messagebox
            timer_path = filedialog.askopenfilename(
                title="Locate QuickBooks Pro Timer (timer.exe)",
                filetypes=[("Executable", "timer.exe")],
                initialdir=default_dir if os.path.exists(default_dir) else os.path.expanduser("~")
            )
            if not timer_path:
                messagebox.showerror("Path Required", "You must select timer.exe to use this feature.")
                return None
            if not os.path.exists(timer_path):
                messagebox.showerror("Invalid Path", f"The selected file does not exist: {timer_path}")
                timer_path = None
        # Save to config
        try:
            with open(config_file, "w") as f:
                json.dump({"timer_path": timer_path}, f)
        except Exception:
            pass
        return timer_path

    def open_quickbooks_timer(self):
        """Open QuickBooks Pro Timer (timer.exe) if available, prompting for path if needed."""
        import subprocess
        timer_path = self.get_timer_path()
        if not timer_path:
            self.status.configure(text="Timer path not set.", text_color="#ef4444")
            return
        try:
            subprocess.Popen([timer_path], shell=True)
        except Exception as e:
            self.status.configure(text=f"Could not open Timer: {e}", text_color="#ef4444")

    def close_quickbooks_timer(self):
        """Terminate all running qbtimer.exe processes."""
        import subprocess
        try:
            result = subprocess.run(["taskkill", "/f", "/im", "qbtimer.exe"], capture_output=True, text=True)
            if result.returncode == 0:
                self.status.configure(text="QuickBooks Timer closed.", text_color="#6ee7b7")
            else:
                if "not found" in result.stdout.lower() or "not found" in result.stderr.lower():
                    self.status.configure(text="No running QuickBooks Timer found.", text_color="#a3a3a3")
                else:
                    self.status.configure(text=f"Error closing Timer: {result.stderr}", text_color="#ef4444")
        except Exception as e:
            self.status.configure(text=f"Error closing Timer: {e}", text_color="#ef4444")

    def show_history(self):
        from tkinter import messagebox
        import json
        import hashlib
        # --- Helper functions for log file ---
        def read_log_entries():
            if not os.path.exists(file_path):
                return []
            with open(file_path, "r") as f:
                lines = f.readlines()
            entries = []
            current = []
            for line in lines:
                if line.strip().startswith("[") and current:
                    entries.append("".join(current).strip())
                    current = [line]
                else:
                    current.append(line)
            if current:
                entries.append("".join(current).strip())
            return entries
        def write_log_entries(entries):
            with open(file_path, "w") as f:
                for entry in entries:
                    f.write(entry.strip() + "\n\n")
        # --- End helpers ---
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        os.makedirs(desktop_path, exist_ok=True)
        file_path = os.path.join(desktop_path, "check_log.txt")
        entries = read_log_entries()
        # --- History Dialog ---
        history_win = ctk.CTkToplevel(self)
        history_win.title("Log History Viewer")
        history_win.geometry("850x650")
        history_win.resizable(True, True)
        history_win.configure(fg_color="#16181d")
        history_win.transient(self)
        history_win.attributes('-topmost', True)
        history_win.lift()
        history_win.after(200, lambda: history_win.attributes('-topmost', False))
        # --- Top Bar with Title and Search ---
        top_bar = ctk.CTkFrame(history_win, fg_color="#191b22", corner_radius=0)
        top_bar.pack(pady=0, padx=0, fill="x")
        title_label = ctk.CTkLabel(top_bar, text="Log History Viewer", font=("Segoe UI Semibold", 18), text_color="#f1f5f9")
        title_label.pack(side="left", padx=15, pady=10)
        search_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        search_frame.pack(side="right", padx=15, pady=10)
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            width=250,
            font=("Segoe UI", 14),
            fg_color="#23272f",
            text_color="#f1f5f9",
            border_width=1,
            border_color="#374151",
            placeholder_text="Search logs...",
            textvariable=search_var
        )
        search_entry.pack(side="left", padx=(0, 5))
        search_btn = ctk.CTkButton(search_frame, text="🔍", width=40, height=32, corner_radius=8, font=("Segoe UI", 14), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9")
        search_btn.pack(side="left")
        # --- Filter Panel (Collapsible) ---
        filter_frame = ctk.CTkFrame(history_win, fg_color="#191b22", corner_radius=10)
        filter_frame.pack(pady=5, padx=10, fill="x")
        filter_toggle_btn = ctk.CTkButton(filter_frame, text="Filters ▼", width=120, height=32, corner_radius=8, font=("Segoe UI", 14), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9")
        filter_toggle_btn.pack(side="left", padx=10)
        filter_options_frame = ctk.CTkFrame(filter_frame, fg_color="#191b22", corner_radius=10)
        # Do not pack filter_options_frame yet, toggle will handle it
        # Customer filter removed but keeping customer_filter_var for compatibility
        customer_filter_var = ctk.StringVar(value="")
        
        # Sort logs option (newest first or oldest first)
        sort_logs_label = ctk.CTkLabel(filter_options_frame, text="Log Sort:")
        sort_logs_label.pack(side="left", padx=5, pady=5)
        
        sort_logs_newest_var = ctk.BooleanVar(value=True)
        sort_logs_newest_check = ctk.CTkCheckBox(filter_options_frame, text="Newest First", variable=sort_logs_newest_var)
        sort_logs_newest_check.pack(side="left", padx=5, pady=5)
        
        # Apply filter button
        def apply_filters():
            filter_text = search_var.get().strip().lower()
            log_sort_order = "Newest" if sort_logs_newest_var.get() else "Oldest"
            filtered = []
            for i, e in enumerate(entries):
                entry_str = str(e)
                if filter_text and filter_text not in entry_str.lower():
                    continue
                filtered.append((i, e))
            # Sort by date
            if log_sort_order == "Newest":
                filtered.reverse()
            refresh_entries(filtered)
        apply_filter_btn = ctk.CTkButton(filter_options_frame, text="Apply Filters", fg_color="#3b82f6", hover_color="#2563eb", font=("Segoe UI", 12, "bold"), command=apply_filters)
        apply_filter_btn.pack(side="left", padx=10, pady=5)
        # --- Scrollable Frame for Entries ---
        scroll_frame = ctk.CTkScrollableFrame(history_win, fg_color="#18181b", border_width=1, border_color="#374151")
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)
        # --- Undo buffer for deleted entries ---
        self._deleted_log_entry = None
        self._deleted_log_index = None
        def refresh_entries(filtered_entries=None):
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            if filtered_entries is None:
                filtered_entries = list(enumerate(entries))
            if not filtered_entries:
                no_entries_label = ctk.CTkLabel(scroll_frame, text="No log entries found.", font=("Segoe UI", 16), text_color="#9ca3af")
                no_entries_label.pack(pady=20)
            else:
                for idx, (entry_idx, entry) in enumerate(filtered_entries):
                    entry_frame = ctk.CTkFrame(scroll_frame, fg_color="#23272f", border_width=1, border_color="#374151")
                    entry_frame.pack(fill="x", pady=6, padx=4)
                    # Entry text (read-only textbox)
                    entry_text = ctk.CTkTextbox(entry_frame, width=440, height=80, font=("Consolas", 12), fg_color="#181b20", text_color="#f1f5f9", border_width=0)
                    entry_text.insert("0.0", entry)
                    entry_text.configure(state="disabled")
                    entry_text.pack(side="left", padx=(8, 0), pady=6, fill="x", expand=True)
                    # Button frame
                    btn_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
                    btn_frame.pack(side="right", padx=8, pady=6)
                    # Edit button
                    def edit_entry(entry_idx=entry_idx, entry=entry):
                        edit_win = ctk.CTkToplevel(history_win)
                        edit_win.title("Edit Log Entry")
                        edit_win.geometry("500x300")
                        edit_win.configure(fg_color="#23272f")
                        edit_win.transient(history_win)
                        edit_win.attributes('-topmost', True)
                        edit_win.lift()
                        edit_win.after(200, lambda: edit_win.attributes('-topmost', False))
                        label = ctk.CTkLabel(edit_win, text="Edit Log Entry", font=("Segoe UI", 16, "bold"), text_color="#f1f5f9")
                        label.pack(pady=(20, 10))
                        text_box = ctk.CTkTextbox(edit_win, width=440, height=140, font=("Consolas", 12), fg_color="#18181b", text_color="#f1f5f9", border_width=1, border_color="#374151")
                        text_box.pack(padx=20, pady=10)
                        text_box.insert("0.0", entry)
                        def save_edit():
                            new_text = text_box.get("0.0", "end").strip()
                            if new_text:
                                entries[entry_idx] = new_text
                                write_log_entries(entries)
                                refresh_entries_based_on_search()
                                edit_win.destroy()
                        save_btn = ctk.CTkButton(edit_win, text="Save", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=save_edit)
                        save_btn.pack(pady=(0, 20))
                    edit_btn = ctk.CTkButton(btn_frame, text="Edit", width=60, height=28, corner_radius=8, font=("Segoe UI", 12), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=edit_entry)
                    edit_btn.pack(pady=2)
                    # Delete button
                    def delete_entry(entry_idx=entry_idx):
                        self._deleted_log_entry = entries[entry_idx]
                        self._deleted_log_index = entry_idx
                        del entries[entry_idx]
                        write_log_entries(entries)
                        refresh_entries_based_on_search()
                    delete_btn = ctk.CTkButton(btn_frame, text="Delete", width=60, height=28, corner_radius=8, font=("Segoe UI", 12), fg_color="#ef4444", hover_color="#dc2626", text_color="#f1f5f9", command=delete_entry)
                    delete_btn.pack(pady=2)
                    # Copy button
                    def copy_entry(entry=entry):
                        pyperclip.copy(entry)
                    copy_btn = ctk.CTkButton(btn_frame, text="Copy", width=60, height=28, corner_radius=8, font=("Segoe UI", 12), fg_color="#64748b", hover_color="#334155", text_color="#f1f5f9", command=copy_entry)
                    copy_btn.pack(pady=2)
                    # Customer button
                    meta_path = os.path.join(desktop_path, "log_metadata.json")
                    try:
                        customer_meta = json.load(open(meta_path))
                    except (FileNotFoundError, json.JSONDecodeError):
                        customer_meta = {}
                    log_hash = hashlib.md5(entry.strip().encode("utf-8")).hexdigest()
                    entry_customer = customer_meta.get(log_hash, "No Customer")
                    cust_btn = ctk.CTkButton(btn_frame, text="Customer", width=60, height=28, corner_radius=8, font=("Segoe UI", 12), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=lambda c=entry_customer: messagebox.showinfo("Customer", f"Customer: {c['customer']}" if isinstance(c, dict) and "customer" in c else "No Customer"))
                    cust_btn.pack(pady=2)
        # --- Bottom Action Bar ---
        action_bar = ctk.CTkFrame(history_win, fg_color="#191b22", corner_radius=0)
        action_bar.pack(fill="x", padx=0, pady=0, side="bottom")
        # --- Undo delete button ---
        def undo_delete():
            if self._deleted_log_entry is not None and self._deleted_log_index is not None:
                entries.insert(self._deleted_log_index, self._deleted_log_entry)
                write_log_entries(entries)
                refresh_entries_based_on_search()
                self._deleted_log_entry = None
                self._deleted_log_index = None
        undo_btn = ctk.CTkButton(action_bar, text="Undo Delete", width=120, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#f59e42", hover_color="#ea580c", text_color="#f1f5f9", command=undo_delete)
        undo_btn.pack(side="left", padx=10, pady=10)
        # --- Delete All button ---
        def delete_all():
            from tkinter import messagebox
            if len(entries) == 0:
                messagebox.showinfo("Delete All", "No log entries to delete.")
                return
            if messagebox.askyesno("Delete All", "Are you sure you want to delete all log entries? This cannot be undone."):
                entries.clear()
                write_log_entries(entries)
                refresh_entries_based_on_search()
        delete_all_btn = ctk.CTkButton(action_bar, text="Delete All", width=120, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#ef4444", hover_color="#dc2626", text_color="#f1f5f9", command=delete_all)
        delete_all_btn.pack(side="left", padx=5, pady=10)
        # --- Refresh Button ---
        def on_refresh():
            nonlocal entries
            entries = read_log_entries()
            # update_customer_dropdown()  # Update customer list on refresh (function not defined)
            refresh_entries_based_on_search()
        refresh_btn = ctk.CTkButton(action_bar, text="Refresh", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=on_refresh)
        refresh_btn.pack(side="right", padx=5, pady=10)
        close_btn = ctk.CTkButton(action_bar, text="Close", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#64748b", hover_color="#334155", text_color="#f1f5f9", command=history_win.destroy)
        close_btn.pack(side="right", padx=10, pady=10)
        # --- Toggle Filters Function ---
        def toggle_filters():
            if filter_options_frame.winfo_ismapped():
                filter_options_frame.pack_forget()
                filter_toggle_btn.configure(text="Filters ▼")
            else:
                filter_options_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                filter_toggle_btn.configure(text="Filters ▲")
        filter_toggle_btn.configure(command=toggle_filters)
        # --- Apply Filters Function ---
        def apply_filters():
            filter_text = search_var.get().strip().lower()
            customer = customer_filter_var.get()
            log_sort_order = "Newest" if sort_logs_newest_var.get() else "Oldest"
            filtered = []
            for i, e in enumerate(entries):
                entry_str = str(e)
                if filter_text and filter_text not in entry_str.lower():
                    continue
                if customer and customer != "No Customer":
                    meta_path = os.path.join(desktop_path, "log_metadata.json")
                    try:
                        customer_meta = json.load(open(meta_path))
                    except (FileNotFoundError, json.JSONDecodeError):
                        customer_meta = {}
                    log_hash = hashlib.md5(entry_str.strip().encode("utf-8")).hexdigest()
                    entry_customer = customer_meta.get(log_hash, "No Customer")
                    if entry_customer != customer:
                        continue
                filtered.append((i, e))
            # Sort by date
            if log_sort_order == "Newest":
                filtered.reverse()
            refresh_entries(filtered)
        apply_filter_btn.configure(command=apply_filters)
        # --- Search Function ---
        def refresh_entries_based_on_search():
            filter_text = search_var.get().strip().lower()
            filtered = [(i, e) for i, e in enumerate(entries) if filter_text in str(e).lower() or not filter_text]
            refresh_entries(filtered)
        search_var.trace_add('write', lambda *args: refresh_entries_based_on_search())
        search_btn.configure(command=refresh_entries_based_on_search)
        # Initial display
        refresh_entries([(i, e) for i, e in enumerate(entries)])
        history_win.after(100, lambda: history_win.focus_force())

    def _on_log_preview_enter(self, event=None):
        self._log_preview_target_color = "#2563eb"
        if not self._log_preview_animating:
            self._log_preview_animating = True
            self._animate_log_preview_bg()

    def _on_log_preview_leave(self, event=None):
        self._log_preview_target_color = "#181b20"
        if not self._log_preview_animating:
            self._log_preview_animating = True
            self._animate_log_preview_bg()

    def _on_log_preview_click(self, event=None):
        self.show_edit_dialog()

    def _animate_log_preview_bg(self):
        # Smoothly animate background color to target
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        cur = hex_to_rgb(self._log_preview_current_color)
        tgt = hex_to_rgb(self._log_preview_target_color)
        step = 12
        new = []
        done = True
        for c, t in zip(cur, tgt):
            if abs(c - t) <= step:
                new.append(t)
            else:
                done = False
                if c < t:
                    new.append(c + step)
                else:
                    new.append(c - step)
        self._log_preview_current_color = rgb_to_hex(tuple(new))
        self.log_preview.configure(fg_color=self._log_preview_current_color)
        if not done:
            self.after(12, self._animate_log_preview_bg)
        else:
            self._log_preview_animating = False

    def clear_customer_selection(self):
        self.selected_customer.set("No Customer")
        self.customer_display.configure(text="No Customer")
        self.status.configure(text="Customer selection cleared", text_color="#6ee7b7")
        self.after(3000, lambda: self.status.configure(text=""))

    def open_customer_dialog(self):
        dlg = CustomerManagementDialog(self)          # modal
        self.wait_window(dlg)
        self.customer_display.configure(text=self.selected_customer.get())

    def _draw_border_animation(self):
        if hasattr(self, '_animation_id'):
            self.after_cancel(self._animation_id)
        self.border_canvas.delete("border")
        thickness = 3
        offset = 1
        w, h = self.winfo_width(), self.winfo_height()
        # Draw border with animation
        border_color = self._get_next_color()
        self.border_canvas.create_rectangle(
            offset, offset, w - offset, h - offset, outline=border_color, width=thickness, tags="border"
        )
        # Schedule next animation frame
        self._animation_id = self.after(30, self._draw_border_animation)

    def _get_next_color(self):
        # Smooth RGB color transition
        if not hasattr(self, '_color_phase'):
            self._color_phase = 0
        self._color_phase = (self._color_phase + 1) % 360
        r = int(255 * (0.5 + 0.5 * math.sin(math.radians(self._color_phase))))
        g = int(255 * (0.5 + 0.5 * math.sin(math.radians(self._color_phase + 120))))
        b = int(255 * (0.5 + 0.5 * math.sin(math.radians(self._color_phase + 240))))
        return f"#{r:02x}{g:02x}{b:02x}"

    def generate_log_entry(self, check_type, current_time, duration_str, custom_message=None, category=None):
        # Format: [date][Start: start_time][check_name] message [End: end_time] [Duration X mins]
        log_messages = {
            's': "Logged onto Servers. Checked system logs, DNS and DHCP entries, disk health and usage. Checked ESET logs. Checked volume shadow copies.",
            'b': "Logged onto Servers. Checked backup jobs. Checked data integrity and verified that all jobs finished successfully.",
            'o': "On-site support provided. Issues resolved."
        }
        
        if check_type == 'c' and custom_message:
            message = custom_message
            check_name = category if category else "Custom Check"
        else:
            message = log_messages.get(check_type, "")
            check_name = 'Service Check' if check_type == 's' else 'Backup Check'
        
        try:
            if ' - ' in current_time:  # Manual mode with start and end times
                date_part = current_time.split(' ')[0]
                times = ' '.join(current_time.split(' ')[1:])
                start_time, end_time = times.split(' - ')
                entry = f"[{date_part}][Start: {start_time}][{check_name}] {message} [End: {end_time}] [Duration: {duration_str}]"
            else:
                # Automatic mode: use current_time for both start and end
                date_part, time_part, period = current_time.split()
                entry = f"[{date_part}][Start: {time_part} {period}][{check_name}] {message} [End: {time_part} {period}] [Duration: {duration_str}]"
        except Exception as e:
            print(f"Error generating log entry: {e}")
            entry = f"[{current_time}][{check_name}] {message} [Duration: {duration_str}]"
            
        return entry

    def copy_log_text(self, event=None):
        selected_text = self.log_preview.get("sel.first", "sel.last")
        if selected_text:
            pyperclip.copy(selected_text)
            self.status.configure(text="Copied to clipboard", text_color="#6ee7b7")
        return "break"

    def enable_edit(self, event=None):
        self.log_preview.configure(state="normal")
        return "break"

    def show_edit_dialog(self, event=None):
        self.log_preview.configure(state="normal")
        current_text = self.log_preview.get("0.0", "end-1c")
        if current_text and current_text != "Log preview will appear here...":
            dialog = ctk.CTkToplevel(self)
            dialog.title("Edit Log Entry")
            dialog.geometry("500x300")
            dialog.resizable(False, False)
            dialog.configure(fg_color="#23272f")
            dialog.grab_set()
            x = self.winfo_x() + (self.winfo_width() - 500) // 2
            y = self.winfo_y() + (self.winfo_height() - 300) // 2
            dialog.geometry(f"+{x}+{y}")
            dialog.attributes('-alpha', 0.97)
            text_entry = ctk.CTkTextbox(dialog, width=450, height=200, font=("Segoe UI", 14), fg_color="#18181b", text_color="#f1f5f9", border_width=1, border_color="#374151")
            text_entry.pack(pady=10, padx=20)
            text_entry.insert("0.0", current_text)
            def save_changes():
                new_text = text_entry.get("0.0", "end-1c")
                self.log_preview.configure(state="normal")
                self.log_preview.delete("0.0", "end")
                self.log_preview.insert("0.0", new_text)
                self.log_preview.configure(state="disabled")
                pyperclip.copy(new_text)
                self.status.configure(text="Log updated and copied to clipboard", text_color="#6ee7b7")
                dialog.destroy()
            save_btn = ctk.CTkButton(dialog, text="Save", width=100, height=32, corner_radius=8, font=("Segoe UI", 13), fg_color="#2563eb", hover_color="#1d4ed8", text_color="#f1f5f9", command=save_changes)
            save_btn.pack(pady=(0, 20))
            dialog.bind("<Return>", lambda event: save_changes())
            dialog.bind("<Escape>", lambda event: dialog.destroy())
            dialog.after(100, lambda: text_entry.focus())

    # New method for 'Run QB Macro' button
    def run_qb_macro(self):
        cancel_flag = False
        def on_alt_press():
            nonlocal cancel_flag
            cancel_flag = True
        keyboard.add_hotkey('alt', on_alt_press)
        type_dialog = MacroTypeDialog(self)
        self.wait_window(type_dialog)
        result = type_dialog.result
        
        try:
            if cancel_flag or result is None:
                raise Exception("Macro was canceled.")
            
            if result["mode"] == "automatic":
                selected_type = result["type"]
                if selected_type == "Service Check":
                    check_type = 's'
                    check_name = 'Service Check'
                    message = globals()['log_messages']['s']
                elif selected_type == "Backup Check":
                    check_type = 'b'
                    check_name = 'Backup Check'
                    message = globals()['log_messages']['b']
                elif selected_type == "On-Site Check":
                    onsite_dialog = OnSiteDialog(self)
                    self.wait_window(onsite_dialog)
                    if onsite_dialog.result is None:
                        raise Exception("On-Site selection canceled.")
                    check_name = 'On-Site Check'
                    message = onsite_dialog.result
                elif selected_type == "Custom Check":
                    custom_dialog = CustomCheckDialog(self)
                    self.wait_window(custom_dialog)
                    if custom_dialog.result is None or custom_dialog.category is None:
                        raise Exception("Custom check selection canceled.")
                    check_name = custom_dialog.category
                    message = custom_dialog.result
                else:
                    raise Exception("Invalid check type selected.")
                
                hours = self.hours_var.get()
                minutes = self.minutes_var.get()
                if not hours.isdigit() or not minutes.isdigit() or int(minutes) > 59 or int(minutes) < 0 or int(hours) < 0:
                    raise Exception("Invalid duration entered.")
                hours = int(hours)
                minutes = int(minutes)
                total_minutes = hours * 60 + minutes
                
                start_time = datetime.now()
                end_time = start_time + timedelta(minutes=total_minutes)
                
                date_str = format_date(start_time)
                start_time_str = format_time(start_time)
                end_time_str = format_time(end_time)
                
                full_note = f"[{date_str}][Start: {start_time_str}][{check_name}] {message} [End: {end_time_str}] [Duration: {total_minutes} minutes]"
                
                if not cancel_flag:
                    pyautogui.click(globals()['QB_NEW_ACTIVITY_COORDS'])
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                customer_name = self.selected_customer.get()
                if customer_name and customer_name != "No Customer":
                    if not cancel_flag:
                        pyautogui.click(globals()['QB_CUSTOMER_COORDS'])
                        pyautogui.typewrite(customer_name)
                if not cancel_flag:
                    pyautogui.click(globals()['QB_SERVICE_ITEM_COORDS'])
                    pyautogui.typewrite('Network Support')
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                if not cancel_flag:
                    pyautogui.click(globals()['QB_DURATION_COORDS'])
                    pyautogui.typewrite(str(total_minutes))
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                if not cancel_flag:
                    pyautogui.click(globals()['QB_NOTES_COORDS'])
                    pyautogui.typewrite(full_note)
                messagebox.showinfo("Macro Completed", "QuickBooks macro ran successfully.", parent=self)
                try:
                    self.status.configure(text="Macro completed", text_color="#6ee7b7")
                except AttributeError:
                    print("Status label not found, skipping update.")
            elif result["mode"] == "manual":
                selected_type = result["type"]
                if selected_type == "Service Check":
                    check_type = 's'
                    check_name = 'Service Check'
                    message = globals()['log_messages']['s']
                elif selected_type == "Backup Check":
                    check_type = 'b'
                    check_name = 'Backup Check'
                    message = globals()['log_messages']['b']
                elif selected_type == "On-Site Check":
                    onsite_dialog = OnSiteDialog(self)
                    self.wait_window(onsite_dialog)
                    if onsite_dialog.result is None:
                        raise Exception("On-Site selection canceled.")
                    check_name = 'On-Site Check'
                    message = onsite_dialog.result
                elif selected_type == "Custom Check":
                    custom_dialog = CustomCheckDialog(self)
                    self.wait_window(custom_dialog)
                    if custom_dialog.result is None or custom_dialog.category is None:
                        raise Exception("Custom check selection canceled.")
                    check_name = custom_dialog.category
                    message = custom_dialog.result
                else:
                    raise Exception("Invalid check type selected.")
                
                start_time_str = result["start_time"]
                end_time_str = result["end_time"]
                duration_minutes = result["duration"]
                date_str = result.get("date", format_date(datetime.now()))
                start_datetime = datetime.strptime(start_time_str, "%I:%M %p")
                end_datetime = datetime.strptime(end_time_str, "%I:%M %p")
                start_full_datetime = datetime.combine(datetime.now().date(), start_datetime.time())
                end_full_datetime = datetime.combine(datetime.now().date(), end_datetime.time())
                full_note = f"[{date_str}][Start: {start_time_str}][{check_name}] {message} [End: {end_time_str}] [Duration: {duration_minutes} minutes]"

                if not cancel_flag:
                    pyautogui.click(globals()['QB_NEW_ACTIVITY_COORDS'])
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                # Handle date input only in manual mode and only if a date is provided
                if result.get("mode") == "manual":
                    # Only run the date sequence if a date was input (not blank and not today's date)
                    if result.get("date") and result.get("date") != format_date(datetime.now()):
                        if not cancel_flag:
                            pyautogui.click(globals()['QB_DATE_COORDS'])
                            time.sleep(0.05)  # Minimal wait for field selection
                            # Delete 15 times to ensure field is completely clear
                            for _ in range(15):  # Delete 15 times to ensure field is completely clear
                                pyautogui.press('delete')
                                time.sleep(0.01)  # Small delay for faster but reliable deletion
                            time.sleep(0.02)  # Minimal wait after clearing
                            # Extract just the date part without brackets or other formatting
                            date_to_enter = result.get("date").strip('[]')
                            # Type the entire date at once after clearing
                            pyautogui.typewrite(date_to_enter)
                            time.sleep(0.02)  # Minimal wait after typing
                            pyautogui.press('tab')  # Press tab to move to next field and confirm input
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                customer_name = self.selected_customer.get()
                if customer_name and customer_name != "No Customer":
                    if not cancel_flag:
                        pyautogui.click(globals()['QB_CUSTOMER_COORDS'])
                        pyautogui.typewrite(customer_name)
                if not cancel_flag:
                    pyautogui.click(globals()['QB_SERVICE_ITEM_COORDS'])
                    pyautogui.typewrite('Network Support')
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                if not cancel_flag:
                    pyautogui.click(globals()['QB_DURATION_COORDS'])
                    pyautogui.typewrite(str(duration_minutes))
                if cancel_flag:
                    raise Exception("Macro canceled by user")
                if not cancel_flag:
                    pyautogui.click(globals()['QB_NOTES_COORDS'])
                    pyautogui.typewrite(full_note)
                messagebox.showinfo("Macro Completed", "QuickBooks macro ran successfully.", parent=self)
                try:
                    self.status.configure(text="Macro completed", text_color="#6ee7b7")
                except AttributeError:
                    print("Status label not found, skipping update.")
            else:
                raise Exception("Invalid mode selected.")
        except Exception as e:
            messagebox.showerror("Macro Error", f"An error occurred: {str(e)}", parent=self)
            try:
                self.status.configure(text="Macro error", text_color="#ef4444")
            except AttributeError:
                print("Status label not found, skipping update.")
        finally:
            try:
                keyboard.remove_hotkey('alt')
            except KeyError:
                print("Hotkey 'alt' not found, skipping removal.")

    # New method for 'Set QB Coordinates' button
    def set_qb_coordinates(self):
        """Enhanced coordinate setting with exe compatibility"""
        try:
            # Ensure imports are available in exe environment
            import pyautogui
            import keyboard
            from tkinter import messagebox
            
            cancel_flag = False
            def on_alt_press():
                nonlocal cancel_flag
                cancel_flag = True
            
            # Add error handling for keyboard hook
            try:
                keyboard.add_hotkey('alt', on_alt_press)
            except Exception as e:
                print(f"Warning: Could not set Alt hotkey: {e}")
                messagebox.showwarning("Hotkey Warning", "Alt cancel hotkey may not work. Use Escape to cancel dialogs.", parent=self)
        
        except ImportError as e:
            messagebox.showerror("Import Error", f"Required modules not available: {e}\nPlease ensure pyautogui and keyboard are installed.", parent=self)
            return
        for label in ["New Activity", "Customer", "Service Item", "Notes", "Duration"]:
            messagebox.showinfo("Set Coordinates", f"Move mouse to '{label}' position. Press Ctrl to confirm. Press Alt to cancel.", parent=self)
            if cancel_flag:
                try:
                    keyboard.remove_hotkey('alt')
                except KeyError:
                    print("Hotkey 'alt' not found, skipping removal.")
                messagebox.showinfo("Coordinate Setting Canceled", "Process canceled by Alt key press.")
                return
            print(f"Waiting for Ctrl key press for '{label}'...")  # Debug log for key wait start
            keyboard.wait('ctrl')  # Indefinite wait reverted as per user request
            print(f"Ctrl key detected for '{label}'.")  # Debug log for key press detection
            if cancel_flag:
                try:
                    keyboard.remove_hotkey('alt')
                except KeyError:
                    print("Hotkey 'alt' not found, skipping removal.")
                messagebox.showinfo("Coordinate Setting Canceled", "Process canceled by Alt key press.")
                return
            pos = pyautogui.position()
            if label == "New Activity": globals()['QB_NEW_ACTIVITY_COORDS'] = pos
            elif label == "Customer": globals()['QB_CUSTOMER_COORDS'] = pos
            elif label == "Service Item": globals()['QB_SERVICE_ITEM_COORDS'] = pos
            elif label == "Notes": globals()['QB_NOTES_COORDS'] = pos
            elif label == "Duration": globals()['QB_DURATION_COORDS'] = pos
            self.save_coordinates()
            messagebox.showinfo("Coordinate Recorded", f"{label} coordinates set to {pos}", parent=self)
        if not cancel_flag:
            messagebox.showinfo("Coordinates Set", "All coordinates have been updated and saved. Use the 'Run QB Macro' button to test.", parent=self)
        try:
            keyboard.remove_hotkey('alt')
        except KeyError:
            print("Hotkey 'alt' not found, skipping removal.")

    def save_coordinates(self):
        """Enhanced coordinate saving with error handling and backup"""
        coord_file = os.path.join(get_app_dir(), 'qb_coordinates.json')
        backup_file = os.path.join(get_app_dir(), 'qb_coordinates_backup.json')
        
        coords = {
            'new_activity': globals().get('QB_NEW_ACTIVITY_COORDS', (100, 100)),
            'customer': globals().get('QB_CUSTOMER_COORDS', (600, 600)),
            'service_item': globals().get('QB_SERVICE_ITEM_COORDS', (200, 200)),
            'notes': globals().get('QB_NOTES_COORDS', (300, 300)),
            'duration': globals().get('QB_DURATION_COORDS', (400, 400)),
            'date': globals().get('QB_DATE_COORDS', (500, 500)),
            'saved_timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        try:
            # Create backup of existing file
            if os.path.exists(coord_file):
                try:
                    import shutil
                    shutil.copy2(coord_file, backup_file)
                    print(f"Backup created: {backup_file}")
                except Exception as backup_err:
                    print(f"Warning: Could not create backup: {backup_err}")
            
            # Save new coordinates
            with open(coord_file, 'w') as f:
                json.dump(coords, f, indent=2)
            
            print(f"Coordinates saved successfully to {coord_file}")
            
        except Exception as e:
            print(f"Error saving coordinates: {e}")
            try:
                # Fallback: save to backup location
                with open(backup_file, 'w') as f:
                    json.dump(coords, f, indent=2)
                print(f"Coordinates saved to backup file: {backup_file}")
            except Exception as backup_error:
                print(f"Failed to save coordinates to backup: {backup_error}")

    def set_qb_date_coord(self):
        """Enhanced date coordinate setting with exe compatibility"""
        try:
            # Ensure imports are available in exe environment
            import pyautogui
            import keyboard
            from tkinter import messagebox
            
            messagebox.showinfo("Set Date Coord", "Hover over the QuickBooks Date field and press Ctrl.", parent=self)
            
            try:
                keyboard.wait('ctrl')
                pos = pyautogui.position()
                globals()['QB_DATE_COORDS'] = pos
                self.save_coordinates()
                messagebox.showinfo("Date Coordinate Set", f"Date field coordinate set to {pos}.", parent=self)
                print(f"Date coordinate set to: {pos}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set date coordinate: {e}", parent=self)
                print(f"Error setting date coordinate: {e}")
                
        except ImportError as e:
            messagebox.showerror("Import Error", f"Required modules not available: {e}\nPlease ensure pyautogui and keyboard are installed.", parent=self)

    def show_help(self):
        messagebox.showinfo("Help", "Use F2 to run QB macro, F3 to set coordinates. Press Alt to cancel operations. Ensure coordinates are set correctly for automation.")
    
    def on_closing(self):
        """Handle app closing with auto-save"""
        try:
            print("Saving coordinates before closing...")
            self.save_coordinates()
            print("Coordinates saved successfully!")
        except Exception as e:
            print(f"Error saving coordinates on close: {e}")
        finally:
            self.destroy()
    
    def auto_save_timer(self):
        """Periodic auto-save timer"""
        try:
            # Save coordinates every 5 minutes (300000 ms)
            self.save_coordinates()
            print("Auto-save: Coordinates saved")
        except Exception as e:
            print(f"Auto-save error: {e}")
        finally:
            # Schedule next auto-save
            self.after(300000, self.auto_save_timer)  # 5 minutes

# Coordinate constants for QuickBooks automation
# User must adjust these coordinates based on their screen setup
QB_NEW_ACTIVITY_COORDS = (100, 100)  # Example coordinates for 'New Activity' button
QB_SERVICE_ITEM_COORDS = (200, 200)  # Example coordinates for 'Service Item' input field
QB_CUSTOMER_COORDS = (600, 600)
QB_NOTES_COORDS = (300, 300)  # Example coordinates for 'Notes' input field
QB_DURATION_COORDS = (400, 400)  # Example coordinates for 'Duration' input field, set default to (400, 400)
QB_DATE_COORDS = (500, 500)  # Example coordinates for 'Date' input field
QB_DATE_COORDS = (500, 500)  # Example coordinates for 'Date' input field

# Enhanced coordinate loading system with multiple fallbacks
def load_qb_coordinates():
    """Load QB coordinates with enhanced error handling and fallbacks"""
    coord_file = os.path.join(get_app_dir(), 'qb_coordinates.json')
    backup_file = os.path.join(get_app_dir(), 'qb_coordinates_backup.json')
    legacy_file = os.path.join(os.path.dirname(__file__), 'qb_coordinates.json')
    
    # Default coordinates
    default_coords = {
        'new_activity': (100, 100),
        'customer': (600, 600),
        'service_item': (200, 200),
        'notes': (300, 300),
        'duration': (400, 400),
        'date': (500, 500)
    }
    
    coords = None
    loaded_from = "defaults"
    
    # Try to load from primary file
    try:
        if os.path.exists(coord_file):
            with open(coord_file, 'r') as f:
                coords = json.load(f)
                loaded_from = coord_file
                print(f"Coordinates loaded from: {coord_file}")
    except Exception as e:
        print(f"Error loading from primary file: {e}")
    
    # Try backup file if primary failed
    if coords is None:
        try:
            if os.path.exists(backup_file):
                with open(backup_file, 'r') as f:
                    coords = json.load(f)
                    loaded_from = backup_file
                    print(f"Coordinates loaded from backup: {backup_file}")
        except Exception as e:
            print(f"Error loading from backup file: {e}")
    
    # Try legacy file location
    if coords is None:
        try:
            if os.path.exists(legacy_file):
                with open(legacy_file, 'r') as f:
                    coords = json.load(f)
                    loaded_from = legacy_file
                    print(f"Coordinates loaded from legacy location: {legacy_file}")
        except Exception as e:
            print(f"Error loading from legacy file: {e}")
    
    # Use defaults if all else fails
    if coords is None:
        coords = default_coords
        print("Using default coordinates")
    
    # Set global variables with validation
    try:
        globals()['QB_NEW_ACTIVITY_COORDS'] = tuple(coords.get('new_activity', default_coords['new_activity']))
        globals()['QB_CUSTOMER_COORDS'] = tuple(coords.get('customer', default_coords['customer']))
        globals()['QB_SERVICE_ITEM_COORDS'] = tuple(coords.get('service_item', default_coords['service_item']))
        globals()['QB_NOTES_COORDS'] = tuple(coords.get('notes', default_coords['notes']))
        globals()['QB_DURATION_COORDS'] = tuple(coords.get('duration', default_coords['duration']))
        globals()['QB_DATE_COORDS'] = tuple(coords.get('date', default_coords['date']))
        
        print(f"QB Coordinates loaded successfully from {loaded_from}")
        print(f"New Activity: {globals()['QB_NEW_ACTIVITY_COORDS']}")
        print(f"Customer: {globals()['QB_CUSTOMER_COORDS']}")
        print(f"Service Item: {globals()['QB_SERVICE_ITEM_COORDS']}")
        print(f"Notes: {globals()['QB_NOTES_COORDS']}")
        print(f"Duration: {globals()['QB_DURATION_COORDS']}")
        print(f"Date: {globals()['QB_DATE_COORDS']}")
        
    except Exception as e:
        print(f"Error setting coordinate globals: {e}")
        # Set defaults if there's any error
        globals()['QB_NEW_ACTIVITY_COORDS'] = default_coords['new_activity']
        globals()['QB_CUSTOMER_COORDS'] = default_coords['customer']
        globals()['QB_SERVICE_ITEM_COORDS'] = default_coords['service_item']
        globals()['QB_NOTES_COORDS'] = default_coords['notes']
        globals()['QB_DURATION_COORDS'] = default_coords['duration']
        globals()['QB_DATE_COORDS'] = default_coords['date']

# Load coordinates at startup
load_qb_coordinates()

class MacroTypeDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Mode")
        self.geometry("800x600")
        self.resizable(False, False)
        try:
            theme = parent.themes.get(parent.current_theme, parent.themes.get('dark', {})) if hasattr(parent, 'themes') else {}
            self.configure(fg_color=theme.get('surface', "#23272f"))
        except Exception:
            self.configure(fg_color="#23272f")
        self.grab_set()
        try:
            if hasattr(parent, '_popup_fade_in'):
                parent._popup_fade_in(self)
        except Exception:
            pass
        self.result = None
        self.mode_var = ctk.StringVar(value="Automatic")
        self.auto_frame = None
        self.manual_frame = None
        self.start_hour_var = ctk.StringVar(value="01")
        self.start_minute_var = ctk.StringVar(value="00")
        self.start_period_var = ctk.StringVar(value="AM")
        self.end_hour_var = ctk.StringVar(value="01")
        self.end_minute_var = ctk.StringVar(value="00")
        self.end_period_var = ctk.StringVar(value="AM")
        self.duration_label = None

        # Mode selection frame
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(mode_frame, text="Select Mode:").pack()
        rb_auto = ctk.CTkRadioButton(mode_frame, text="Automatic", variable=self.mode_var, value="Automatic", command=self.toggle_mode_fields)
        rb_auto.pack(anchor="w", pady=5)
        rb_manual = ctk.CTkRadioButton(mode_frame, text="Manual", variable=self.mode_var, value="Manual", command=self.toggle_mode_fields)
        rb_manual.pack(anchor="w", pady=5)

        # Check type selection frame (always shown)
        self.check_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.check_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.check_frame, text="Check Type:").pack()
        self.option_var = ctk.StringVar(value="Service Check")
        self.rb_service = ctk.CTkRadioButton(self.check_frame, text="Service Check", variable=self.option_var, value="Service Check")
        self.rb_service.pack(anchor="w", pady=5)
        self.rb_backup = ctk.CTkRadioButton(self.check_frame, text="Backup Check", variable=self.option_var, value="Backup Check")
        self.rb_backup.pack(anchor="w", pady=5)
        self.rb_onsite = ctk.CTkRadioButton(self.check_frame, text="On-Site Check", variable=self.option_var, value="On-Site Check")
        self.rb_onsite.pack(anchor="w", pady=5)
        self.rb_custom = ctk.CTkRadioButton(self.check_frame, text="Custom Check", variable=self.option_var, value="Custom Check")
        self.rb_custom.pack(anchor="w", pady=5)

        # Manual mode frame for time input (initially hidden)
        self.manual_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Start time
        start_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        start_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(start_frame, text="Start Time:").pack(side="left", padx=5)
        start_hour = ctk.CTkOptionMenu(start_frame, variable=self.start_hour_var, values=[f"{i:02d}" for i in range(1, 13)], width=60)
        start_hour.pack(side="left", padx=5)
        ctk.CTkLabel(start_frame, text=":").pack(side="left")
        self.start_minute_entry = ctk.CTkEntry(start_frame, width=60, textvariable=self.start_minute_var, font=("Segoe UI", 15))
        self.start_minute_entry.pack(side="left", padx=5)
        start_period = ctk.CTkOptionMenu(start_frame, variable=self.start_period_var, values=["AM", "PM"], width=60)
        start_period.pack(side="left", padx=5)
        # End time
        end_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        end_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(end_frame, text="End Time:").pack(side="left", padx=5)
        end_hour = ctk.CTkOptionMenu(end_frame, variable=self.end_hour_var, values=[f"{i:02d}" for i in range(1, 13)], width=60)
        end_hour.pack(side="left", padx=5)
        ctk.CTkLabel(end_frame, text=":").pack(side="left")
        self.end_minute_entry = ctk.CTkEntry(end_frame, width=60, textvariable=self.end_minute_var, font=("Segoe UI", 15))
        self.end_minute_entry.pack(side="left", padx=5)
        end_period = ctk.CTkOptionMenu(end_frame, variable=self.end_period_var, values=["AM", "PM"], width=60)
        end_period.pack(side="left", padx=5)
        # Date input
        date_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        date_frame.pack(pady=5, fill="x")
        ctk.CTkLabel(date_frame, text="Date (MM/DD/YYYY, optional):").pack(side="left", padx=5)
        self.date_var = ctk.StringVar()
        self.date_entry = ctk.CTkEntry(date_frame, width=150, textvariable=self.date_var, font=("Segoe UI", 15))
        self.date_entry.pack(side="left", padx=5)
        # Duration display
        self.duration_label = ctk.CTkLabel(self.manual_frame, text="Duration: To be calculated")
        self.duration_label.pack(pady=5)
        # Bind changes for real-time duration update
        self.start_minute_var.trace_add("write", self.update_duration)
        self.end_minute_var.trace_add("write", self.update_duration)
        self.start_hour_var.trace_add("write", self.update_duration)
        self.end_hour_var.trace_add("write", self.update_duration)
        self.start_period_var.trace_add("write", self.update_duration)
        self.end_period_var.trace_add("write", self.update_duration)

        # Initially set fields based on default mode
        self.toggle_mode_fields()

        self.ok_btn = ctk.CTkButton(self, text="OK", command=self.submit, height=40)
        self.ok_btn.pack(pady=10)
        self.bind("<Return>", lambda event: self.submit())
        self.bind("<Escape>", lambda event: self.cancel())
        self.after(100, lambda: self.focus_force())

    def toggle_mode_fields(self):
        if self.mode_var.get() == "Automatic":
            self.manual_frame.pack_forget()
        else:
            self.manual_frame.pack(pady=10, padx=20, fill="x")

    def update_duration(self, *args):
        try:
            start_hour = int(self.start_hour_var.get())
            start_minute = int(self.start_minute_var.get())
            start_period = self.start_period_var.get()
            end_hour = int(self.end_hour_var.get())
            end_minute = int(self.end_minute_var.get())
            end_period = self.end_period_var.get()
            # Convert to 24-hour for calculation
            if start_period == "PM" and start_hour != 12:
                start_hour += 12
            elif start_period == "AM" and start_hour == 12:
                start_hour = 0
            if end_period == "PM" and end_hour != 12:
                end_hour += 12
            elif end_period == "AM" and end_hour == 12:
                end_hour = 0
            start_total = start_hour * 60 + start_minute
            end_total = end_hour * 60 + end_minute
            if end_total > start_total:
                duration = end_total - start_total
                self.duration_label.configure(text=f"Duration: {duration} minutes")
            else:
                self.duration_label.configure(text="Duration: End must be after Start")
        except ValueError:
            self.duration_label.configure(text="Duration: Invalid time")

    def calculate_duration(self):
        try:
            start_hour = int(self.start_hour_var.get())
            start_minute = int(self.start_minute_var.get())
            start_period = self.start_period_var.get()
            end_hour = int(self.end_hour_var.get())
            end_minute = int(self.end_minute_var.get())
            end_period = self.end_period_var.get()
            # Convert to 24-hour for calculation
            if start_period == "PM" and start_hour != 12:
                start_hour += 12
            elif start_period == "AM" and start_hour == 12:
                start_hour = 0
            if end_period == "PM" and end_hour != 12:
                end_hour += 12
            elif end_period == "AM" and end_hour == 12:
                end_hour = 0
            start_total = start_hour * 60 + start_minute
            end_total = end_hour * 60 + end_minute
            if end_total > start_total:
                duration = end_total - start_total
                self.duration_label.configure(text=f"Duration: {duration} minutes")
                return duration
            else:
                self.duration_label.configure(text="Duration: End must be after Start")
                return None
        except ValueError:
            self.duration_label.configure(text="Duration: Invalid time")
            return None

    def submit(self):
        mode = self.mode_var.get()
        selected_type = self.option_var.get()
        if mode == "Manual":
            duration_minutes = self.calculate_duration()
            if duration_minutes is None:
                messagebox.showerror("Invalid Time", "End time must be after start time or times are invalid.", parent=self)
                return
            start_time_str = f"{self.start_hour_var.get()}:{self.start_minute_var.get()} {self.start_period_var.get()}"
            end_time_str = f"{self.end_hour_var.get()}:{self.end_minute_var.get()} {self.end_period_var.get()}"
            # Use the selected check type's message if available
            if selected_type == "Service Check":
                message = globals()['log_messages']['s']
            elif selected_type == "Backup Check":
                message = globals()['log_messages']['b']
            else:
                message = selected_type  # Fallback for On-Site or Custom, will be overridden if needed
            date_input = self.date_var.get().strip()
            log_date = None
            if date_input:
                try:
                    # Accept MM/DD/YYYY or M/D/YYYY
                    log_date = datetime.strptime(date_input, "%m/%d/%Y")
                except ValueError:
                    try:
                        log_date = datetime.strptime(date_input, "%m/%d/%y")
                    except ValueError:
                        messagebox.showerror("Invalid Date", "Please enter the date as MM/DD/YYYY or leave blank.", parent=self)
                        return
            else:
                log_date = datetime.now()
            date_str = format_date(log_date)
            self.result = {"mode": "manual", "start_time": start_time_str, "end_time": end_time_str, "duration": duration_minutes, "type": selected_type, "message": message, "date": date_str}
        else:
            self.result = {"mode": "automatic", "type": selected_type}
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

if __name__ == "__main__":
    app = LogCheckApp()
    app.mainloop()
