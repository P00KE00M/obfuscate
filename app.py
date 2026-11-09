import os
import sys
import shutil
import tempfile
import subprocess
import zipfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import datetime

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg="#1769db", fg="white", hover_bg="#168fda", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.text = text
        self.width = kwargs.get('width', 200)
        self.height = kwargs.get('height', 40)
        self.configure(width=self.width, height=self.height, bg=parent['bg'])
        
        self.rect = self.create_rounded_rect(0, 0, self.width, self.height, 8, fill=self.bg, outline="")
        self.text_id = self.create_text(self.width/2, self.height/2, text=self.text, fill=self.fg, font=("Segoe UI", 10, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg)

    def on_click(self, e):
        if self.command:
            self.command()

class ObfuscateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BlueForge - Java Obfuscation")
        self.root.geometry("900x650")
        self.root.configure(bg="#070d18")
        self.root.resizable(False, False)

        self.jar_path = None
        self.output_path = None
        self.jobs = []

        # Colors
        self.bg = "#070d18"
        self.panel = "#0c1728"
        self.panel2 = "#101f34"
        self.text = "#edf5ff"
        self.muted = "#8192ad"
        self.blue = "#318cff"
        self.cyan = "#53d8ff"

        self.setup_ui()
        self.check_java()

    def setup_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg="#09101c", width=220, height=650)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        tk.Label(sidebar, text="B", bg=self.blue, fg="white", font=("Segoe UI", 16, "bold"), width=3, height=1).place(x=20, y=20)
        tk.Label(sidebar, text="BLUEFORGE", bg="#09101c", fg=self.text, font=("Segoe UI", 12, "bold")).place(x=70, y=22)
        tk.Label(sidebar, text="JAVA PROTECTION", bg="#09101c", fg=self.muted, font=("Segoe UI", 7)).place(x=70, y=42)

        # Nav
        tk.Label(sidebar, text="WORKSPACE", bg="#09101c", fg=self.muted, font=("Segoe UI", 8, "bold")).place(x=20, y=100)
        
        self.nav_obf = tk.Button(sidebar, text="⌘  Obfuscation", bg=self.panel2, fg=self.text, font=("Segoe UI", 10, "bold"), borderwidth=0, anchor="w", padx=15, pady=10)
        self.nav_obf.place(x=10, y=120, width=200)
        
        self.nav_rec = tk.Button(sidebar, text="◷  Recent", bg="#09101c", fg=self.muted, font=("Segoe UI", 10), borderwidth=0, anchor="w", padx=15, pady=10, command=self.show_recent)
        self.nav_rec.place(x=10, y=165, width=200)

        # Status
        tk.Label(sidebar, text="SYSTEM READY", bg="#09101c", fg="#49e0ae", font=("Segoe UI", 8, "bold")).place(x=20, y=580)
        tk.Label(sidebar, text="Your workspace is ready.", bg="#09101c", fg=self.muted, font=("Segoe UI", 8)).place(x=20, y=600)

        # Main Container
        self.main_frame = tk.Frame(self.root, bg=self.bg)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Pages
        self.page_obf = tk.Frame(self.main_frame, bg=self.bg)
        self.page_rec = tk.Frame(self.main_frame, bg=self.bg)
        
        self.setup_obf_page()
        self.setup_recent_page()
        
        self.show_obf()

    def setup_obf_page(self):
        # Header
        tk.Label(self.page_obf, text="Obfuscate your JAR.", bg=self.bg, fg=self.text, font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=30, pady=(30, 5))
        tk.Label(self.page_obf, text="A clean workspace for your Java projects. Upload an archive, configure your session, and preview the protection workflow.", bg=self.bg, fg=self.muted, font=("Segoe UI", 9), wraplength=550, justify="left").pack(anchor="w", padx=30)

        # Content Grid
        content = tk.Frame(self.page_obf, bg=self.bg)
        content.pack(fill="both", expand=True, padx=30, pady=20)

        # Left Panel (Upload)
        left_panel = tk.Frame(content, bg=self.panel, padx=20, pady=20, highlightbackground=self.panel2, highlightthickness=1)
        left_panel.pack(side="left", fill="both", expand=True)

        tk.Label(left_panel, text="Upload your project", bg=self.panel, fg=self.text, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(left_panel, text="Select a compiled Java archive to begin", bg=self.panel, fg=self.muted, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 15))

        self.upload_btn = ModernButton(left_panel, text="⇧ Choose JAR file", command=self.upload_jar, width=150, height=35)
        self.upload_btn.pack(pady=20)

        self.file_label = tk.Label(left_panel, text="No file selected", bg=self.panel, fg=self.muted, font=("Segoe UI", 9))
        self.file_label.pack()

        # Options
        opt_frame = tk.Frame(left_panel, bg=self.panel2, padx=15, pady=10)
        opt_frame.pack(fill="x", pady=20)
        tk.Label(opt_frame, text="Enhanced protection preview", bg=self.panel2, fg=self.text, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(opt_frame, text="Show the advanced protection workflow in this demo", bg=self.panel2, fg=self.muted, font=("Segoe UI", 8)).pack(anchor="w")

        # Output folder
        self.out_btn = ModernButton(left_panel, text="Select Output Folder", command=self.select_output, bg="#173e5b", hover_bg="#1b5c96", width=150, height=35)
        self.out_btn.pack(pady=10)

        # Start Button
        self.start_btn = ModernButton(left_panel, text="Start obfuscation", command=self.start_obfuscate, width=200, height=45)
        self.start_btn.pack(pady=20)

        # Progress
        self.progress_frame = tk.Frame(left_panel, bg=self.panel)
        self.progress_frame.pack(fill="x", pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="Ready", bg=self.panel, fg=self.cyan, font=("Segoe UI", 9, "bold"))
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="determinate", length=300)
        self.progress_bar.pack(fill="x", pady=5)

        # Right Panel (Info)
        right_panel = tk.Frame(content, bg=self.panel, padx=20, pady=20, width=250, highlightbackground=self.panel2, highlightthickness=1)
        right_panel.pack(side="right", fill="y", padx=(20, 0))
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="How it works", bg=self.panel, fg=self.text, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 20))
        
        steps = [
            ("01 — Import archive", "Choose the compiled .jar file from your device."),
            ("02 — Configure", "Set your preferred options for the preview session."),
            ("03 — Export result", "Review the simulated output and download the demo result.")
        ]
        for title, desc in steps:
            f = tk.Frame(right_panel, bg=self.panel)
            f.pack(fill="x", pady=10)
            tk.Label(f, text=title, bg=self.panel, fg=self.text, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(f, text=desc, bg=self.panel, fg=self.muted, font=("Segoe UI", 8), wraplength=200, justify="left").pack(anchor="w")

    def setup_recent_page(self):
        tk.Label(self.page_rec, text="Recent activity.", bg=self.bg, fg=self.text, font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=30, pady=(30, 5))
        tk.Label(self.page_rec, text="Keep track of your latest obfuscation sessions.", bg=self.bg, fg=self.muted, font=("Segoe UI", 9)).pack(anchor="w", padx=30)
        
        self.rec_list = tk.Frame(self.page_rec, bg=self.bg)
        self.rec_list.pack(fill="both", expand=True, padx=30, pady=20)

    def show_obf(self):
        self.page_rec.pack_forget()
        self.page_obf.pack(fill="both", expand=True)
        self.nav_obf.config(bg=self.panel2, fg=self.text)
        self.nav_rec.config(bg="#09101c", fg=self.muted)

    def show_recent(self):
        self.page_obf.pack_forget()
        self.page_rec.pack(fill="both", expand=True)
        self.nav_obf.config(bg="#09101c", fg=self.muted)
        self.nav_rec.config(bg=self.panel2, fg=self.text)
        self.render_recent()

    def check_java(self):
        try:
            subprocess.run(["java", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showwarning("Java Not Found", 
                "Java (JRE) is not installed on this computer!\n\n"
                "ProGuard needs Java to run. Please install Java 8 or higher.")

    def upload_jar(self):
        path = filedialog.askopenfilename(filetypes=[("JAR files", "*.jar")])
        if path:
            self.jar_path = path
            self.file_label.config(text=f"Selected: {os.path.basename(path)}", fg=self.text)

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.out_btn.text = "Folder Selected"
            self.out_btn.itemconfig(self.out_btn.text_id, text="Folder Selected")

    def start_obfuscate(self):
        if not self.jar_path:
            messagebox.showerror("Error", "Please upload a plugin JAR first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Preparing...")
        threading.Thread(target=self.run_obfuscate, daemon=True).start()

    def run_obfuscate(self):
        try:
            tmp = tempfile.mkdtemp(prefix="obf_")
            unpack = os.path.join(tmp, "unpacked")
            os.makedirs(unpack, exist_ok=True)

            self.update_progress("Extracting plugin...", 10)
            with zipfile.ZipFile(self.jar_path, "r") as z:
                z.extractall(unpack)

            plugin_yml = os.path.join(unpack, "plugin.yml")
            main_class = None
            if os.path.exists(plugin_yml):
                with open(plugin_yml, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip().startswith("main:"):
                            main_class = line.split(":", 1)[1].strip()
                            break
            
            self.update_progress("Building rules...", 30)
            keep_rules = self.build_keep_rules(main_class)
            pro_file = os.path.join(tmp, "keep.pro")
            with open(pro_file, "w") as f:
                f.write(keep_rules)

            self.update_progress("Obfuscating classes...", 50)
            proguard_jar = self.find_proguard()
            if not proguard_jar:
                raise RuntimeError("ProGuard jar not found! The EXE might be corrupted.")

            libs_dir = os.path.join(tmp, "libs")
            os.makedirs(libs_dir, exist_ok=True)
            obf_out = os.path.join(tmp, "obf.jar")

            cmd = [
                "java", "-jar", proguard_jar,
                "-injars", self.jar_path,
                "-outjars", obf_out,
                "-libraryjars", libs_dir,
                "-include", pro_file,
                "-dontwarn", "-dontoptimize", "-dontshrink"
            ]
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            subprocess.run(cmd, check=True, startupinfo=startupinfo)

            self.update_progress("Exporting result...", 90)
            final = os.path.join(
                self.output_path,
                os.path.basename(self.jar_path).replace(".jar", "-obf.jar")
            )
            shutil.copy(obf_out, final)
            
            self.update_progress("Done!", 100)
            self.jobs.append({
                "name": os.path.basename(self.jar_path),
                "output": final,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            messagebox.showinfo("Success", f"Obfuscated plugin saved to:\n{final}")

        except Exception as e:
            self.progress_label.config(text="Error!")
            messagebox.showerror("Obfuscation failed", str(e))

    def update_progress(self, msg, val):
        self.progress_label.config(text=msg)
        self.progress_bar['value'] = val
        self.root.update_idletasks()

    def build_keep_rules(self, main_class):
        lines = [
            "-keepattributes *Annotation*,Signature,Exceptions,InnerClasses",
            "-keep public class * extends org.bukkit.plugin.java.JavaPlugin { *; }",
            "-keep class * implements org.bukkit.event.Listener { *; }",
            "-keepclassmembers class * { @org.bukkit.event.EventHandler <methods>; }",
            "-keep class * implements java.io.Serializable { *; }",
            "-keep enum * { *; }",
            "-keep class org.bukkit.** { *; }",
            "-dontwarn **",
        ]
        if main_class:
            lines.append(f"-keep public class {main_class} {{ *; }}")
        return "\n".join(lines)

    def find_proguard(self):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        for name in ("proguard.jar", "proguard-7.4.2/lib/proguard.jar", os.path.join("proguard", "proguard.jar")):
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        return None

    def render_recent(self):
        for w in self.rec_list.winfo_children():
            w.destroy()
            
        if not self.jobs:
            tk.Label(self.rec_list, text="No sessions yet.", bg=self.bg, fg=self.muted, font=("Segoe UI", 10)).pack(pady=40)
            return

        for job in reversed(self.jobs):
            f = tk.Frame(self.rec_list, bg=self.panel, padx=15, pady=15)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=job["name"], bg=self.panel, fg=self.text, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(f, text=f"Saved: {job['output']} | {job['date']}", bg=self.panel, fg=self.muted, font=("Segoe UI", 8)).pack(anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = ObfuscateApp(root)
    root.mainloop()
