from pathlib import Path
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import yaml

import TestCaseEditor
import main

# ---- Constants ----
FOLDERS = ["Output", "Payloads", "Templates", "Data", "tests"]
INIT_FILE = ".workspace_init"
CONFIG_FILE = "workspace_config.yaml"
THEME_BG = "#1e1e1e"  # IntelliJ-style dark background
THEME_FG = "#ffffff"  # White text
BUTTON_BG = "#4b6eaf"  # Brighter blue button background
BUTTON_FG = "#4b6eaf"  # White text
BUTTON_ACTIVE_BG = "#3d5a99"  # Slightly darker for active
FONT = ("Segoe UI", 11)

# ---- Helpers ----
def initialize_workspace(path):
    for folder in FOLDERS:
        Path(path, folder).mkdir(parents=True, exist_ok=True)

    # Simulate downloading Swagger templates
    template_path = Path(path, "Templates", "sample_template.yaml")
    if not template_path.exists():
        with open(template_path, "w") as f:
            f.write("""query_params:
  vbu_number: <Number of VBU>
  start_date: <Start date YYYY-MM-DD>
  end_date: <End date YYYY-MM-DD>
body:
  region_id: <Region Identifier>
  include_metrics: <Boolean>
""")

    # Create init file
    Path(path, INIT_FILE).touch()

def save_credentials(project_root, username, password):
    config = {
        "username": username,
        "password": password
    }
    with open(Path(project_root) / CONFIG_FILE, "w") as f:
        yaml.dump(config, f)
    messagebox.showinfo("Saved", "Credentials saved to workspace_config.yaml")

# ---- GUI App ----
class TestManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Manager")
        self.root.configure(bg=THEME_BG)
        self.project_root = None

        self.load_or_select_workspace()
        self.create_main_menu()

    def load_or_select_workspace(self):
        selected = filedialog.askdirectory(title="Select Target Project Folder")
        if not selected:
            messagebox.showerror("Required", "Project folder must be selected.")
            self.root.quit()
            return

        self.project_root = Path(selected)

        # Check if already initialized
        if not Path(self.project_root, INIT_FILE).exists():
            initialize_workspace(self.project_root)

        # Ask for credentials if not saved
        config_path = Path(self.project_root, CONFIG_FILE)
        if not config_path.exists():
            username = simpledialog.askstring("Credentials", "Enter username:")
            password = simpledialog.askstring("Credentials", "Enter password:", show="*")
            save_credentials(self.project_root, username, password)

    def create_main_menu(self):
        frm = tk.Frame(self.root, padx=20, pady=20, bg=THEME_BG)
        frm.pack(fill="both", expand=True)

        tk.Label(
            frm, text=f"Workspace: {self.project_root}", fg=THEME_FG, bg=THEME_BG, font=("Segoe UI", 10, "italic")
        ).pack(pady=(0, 20))

        for text, cmd in [
            ("➕  Create Payload", self.handle_payload),
            ("🧾  Add/Edit Test Cases", self.handle_test_cases),
            ("▶️  Run Tests", self.run_tests),
        ]:
            tk.Button(
                frm, text=text, width=30, height=2, font=FONT,
                bg=BUTTON_BG, fg=BUTTON_FG, activebackground=BUTTON_ACTIVE_BG,
                command=cmd, relief="flat", bd=1, cursor="hand2"
            ).pack(pady=10)

    def handle_payload(self):
        messagebox.showinfo("Coming Soon", "Payload creator form will go here.")

    def handle_test_cases(self):
        TestCaseEditor.TestCaseEditor(self.root, self.project_root / "tests")

    def run_tests(self):
        main.main()

# ---- Run the App ----
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("420x420")
    app = TestManagerApp(root)
    root.mainloop()