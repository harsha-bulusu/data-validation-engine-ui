import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import yaml
from TestCaseSuiteEditor import TestSuiteFormEditor

class TestCaseEditor:
    def __init__(self, root, tests_path):
        self.root = root
        self.tests_path = Path(tests_path)
        self.window = tk.Toplevel(self.root)
        self.window.title("Test Case Editor")
        self.window.geometry("1000x600")

        # Layout: left for file list, right for preview, bottom for buttons
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        self.selected_file = None

        # --- File List Panel ---
        left_frame = tk.Frame(self.window, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="ns")

        tk.Label(left_frame, text="Test Suites:").pack(anchor="w")
        self.file_listbox = tk.Listbox(left_frame, width=40)
        self.file_listbox.pack(fill="y", expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        # --- Preview Panel ---
        self.preview = tk.Text(self.window, bg="#f9f9f9", fg="#000000")
        self.preview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.preview.config(state="disabled")

        # --- Buttons ---
        button_frame = tk.Frame(self.window, pady=10)
        button_frame.grid(row=1, column=0, columnspan=2)

        tk.Button(button_frame, text="➕ Add New", command=self.add_suite).pack(side="left", padx=5)
        tk.Button(button_frame, text="✏️ Edit", command=self.edit_suite).pack(side="left", padx=5)
        tk.Button(button_frame, text="🗑️ Delete", command=self.delete_suite).pack(side="left", padx=5)

        self.load_file_list()

    def load_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in sorted(self.tests_path.glob("*.yml")):
            self.file_listbox.insert(tk.END, file.name)

    def on_file_select(self, event):
        if not self.file_listbox.curselection():
            return
        index = self.file_listbox.curselection()[0]
        filename = self.file_listbox.get(index)
        self.selected_file = self.tests_path / filename

        try:
            with open(self.selected_file, "r") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return

        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)

        summary = f"Test Suite Summary\n===================\n"
        summary += f"Suite Name   : {data.get('test_suite_name', '')}\n"
        summary += f"Tolerance    : {data.get('numeric_tolerance', '')}\n"
        summary += f"Test Cases   : {len(data.get('test_cases', []))}\n\n"

        for i, case in enumerate(data.get("test_cases", []), start=1):
            summary += f"Test Case {i}\n------------\n"
            for key, value in case.items():
                summary += f"{key:<15}: {value}\n"
            summary += "\n"

        self.preview.insert(tk.END, summary)
        self.preview.config(state="disabled")

    def add_suite(self):
        TestSuiteFormEditor(self.root, self.tests_path)
        self.window.after(500, self.load_file_list)

    def edit_suite(self):
        if not self.selected_file:
            messagebox.showwarning("No selection", "Select a suite to edit")
            return
        with open(self.selected_file) as f:
            existing_data = yaml.safe_load(f)

        TestSuiteFormEditor(self.root, on_save_callback=self.save_test_suite_callback, existing_data=existing_data)
        self.window.after(500, self.load_file_list)

    def delete_suite(self):
        if not self.selected_file:
            messagebox.showwarning("No selection", "Select a suite to delete")
            return
        confirm = messagebox.askyesno("Confirm", f"Delete {self.selected_file.name}?")
        if confirm:
            self.selected_file.unlink()
            self.selected_file = None
            self.load_file_list()
            self.preview.config(state="normal")
            self.preview.delete("1.0", tk.END)
            self.preview.config(state="disabled")

    def save_test_suite_callback(self, test_suite_data):
        # Save to the selected file (edit mode)
        if self.selected_file:
            with open(self.selected_file, "w") as f:
                yaml.dump(test_suite_data, f)
            messagebox.showinfo("Saved", f"{self.selected_file.name} updated.")
        else:
            # Handle add mode (optional)
            pass
