import os
import sys
import shutil
import tempfile
import subprocess
import zipfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ObfuscateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Plugin Obfuscator")
        self.root.geometry("620x460")
        self.root.resizable(False, False)

        self.jar_path = None
        self.output_path = None

        ttk.Label(root, text="Minecraft Plugin Obfuscator",
                  font=("Segoe UI", 16, "bold")).pack(pady=10)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="x")

        ttk.Button(frame, text="Upload Plugin (.jar)",
                   command=self.upload_jar).pack(fill="x", pady=4)

        self.jar_label = ttk.Label(frame, text="No file selected", foreground="gray")
        self.jar_label.pack(fill="x", pady=2)

        ttk.Button(frame, text="Select Output Folder",
                   command=self.select_output).pack(fill="x", pady=4)

        self.out_label = ttk.Label(frame, text="No folder selected", foreground="gray")
        self.out_label.pack(fill="x", pady=2)

        ttk.Button(frame, text="Obfuscate & Build",
                   command=self.start_obfuscate).pack(fill="x", pady=10)

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=5)

        self.log = tk.Text(root, height=12, state="disabled",
                           bg="#111", fg="#0f0", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def log_msg(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def upload_jar(self):
        path = filedialog.askopenfilename(filetypes=[("JAR files", "*.jar")])
        if path:
            self.jar_path = path
            self.jar_label.config(text=os.path.basename(path), foreground="black")

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.out_label.config(text=path, foreground="black")

    def start_obfuscate(self):
        if not self.jar_path:
            messagebox.showerror("Error", "Please upload a plugin JAR first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        self.progress.start(10)
        threading.Thread(target=self.run_obfuscate, daemon=True).start()

    def run_obfuscate(self):
        try:
            tmp = tempfile.mkdtemp(prefix="obf_")
            unpack = os.path.join(tmp, "unpacked")
            os.makedirs(unpack, exist_ok=True)

            self.log_msg(f"[*] Extracting {os.path.basename(self.jar_path)} ...")
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
            self.log_msg(f"[*] Main class: {main_class or 'not found'}")

            keep_rules = self.build_keep_rules(main_class)
            pro_file = os.path.join(tmp, "keep.pro")
            with open(pro_file, "w") as f:
                f.write(keep_rules)

            self.log_msg("[*] Running ProGuard ...")
            proguard_jar = self.find_proguard()
            if not proguard_jar:
                raise RuntimeError("ProGuard jar not found. Reinstall the tool.")

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
            subprocess.run(cmd, check=True)

            final = os.path.join(
                self.output_path,
                os.path.basename(self.jar_path).replace(".jar", "-obf.jar")
            )
            shutil.copy(obf_out, final)
            self.log_msg(f"[+] Done: {final}")
            messagebox.showinfo("Success", f"Obfuscated plugin saved to:\n{final}")

        except Exception as e:
            self.log_msg(f"[!] Error: {e}")
            messagebox.showerror("Obfuscation failed", str(e))
        finally:
            self.progress.stop()

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
        for name in ("proguard.jar", "proguard-7.4.2/lib/proguard.jar"):
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        return None


if __name__ == "__main__":
    root = tk.Tk()
    ObfuscateApp(root)
    root.mainloop()
