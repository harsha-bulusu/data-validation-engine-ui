from tkinter import Frame, Label, Entry, Button, Scrollbar, Text, StringVar, OptionMenu, filedialog, messagebox
from tkinter.ttk import Combobox
import tkinter as tk
import yaml

class TestSuiteFormEditor:
    def __init__(self, root, on_save_callback, existing_data=None):
        self.root = root
        self.on_save_callback = on_save_callback
        self.existing_data = existing_data or {}

        self.window = tk.Toplevel(self.root)
        self.window.title("Test Suite Form Editor")
        self.window.geometry("900x700")

        self.scroll_canvas = tk.Canvas(self.window)
        self.scroll_frame = Frame(self.scroll_canvas)
        self.scrollbar = Scrollbar(self.window, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scroll_window = self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')

        self.scroll_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Test Suite metadata
        Label(self.scroll_frame, text="Test Suite Name:").pack(anchor="w", padx=10)
        self.suite_name_var = StringVar(value=self.existing_data.get("test_suite_name", ""))
        Entry(self.scroll_frame, textvariable=self.suite_name_var, width=60).pack(padx=10, pady=2, anchor="w")

        Label(self.scroll_frame, text="Numeric Tolerance:").pack(anchor="w", padx=10)
        self.tolerance_var = StringVar(value=str(self.existing_data.get("numeric_tolerance", 0.05)))
        Entry(self.scroll_frame, textvariable=self.tolerance_var, width=20).pack(padx=10, pady=2, anchor="w")

        self.test_case_frames = []
        Button(self.scroll_frame, text="➕ Add Test Case", command=self.add_test_case).pack(pady=10)
        Button(self.scroll_frame, text="💾 Save Test Suite", command=self.save_test_suite).pack(pady=5)

        for case in self.existing_data.get("test_cases", []):
            self.add_test_case(prefill=case)

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_test_case(self, prefill=None):
        frame = Frame(self.scroll_frame, bd=1, relief="solid", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        case = {}

        Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
        name_var = StringVar(value=prefill.get("name") if prefill else "")
        Entry(frame, textvariable=name_var, width=50).grid(row=0, column=1, columnspan=3, sticky="w")

        Label(frame, text="Type:").grid(row=1, column=0, sticky="w")
        type_var = StringVar(value=prefill.get("type") if prefill else "")
        type_menu = OptionMenu(frame, type_var, "file_comparison", "api_comparison", command=lambda _: self.render_test_case_fields(case_frame, type_var.get(), case, prefill))
        type_menu.grid(row=1, column=1, sticky="w")

        case_frame = Frame(frame)
        case_frame.grid(row=2, column=0, columnspan=4, sticky="w")

        self.test_case_frames.append((name_var, type_var, case, case_frame))

        if prefill:
            self.render_test_case_fields(case_frame, type_var.get(), case, prefill)

    def render_test_case_fields(self, parent, test_type, case_dict, prefill=None):
        for widget in parent.winfo_children():
            widget.destroy()

        if test_type == "file_comparison":
            Label(parent, text="GCP File:").grid(row=0, column=0, sticky="w")
            case_dict["gcp_file"] = StringVar(value=prefill.get("gcp_file") if prefill else "")
            Entry(parent, textvariable=case_dict["gcp_file"], width=50).grid(row=0, column=1, sticky="w")

            Label(parent, text="Legacy File:").grid(row=1, column=0, sticky="w")
            case_dict["legacy_file"] = StringVar(value=prefill.get("legacy_file") if prefill else "")
            Entry(parent, textvariable=case_dict["legacy_file"], width=50).grid(row=1, column=1, sticky="w")

            Label(parent, text="Match Keys (comma separated):").grid(row=2, column=0, sticky="w")
            keys = ", ".join(prefill.get("match_keys", [])) if prefill else ""
            case_dict["match_keys"] = StringVar(value=keys)
            Entry(parent, textvariable=case_dict["match_keys"], width=50).grid(row=2, column=1, sticky="w")

        elif test_type == "api_comparison":
            Label(parent, text="Token Type:").grid(row=0, column=0, sticky="w")
            token_type = StringVar(value=prefill.get("token_type") if prefill else "user")
            case_dict["token_type"] = token_type

            def on_token_type_change(value):
                for w in parent.grid_slaves():
                    if int(w.grid_info()["row"]) > 0:
                        w.destroy()

                if value == "kong":
                    Label(parent, text="Client ID:").grid(row=1, column=0, sticky="w")
                    case_dict["client_id"] = StringVar(value=prefill.get("client_id") if prefill else "")
                    Entry(parent, textvariable=case_dict["client_id"], width=50).grid(row=1, column=1, sticky="w")

                    Label(parent, text="Client Secret:").grid(row=2, column=0, sticky="w")
                    case_dict["client_secret"] = StringVar(value=prefill.get("client_secret") if prefill else "")
                    Entry(parent, textvariable=case_dict["client_secret"], width=50).grid(row=2, column=1, sticky="w")
                else:
                    Label(parent, text="Base URL:").grid(row=1, column=0, sticky="w")
                    case_dict["base_url"] = StringVar(value=prefill.get("base_url") if prefill else "")
                    Entry(parent, textvariable=case_dict["base_url"], width=50).grid(row=1, column=1, sticky="w")

                Label(parent, text="Legacy URL:").grid(row=3, column=0, sticky="w")
                case_dict["legacy_url"] = StringVar(value=prefill.get("legacy_url") if prefill else "")
                Entry(parent, textvariable=case_dict["legacy_url"], width=50).grid(row=3, column=1, sticky="w")

                Label(parent, text="GCP URL:").grid(row=4, column=0, sticky="w")
                case_dict["gcp_url"] = StringVar(value=prefill.get("gcp_url") if prefill else "")
                Entry(parent, textvariable=case_dict["gcp_url"], width=50).grid(row=4, column=1, sticky="w")

                Label(parent, text="Params File:").grid(row=5, column=0, sticky="w")
                case_dict["params_file"] = StringVar(value=prefill.get("params_file") if prefill else "")
                Entry(parent, textvariable=case_dict["params_file"], width=50).grid(row=5, column=1, sticky="w")

            OptionMenu(parent, token_type, "user", "kong", command=on_token_type_change).grid(row=0, column=1, sticky="w")
            on_token_type_change(token_type.get())

    def save_test_suite(self):
        test_suite = {
            "test_suite_name": self.suite_name_var.get(),
            "numeric_tolerance": float(self.tolerance_var.get()),
            "test_cases": []
        }

        for name_var, type_var, case_dict, _ in self.test_case_frames:
            case = {
                "name": name_var.get(),
                "type": type_var.get()
            }
            for key, var in case_dict.items():
                if isinstance(var, StringVar):
                    val = var.get()
                    if val:
                        case[key] = val
                elif key == "match_keys":
                    case[key] = [k.strip() for k in var.get().split(",") if k.strip()]

            test_suite["test_cases"].append(case)

        self.on_save_callback(test_suite)
        self.window.destroy()