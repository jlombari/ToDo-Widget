'''
SUMMARY OF SOFTWARE
- - - - - - - - - - - - - -
Version 0.1.3 (Pre-Release)
 - - - - - - - - - - - - - -
A TO-DO desktop widget with
persistent storage and a
priority system. Similar to
Todoist or Trello.

By Jerremy Lombari
'''
import customtkinter as ctk
import json
import os
import sys
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))


SAVE_FILE = os.path.join(APP_DIR, "tasks.json")
SETTINGS_FILE = os.path.join(APP_DIR, "userPref.json")

User_ThemePref = "Dark"

PRIORITY_ORDER = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3
}

def priority_color(priority):
    colors = {
        "Critical": "#ff0000",
        "High": "#ff6b6b",
        "Medium": "#fb7f2f",
        "Low": "#59d98e"
    }
    return colors.get(priority, "white")

class TodoWidget(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TODOs")
        self.geometry("400x700")
        self.topbar = ctk.CTkFrame(self, height=40)
        self.topbar.pack(fill="x")
        self.attributes("-topmost", True)
        self.todo_items = []
        self.completed_items = []
        self.build_ui()
        self.load_tasks()
        self.load_preferences()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()

        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☀")
            self.User_ThemePref = ctk.get_appearance_mode()
            self.update_preference()
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌙")
            self.User_ThemePref = ctk.get_appearance_mode()
            self.update_preference()

    
    def build_ui(self):
        title = ctk.CTkLabel(
            self.topbar,
            text="TO-DO WIDGET",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(side="left", padx=10)
        self.theme_btn = ctk.CTkButton(
            self.topbar,
            width=40,
            text="🌙",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right", padx=10)
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10)
        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Add a new task..."
        )
        self.task_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
            pady=5
        )
        self.task_entry.bind("<Return>", self.add_task)
        self.priority_var = ctk.StringVar(value="Medium")
        priority_menu = ctk.CTkOptionMenu(
            input_frame,
            variable=self.priority_var,
            values=[
                "Critical",
                "High",
                "Medium",
                "Low"
            ]
        )
        priority_menu.pack(
            side="left",
            padx=5
        )
        add_btn = ctk.CTkButton(
            input_frame,
            text="+",
            width=45,
            command=self.add_task
        )
        add_btn.pack(
            side="right",
            padx=5,
            pady=5
        )
        self.todo_label = ctk.CTkLabel(
            self,
            text="Active Tasks",
            anchor="w",
            font=("Segoe UI", 15, "bold")
        )
        self.todo_label.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )
        self.todo_frame = ctk.CTkScrollableFrame(self)
        self.todo_frame.pack(
            fill="both",
            expand=True,
            padx=10
        )
        self.done_header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.done_header.pack(fill="x", padx=10, pady=(10, 5))
        self.done_label = ctk.CTkLabel(
            self.done_header,
            text="Completed Tasks",
            font=("Segoe UI", 15, "bold")
        )
        self.done_label.pack(side="left")
        self.clear_button = ctk.CTkButton(
            self.done_header,
            text="Clear",
            width=80,
            command=self.clear_completed_tasks
        )
        self.clear_button.pack(side="right")
        self.done_frame = ctk.CTkScrollableFrame(
            self,
            height=180
        )
        self.done_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

    def add_task(self, event=None):
        text = self.task_entry.get().strip()
        if not text:
            return
        task = {
            "text": text,
            "priority": self.priority_var.get(),
            "created": datetime.now().isoformat()
        }
        self.todo_items.append(task)
        self.task_entry.delete(0, "end")
        self.sort_tasks()
        self.save_tasks()

    def save_tasks(self):
        data = {
            "todo": self.todo_items,
            "completed": self.completed_items
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4
            )

    def update_preference(self):
        data = {
            "appearance_mode": self.User_ThemePref
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4
            )

    def load_preferences(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            theme = data.get("appearance_mode", "Dark")
            ctk.set_appearance_mode(theme)
            self.User_themePref = theme

    def clear_completed_tasks(self):
        self.completed_items = []
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "todo": self.todo_items,
                    "completed": self.completed_items
                },
                f,
                indent=4
            )
        self.refresh_completed_display()
    
    def load_tasks(self):
        if not os.path.exists(SAVE_FILE):
            return
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.todo_items = data.get("todo", [])
        self.completed_items = data.get("completed", [])
        self.sort_tasks()
        self.refresh_completed_display()

    def sort_tasks(self):
        self.todo_items.sort(
            key=lambda task: (
                PRIORITY_ORDER.get(task["priority"], 999),
                task["created"]
            )
        )
        self.refresh_todo_display()

    def refresh_todo_display(self):
        for widget in self.todo_frame.winfo_children():
            widget.destroy()
        for task in self.todo_items:
            self.create_todo_widget(task)

    def refresh_completed_display(self):
        for widget in self.done_frame.winfo_children():
            widget.destroy()
        for task in reversed(self.completed_items):
            self.create_completed_widget(task)

    def create_todo_widget(self, task):
        row = ctk.CTkFrame(self.todo_frame)
        row.pack(
            fill="x",
            padx=3,
            pady=2
        )
        checkbox = ctk.CTkCheckBox(
            row,
            text=task["text"],
            command=lambda:
            self.complete_task(task)
        )
        checkbox.pack(
            side="left",
            padx=10,
            pady=8
        )
        badge = ctk.CTkLabel(
            row,
            text=task["priority"],
            text_color=priority_color(task["priority"])
        )
        badge.pack(
            side="right",
            padx=10
        )

    def create_completed_widget(self, task):
        row = ctk.CTkFrame(self.done_frame)
        row.pack(
            fill="x",
            padx=3,
            pady=2
        )
        label = ctk.CTkLabel(
            row,
            text=f"✓ {task['text']}",
            text_color="gray"
        )
        label.pack(
            side="left",
            padx=10,
            pady=8
        )
        badge = ctk.CTkLabel(
            row,
            text=task["priority"],
            text_color=priority_color(task["priority"])
        )
        badge.pack(
            side="right",
            padx=10
        )

    def complete_task(self, task):
        if task in self.todo_items:
            self.todo_items.remove(task)
        self.completed_items.append(task)
        self.sort_tasks()
        self.refresh_completed_display()
        self.save_tasks()

if __name__ == "__main__":
    app = TodoWidget()
    app.mainloop()
