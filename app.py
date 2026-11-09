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

# Set global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class KeVanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KeVanObfuscate")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # Colors (Flat, No Gradient)
        self.bg_color = "#0a0f1a"
        self.panel_color = "#121a2a"
        self.text_color = "#ffffff"
        self.muted_text = "#6b7b93"
        self.primary = "#2962ff"
        self.success = "#00c853"
        self.error = "#d50000"

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
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.panel_color)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="K", font=("Segoe UI", 24, "bold"), text_color=self.primary, width=40, height=40, fg_color="#1a2b4c", corner_radius=8).place(x=20, y=30)
        ctk.CTkLabel(self.sidebar, text="KeVan", font=("Segoe UI", 18, "bold"), text_color=self.text_color).place(x=70, y=30)
        ctk.CTkLabel(self.sidebar, text="OBFUSCATE", font=("Segoe UI", 10), text_color=self.muted_text).place(x=70, y=55)

        ctk.CTkLabel(self.sidebar, text="WORKSPACE", font=("Segoe UI", 11, "bold"), text_color=self.muted_text).place(x=20, y=120)
        
        self.btn_obf = ctk.CTkButton(self.sidebar, text="Obfuscation", fg_color="#1e3a8a", text_color=self.text_color, hover=False, anchor="w", font=("Segoe UI", 13, "bold"), corner_radius=6)
        self.btn_obf.place(x=15, y=150, width=190, height=40)
        
        self.btn_rec = ctk.CTkButton(self.sidebar, text="Recent Activity", fg_color="transparent", text_color=self.muted_text, hover=False, anchor="w", font=("Segoe UI", 13), corner_radius=6, command=self.show_recent)
        self.btn_rec.place(x=15, y=200, width=190, height=40)

        ctk.CTkLabel(self.sidebar, text="SYSTEM READY", font=("Segoe UI", 10, "bold"), text_color=self.success).place(x=20, y=580)
        ctk.CTkLabel(self.sidebar, text="KeVan Engine Active.", font=("Segoe UI", 10), text_color=self.muted_text).place(x=20, y=600)

        # --- Main Content Area ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=30, pady=20)

        self.page_obf = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.page_rec = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self.setup_obf_page()
        self.setup_rec_page()
        self.show_obf()

    def setup_obf_page(self):
        ctk.CTkLabel(self.page_obf, text="KeVan Obfuscator", font=("Segoe UI", 28, "bold"), text_color=self.text_color).pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(self.page_obf, text="Secure your Java plugins with maximum protection while keeping full functionality.", font=("Segoe UI", 12), text_color=self.muted_text).pack(anchor="w", pady=(0, 20))

        content = ctk.CTkFrame(self.page_obf, fg_color="transparent")
        content.pack(fill="both", expand=True)

        # Left Panel
        left_panel = ctk.CTkFrame(content, fg_color=self.panel_color, corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(left_panel, text="Upload Project", font=("Segoe UI", 14, "bold"), text_color=self.text_color).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(left_panel, text="Select a compiled .jar file to begin.", font=("Segoe UI", 11), text_color=self.muted_text).pack(anchor="w", padx=20, pady=(0, 20))

        self.btn_upload = ctk.CTkButton(left_panel, text="Choose JAR File", font=("Segoe UI", 12, "bold"), fg_color="#1e3a8a", text_color="#ffffff", hover=False, height=40, corner_radius=8, command=self.upload_jar)
        self.btn_upload.pack(padx=20, pady=10, fill="x")

        self.lbl_file = ctk.CTkLabel(left_panel, text="No file selected", font=("Segoe UI", 11), text_color=self.muted_text)
        self.lbl_file.pack(pady=5)

        # Engine Selection
        ctk.CTkLabel(left_panel, text="Protection Engine", font=("Segoe UI", 12, "bold"), text_color=self.text_color).pack(anchor="w", padx=20, pady=(20, 5))
        self.combo_engine = ctk.CTkOptionMenu(left_panel, values=["ProGuard (Stable)", "Skidfuscator (Advanced)"], fg_color="#1e3a8a", button_color="#1e3a8a", button_hover_color="#1e3a8a", text_color="#ffffff", command=self.on_engine_change)
        self.combo_engine.pack(padx=20, fill="x")
        self.combo_engine.set("ProGuard (Stable)")

        # Output Folder
        self.btn_out = ctk.CTkButton(left_panel, text="Select Output Folder", font=("Segoe UI", 12), fg_color="transparent", border_width=1, border_color="#1e3a8a", text_color="#ffffff", hover=False, height=40, corner_radius=8, command=self.select_output)
        self.btn_out.pack(padx=20, pady=20, fill="x")

        # Start Button
        self.btn_start = ctk.CTkButton(left_panel, text="Start Obfuscation", font=("Segoe UI", 14, "bold"), fg_color="#2962ff", text_color="#ffffff", hover=False, height=50, corner_radius=8, command=self.start_obfuscate)
        self.btn_start.pack(padx=20, pady=(0, 20), fill="x")

        # Progress
        self.lbl_progress = ctk.CTkLabel(left_panel, text="Ready", font=("Segoe UI", 11, "bold"), text_color=self.primary)
        self.lbl_progress.pack(anchor="w", padx=20)
        
        self.prog_bar = ctk.CTkProgressBar(left_panel, progress_color=self.primary, fg_color="#0a0f1a")
        self.prog_bar.pack(padx=20, pady=(5, 20), fill="x")
        self.prog_bar.set(0)

        # Right Panel (Info)
        right_panel = ctk.CTkFrame(content, fg_color=self.panel_color, corner_radius=12, width=280)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="Safety First", font=("Segoe UI", 14, "bold"), text_color=self.text_color).pack(anchor="w", padx=20, pady=(20, 15))
        
        info_text = (
            "• Main Classes & Commands\n"
            "• @EventHandler Methods\n"
            "• Configuration Classes\n"
            "• Bukkit API Hooks\n"
            "• Enums & Interfaces\n\n"
            "These rules ensure your plugin runs perfectly on the server without errors."
        )
        ctk.CTkLabel(right_panel, text=info_text, font=("Segoe UI", 11), text_color=self.muted_text, justify="left", wraplength=240).pack(anchor="w", padx=20)

    def setup_rec_page(self):
        ctk.CTkLabel(self.page_rec, text="Recent Activity", font=("Segoe UI", 28, "bold"), text_color=self.text_color).pack(anchor="w", pady=(10, 20))
        self.rec_list = ctk.CTkScrollableFrame(self.page_rec, fg_color="transparent")
        self.rec_list.pack(fill="both", expand=True)

    def show_obf(self):
        self.page_rec.pack_forget()
        self.page_obf.pack(fill="both", expand=True)
        self.btn_obf.configure(fg_color="#1e3a8a", text_color=self.text_color)
        self.btn_rec.configure(fg_color="transparent", text_color=self.muted_text)

    def show_recent(self):
        self.page_obf.pack_forget()
        self.page_rec.pack(fill="both", expand=True)
        self.btn_obf.configure(fg_color="transparent", text_color=self.muted_text)
        self.btn_rec.configure(fg_color="#1e3a8a", text_color=self.text_color)
        self.render_recent()

    def on_engine_change(self, choice):
        self.engine = "ProGuard" if "ProGuard" in choice else "Skidfuscator"

    def check_java(self):
        try:
            subprocess.run(["java", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showwarning("Java Not Found", "Java (JRE) is not installed!\nPlease install Java 8 or higher to use this tool.")

    def upload_jar(self):
        path = filedialog.askopenfilename(filetypes=[("JAR files", "*.jar")])
        if path:
            self.jar_path = path
            self.lbl_file.configure(text=f"Selected: {os.path.basename(path)}", text_color=self.text_color)

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.btn_out.configure(text="Folder Selected", border_color=self.success)

    def start_obfuscate(self):
        if self.is_running: return
        if not self.jar_path:
            messagebox.showerror("Error", "Please upload a plugin JAR first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        
        self.is_running = True
        self.prog_bar.set(0)
        self.lbl_progress.configure(text="Preparing...", text_color=self.primary)
        threading.Thread(target=self.run_obfuscate, daemon=True).start()

    def random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def run_obfuscate(self):
        try:
            tmp = tempfile.mkdtemp(prefix="obf_")
            final = os.path.join(self.output_path, os.path.basename(self.jar_path).replace(".jar", "-obf.jar"))

            if self.engine == "ProGuard":
                unpack = os.path.join(tmp, "unpacked")
                os.makedirs(unpack, exist_ok=True)

                self.update_progress("Extracting plugin...", 0.1)
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
                
                if not main_package:
                    main_package = "obf"

                self.update_progress("Generating random names...", 0.2)
                dict_path = os.path.join(tmp, "dict.txt")
                with open(dict_path, "w") as f:
                    for _ in range(2000):
                        f.write(self.random_name() + "\n")

                self.update_progress("Building strict rules...", 0.3)
                
                # STRICT KEEP RULES FOR BUKKIT
                keep_rules = [
                    "-keepattributes *Annotation*,Signature,Exceptions,InnerClasses,MethodParameters,SourceFile,LineNumberTable",
                    "-keep public class * extends org.bukkit.plugin.java.JavaPlugin { *; }",
                    "-keep class * implements org.bukkit.event.Listener { *; }",
                    "-keepclassmembers class * { @org.bukkit.event.EventHandler <methods>; }",
                    "-keepclassmembers class * { @org.bukkit.command.CommandExecutor <methods>; }",
                    "-keepclassmembers class * { @org.bukkit.command.TabCompleter <methods>; }",
                    "-keep class * implements org.bukkit.configuration.serialization.ConfigurationSerializable { *; }",
                    "-keep class * extends org.bukkit.plugin.ServiceProvider { *; }",
                    "-keep enum * { *; }",
                    "-keep interface * { *; }",
                    "-keep class org.bukkit.** { *; }",
                    "-keep class net.minecraft.** { *; }",
                    "-keep class com.destroystokyo.** { *; }",
                    "-dontwarn **",
                    "-adaptclassstrings",
                    "-adaptresourcefilecontents **.yml,**.txt,**.properties,**.json",
                    "-overloadaggressively",
                    "-allowaccessmodification",
                    f"-keeppackagenames {main_class_full.rsplit('.', 1)[0]}",
                    f"-obfuscationdictionary {dict_path}"
                ]
                
                if main_class:
                    keep_rules.append(f"-keep public class {main_class} {{ *; }}")
                    
                pro_file = os.path.join(tmp, "keep.pro")
                with open(pro_file, "w") as f:
                    f.write("\n".join(keep_rules))

                self.update_progress("Obfuscating classes...", 0.5)
                proguard_jar = self.find_tool("proguard.jar")
                if not proguard_jar:
                    raise RuntimeError("ProGuard jar not found! Place 'proguard.jar' next to the app.")

                libs_dir = os.path.join(tmp, "libs")
                os.makedirs(libs_dir, exist_ok=True)
                obf_out = os.path.join(tmp, "obf.jar")

                cmd = ["java", "-jar", proguard_jar, "-injars", self.jar_path, "-outjars", obf_out, "-libraryjars", libs_dir, "-include", pro_file, "-dontoptimize", "-dontshrink"]
                self.run_java(cmd)

                self.update_progress("Injecting 5000+ dummy files...", 0.7)
                with zipfile.ZipFile(obf_out, 'r') as zin:
                    with zipfile.ZipFile(final, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
                        for item in zin.infolist():
                            zout.writestr(item, zin.read(item.filename))
                        
                        dummy_bytecode = b'\xca\xfe\xba\xbe\x00\x00\x00\x34\x00\x01\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        for i in range(5000):
                            dummy_name = f"{main_package}/{self.random_name()}.class"
                            zout.writestr(dummy_name, dummy_bytecode)
                            
                            if i % 500 == 0:
                                self.update_progress(f"Injecting noise... ({i}/5000)", 0.7 + ((i/5000)*0.2))

            else:
                self.update_progress("Running Skidfuscator...", 0.5)
                skid_jar = self.find_tool("skidfuscator.jar")
                if not skid_jar:
                    raise RuntimeError("Skidfuscator jar not found! Place 'skidfuscator.jar' next to the app.")
                
                libs_dir = os.path.join(tmp, "libs")
                os.makedirs(libs_dir, exist_ok=True)
                
                cmd = ["java", "-jar", skid_jar, "obfuscate", self.jar_path, f"--output={final}", "--phantom", "--notrack"]
                self.run_java(cmd)
                
                if not os.path.exists(final):
                    raise RuntimeError("Skidfuscator did not produce an output file.")

            self.update_progress("Done!", 1.0)
            self.jobs.append({"name": os.path.basename(self.jar_path), "output": final, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            messagebox.showinfo("Success", f"Obfuscation Complete!\nSaved to:\n{final}")

        except Exception as e:
            self.lbl_progress.configure(text="Error!", text_color=self.error)
            messagebox.showerror("Obfuscation failed", str(e))
        finally:
            self.is_running = False

    def run_java(self, cmd):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, check=True, startupinfo=startupinfo)

    def update_progress(self, msg, val):
        self.lbl_progress.configure(text=msg)
        self.prog_bar.set(val)
        self.update_idletasks()

    def find_tool(self, tool_name):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(base, tool_name)
        return p if os.path.exists(p) else None

    def render_recent(self):
        for w in self.rec_list.winfo_children():
            w.destroy()
        if not self.jobs:
            ctk.CTkLabel(self.rec_list, text="No recent sessions.", font=("Segoe UI", 12), text_color=self.muted_text).pack(pady=40)
            return
        for job in reversed(self.jobs):
            f = ctk.CTkFrame(self.rec_list, fg_color=self.panel_color, corner_radius=8)
            f.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(f, text=job["name"], font=("Segoe UI", 12, "bold"), text_color=self.text_color).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(f, text=f"Saved: {job['output']} | {job['date']}", font=("Segoe UI", 10), text_color=self.muted_text).pack(anchor="w", padx=15, pady=(0, 10))

if __name__ == "__main__":
    app = KeVanApp()
    app.mainloop()
