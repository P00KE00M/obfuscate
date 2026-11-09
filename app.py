import os
import sys
import shutil
import tempfile
import subprocess
import zipfile
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import datetime
import random
import string
import time

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class KeVanApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KeVanObfuscate")
        self.geometry("1100x750")
        self.minsize(900, 650)
        
        # Flat Red Theme
        self.bg_color = "#0a0a0a"
        self.panel_color = "#141414"
        self.text_color = "#ffffff"
        self.muted_text = "#888888"
        self.primary_red = "#d32f2f"
        self.success_green = "#2e7d32"
        self.console_bg = "#000000"

        self.configure(fg_color=self.bg_color)
        self.jar_path = None
        self.output_path = None
        self.jobs = []
        self.engine = "ProGuard"
        self.is_running = False

        self.setup_ui()
        self.check_java()

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.panel_color)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        side_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        side_content.pack(fill="both", expand=True, padx=20, pady=30)

        logo_frame = ctk.CTkFrame(side_content, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 40))
        
        ctk.CTkLabel(logo_frame, text="K", font=("Segoe UI", 24, "bold"), text_color="#ffffff", width=40, height=40, fg_color=self.primary_red, corner_radius=8).pack(side="left")
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=10)
        ctk.CTkLabel(title_frame, text="KeVan", font=("Segoe UI", 20, "bold"), text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="OBFUSCATE", font=("Segoe UI", 10, "bold"), text_color=self.muted_text).pack(anchor="w")

        ctk.CTkLabel(side_content, text="MENU", font=("Segoe UI", 11, "bold"), text_color=self.muted_text).pack(anchor="w", pady=(0, 10))
        
        self.btn_obf = ctk.CTkButton(side_content, text="  Obfuscation", fg_color=self.primary_red, text_color=self.text_color, hover=False, anchor="w", font=("Segoe UI", 14, "bold"), corner_radius=6, height=45, command=self.show_obf)
        self.btn_obf.pack(fill="x", pady=5)
        
        self.btn_rec = ctk.CTkButton(side_content, text="  Recent Activity", fg_color="transparent", text_color=self.muted_text, hover=False, anchor="w", font=("Segoe UI", 14), corner_radius=6, height=45, command=self.show_recent)
        self.btn_rec.pack(fill="x", pady=5)

        status_frame = ctk.CTkFrame(side_content, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", pady=20)
        ctk.CTkLabel(status_frame, text="● SYSTEM READY", font=("Segoe UI", 11, "bold"), text_color=self.success_green).pack(anchor="w")
        ctk.CTkLabel(status_frame, text="KeVan Engine Active.", font=("Segoe UI", 10), text_color=self.muted_text).pack(anchor="w")

        # --- Main Content Area ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=30, pady=20)

        self.page_obf = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.page_rec = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self.setup_obf_page()
        self.setup_rec_page()
        self.show_obf()

    def setup_obf_page(self):
        header_frame = ctk.CTkFrame(self.page_obf, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Obfuscation Workspace", font=("Segoe UI", 28, "bold"), text_color=self.text_color).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Secure your Java plugins while keeping full functionality.", font=("Segoe UI", 13), text_color=self.muted_text).pack(anchor="w")

        content = ctk.CTkFrame(self.page_obf, fg_color="transparent")
        content.pack(fill="both", expand=True)

        # Left Panel
        left_panel = ctk.CTkFrame(content, fg_color=self.panel_color, corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(left_panel, text="1. Upload Project", font=("Segoe UI", 15, "bold"), text_color=self.text_color).pack(anchor="w", padx=25, pady=(25, 10))
        self.btn_upload = ctk.CTkButton(left_panel, text="Choose JAR File", font=("Segoe UI", 13, "bold"), fg_color=self.primary_red, hover=False, height=40, corner_radius=6, command=self.upload_jar)
        self.btn_upload.pack(padx=25, pady=5, fill="x")
        self.lbl_file = ctk.CTkLabel(left_panel, text="No file selected", font=("Segoe UI", 12), text_color=self.muted_text)
        self.lbl_file.pack(pady=(5, 20))

        ctk.CTkLabel(left_panel, text="2. Protection Engine", font=("Segoe UI", 15, "bold"), text_color=self.text_color).pack(anchor="w", padx=25, pady=(10, 10))
        self.combo_engine = ctk.CTkOptionMenu(left_panel, values=["ProGuard (Safe & Stable)", "Skidfuscator (Advanced)"], fg_color=self.primary_red, button_color=self.primary_red, button_hover_color=self.primary_red, text_color="#ffffff", font=("Segoe UI", 13), dropdown_font=("Segoe UI", 12), height=40, corner_radius=6, command=self.on_engine_change)
        self.combo_engine.pack(padx=25, fill="x")
        self.combo_engine.set("ProGuard (Safe & Stable)")

        ctk.CTkLabel(left_panel, text="3. Output Destination", font=("Segoe UI", 15, "bold"), text_color=self.text_color).pack(anchor="w", padx=25, pady=(25, 10))
        self.btn_out = ctk.CTkButton(left_panel, text="Select Output Folder", font=("Segoe UI", 13), fg_color="transparent", border_width=1, border_color=self.primary_red, text_color="#ffffff", hover=False, height=40, corner_radius=6, command=self.select_output)
        self.btn_out.pack(padx=25, pady=(0, 30), fill="x")

        self.btn_start = ctk.CTkButton(left_panel, text="START OBFUSCATION", font=("Segoe UI", 16, "bold"), fg_color=self.primary_red, text_color="#ffffff", hover=False, height=55, corner_radius=8, command=self.start_obfuscate)
        self.btn_start.pack(padx=25, pady=(10, 30), fill="x")

        # Right Panel
        right_panel = ctk.CTkFrame(content, fg_color=self.panel_color, corner_radius=10, width=450)
        right_panel.pack(side="right", fill="both", expand=True, padx=(15, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="Process Monitor", font=("Segoe UI", 15, "bold"), text_color=self.text_color).pack(anchor="w", padx=25, pady=(25, 15))

        # Progress Bar
        self.prog_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.prog_frame.pack(fill="x", padx=25, pady=10)
        
        self.lbl_percent = ctk.CTkLabel(self.prog_frame, text="0%", font=("Segoe UI", 14, "bold"), text_color=self.primary_red)
        self.lbl_percent.pack(side="right")
        self.lbl_prog_status = ctk.CTkLabel(self.prog_frame, text="Waiting for input...", font=("Segoe UI", 13), text_color=self.muted_text)
        self.lbl_prog_status.pack(side="left")

        self.prog_bar = ctk.CTkProgressBar(right_panel, progress_color=self.primary_red, fg_color="#000000", height=12, corner_radius=6)
        self.prog_bar.pack(fill="x", padx=25, pady=(5, 20))
        self.prog_bar.set(0)

        # Console
        ctk.CTkLabel(right_panel, text="Console Output", font=("Segoe UI", 13, "bold"), text_color=self.muted_text).pack(anchor="w", padx=25)
        self.console = ctk.CTkTextbox(right_panel, fg_color=self.console_bg, text_color="#00ff00", font=("Consolas", 12), corner_radius=6, activate_scrollbars=True)
        self.console.pack(fill="both", expand=True, padx=25, pady=(5, 25))
        self.console.insert("0.0", "KeVanObfuscate Initialized.\nSafe Mode Active.\n")
        self.console.configure(state="disabled")

    def setup_rec_page(self):
        header_frame = ctk.CTkFrame(self.page_rec, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Recent Activity", font=("Segoe UI", 28, "bold"), text_color=self.text_color).pack(anchor="w")
        
        self.rec_list = ctk.CTkScrollableFrame(self.page_rec, fg_color="transparent")
        self.rec_list.pack(fill="both", expand=True)

    def show_obf(self):
        self.page_rec.pack_forget()
        self.page_obf.pack(fill="both", expand=True)
        self.btn_obf.configure(fg_color=self.primary_red, text_color=self.text_color)
        self.btn_rec.configure(fg_color="transparent", text_color=self.muted_text)

    def show_recent(self):
        self.page_obf.pack_forget()
        self.page_rec.pack(fill="both", expand=True)
        self.btn_obf.configure(fg_color="transparent", text_color=self.muted_text)
        self.btn_rec.configure(fg_color=self.primary_red, text_color=self.text_color)
        self.render_recent()

    def log_console(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def on_engine_change(self, choice):
        self.engine = "ProGuard" if "ProGuard" in choice else "Skidfuscator"
        self.log_console(f"Engine switched to {self.engine}")

    def check_java(self):
        try:
            subprocess.run(["java", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log_console("Java environment detected.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_console("ERROR: Java not found. Please install Java 8+.")
            messagebox.showwarning("Java Not Found", "Java (JRE) is not installed!\nPlease install Java 8 or higher.")

    def upload_jar(self):
        path = filedialog.askopenfilename(filetypes=[("JAR files", "*.jar")])
        if path:
            self.jar_path = path
            self.lbl_file.configure(text=f"{os.path.basename(path)}", text_color=self.text_color)
            self.log_console(f"File loaded: {os.path.basename(path)}")

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.btn_out.configure(text="Folder Selected", border_color=self.success_green)
            self.log_console(f"Output directory set.")

    def start_obfuscate(self):
        if self.is_running: return
        if not self.jar_path:
            messagebox.showerror("Error", "Please upload a plugin JAR first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        
        self.is_running = True
        self.btn_start.configure(state="disabled", fg_color="#555555")
        self.prog_bar.set(0)
        self.lbl_percent.configure(text="0%")
        self.log_console("Starting obfuscation process...")
        threading.Thread(target=self.run_obfuscate, daemon=True).start()

    def random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def update_progress(self, msg, percent, delay=0.1):
        self.lbl_prog_status.configure(text=msg)
        self.lbl_percent.configure(text=f"{percent}%")
        self.prog_bar.set(percent / 100)
        self.log_console(msg)
        self.update_idletasks()
        time.sleep(delay)

    def run_obfuscate(self):
        try:
            tmp = tempfile.mkdtemp(prefix="obf_")
            final = os.path.join(self.output_path, os.path.basename(self.jar_path).replace(".jar", "-obf.jar"))

            if self.engine == "ProGuard":
                self.update_progress("Extracting plugin...", 10)
                unpack = os.path.join(tmp, "unpacked")
                os.makedirs(unpack, exist_ok=True)
                with zipfile.ZipFile(self.jar_path, "r") as z:
                    z.extractall(unpack)

                plugin_yml = os.path.join(unpack, "plugin.yml")
                main_class = None
                main_package = ""
                
                if os.path.exists(plugin_yml):
                    with open(plugin_yml, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip().startswith("main:"):
                                main_class_full = line.split(":", 1)[1].strip()
                                main_class = main_class_full
                                if "." in main_class_full:
                                    main_package = "/".join(main_class_full.split(".")[:-1])
                                break
                
                self.update_progress("Generating random names...", 30)
                dict_path = os.path.join(tmp, "dict.txt")
                with open(dict_path, "w") as f:
                    for _ in range(1000):
                        f.write(self.random_name() + "\n")

                self.update_progress("Building strict safe rules...", 50)
                
                # EXTREMELY STRICT KEEP RULES FOR SERVER COMPATIBILITY
                keep_rules = [
                    "-keepattributes *Annotation*,Signature,Exceptions,InnerClasses,MethodParameters,SourceFile,LineNumberTable",
                    
                    # Keep all Bukkit/Spigot core
                    "-keep class org.bukkit.** { *; }",
                    "-keep class net.minecraft.** { *; }",
                    "-keep class com.destroystokyo.** { *; }",
                    "-keep class io.papermc.** { *; }",
                    
                    # Keep Main Class and all its members
                    f"-keep public class {main_class} {{ *; }}" if main_class else "",
                    
                    # Keep Event Listeners, Commands, Config
                    "-keep public class * extends org.bukkit.plugin.java.JavaPlugin { *; }",
                    "-keep class * implements org.bukkit.event.Listener { *; }",
                    "-keepclassmembers class * { @org.bukkit.event.EventHandler <methods>; }",
                    "-keepclassmembers class * { @org.bukkit.command.CommandExecutor <methods>; }",
                    "-keepclassmembers class * { @org.bukkit.command.TabCompleter <methods>; }",
                    "-keep class * implements org.bukkit.configuration.serialization.ConfigurationSerializable { *; }",
                    
                    # Keep Enums & Interfaces
                    "-keep enum * { *; }",
                    "-keep interface * { *; }",
                    
                    # Keep other essential stuff
                    "-dontwarn **",
                    "-dontshrink", # DO NOT SHRINK! Prevents deleting essential code.
                    "-dontoptimize", # DO NOT OPTIMIZE! Prevents breaking flow.
                    "-adaptclassstrings",
                    "-adaptresourcefilecontents **.yml,**.txt,**.properties,**.json",
                    "-overloadaggressively",
                    "-allowaccessmodification",
                    f"-obfuscationdictionary {dict_path}"
                ]
                
                pro_file = os.path.join(tmp, "keep.pro")
                with open(pro_file, "w") as f:
                    f.write("\n".join(filter(None, keep_rules)))

                self.update_progress("Running ProGuard engine...", 70, 0.5)
                proguard_jar = self.find_tool("proguard.jar")
                if not proguard_jar:
                    raise RuntimeError("ProGuard jar not found!")

                libs_dir = os.path.join(tmp, "libs")
                os.makedirs(libs_dir, exist_ok=True)

                cmd = ["java", "-jar", proguard_jar, "-injars", self.jar_path, "-outjars", final, "-libraryjars", libs_dir, "-include", pro_file]
                self.run_java(cmd)

            else:
                self.update_progress("Running Skidfuscator...", 50, 0.5)
                skid_jar = self.find_tool("skidfuscator.jar")
                if not skid_jar:
                    raise RuntimeError("Skidfuscator jar not found!")
                
                cmd = ["java", "-jar", skid_jar, "obfuscate", self.jar_path, f"--output={final}", "--phantom", "--notrack"]
                self.run_java(cmd)

            self.update_progress("Completed Successfully!", 100, 0.5)
            self.jobs.append({"name": os.path.basename(self.jar_path), "output": final, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            
            self.after(0, lambda: messagebox.showinfo("Success", f"Obfuscation Complete!\n\nSaved to:\n{final}\n\nNote: If using Paper, add -Dpaper.disablePluginRemapping=true to your server startup flags."))
            
        except Exception as e:
            self.lbl_prog_status.configure(text="Error occurred!", text_color=self.primary_red)
            self.log_console(f"FATAL ERROR: {str(e)}")
            self.after(0, lambda: messagebox.showerror("Obfuscation failed", str(e)))
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_start.configure(state="normal", fg_color=self.primary_red))

    def run_java(self, cmd):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo)

    def find_tool(self, tool_name):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(base, tool_name)
        return p if os.path.exists(p) else None

    def render_recent(self):
        for w in self.rec_list.winfo_children():
            w.destroy()
        if not self.jobs:
            ctk.CTkLabel(self.rec_list, text="No recent sessions found.", font=("Segoe UI", 12), text_color=self.muted_text).pack(pady=40)
            return
        for job in reversed(self.jobs):
            f = ctk.CTkFrame(self.rec_list, fg_color=self.panel_color, corner_radius=8)
            f.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(f, text=job["name"], font=("Segoe UI", 13, "bold"), text_color=self.text_color).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(f, text=f"Saved: {job['output']} | {job['date']}", font=("Segoe UI", 11), text_color=self.muted_text).pack(anchor="w", padx=15, pady=(0, 10))

if __name__ == "__main__":
    app = KeVanApp()
    app.mainloop()
