# Obfuscate-pokemon

Minecraft plugin obfuscator with a simple GUI. Runs fully local (no backend).

## Features
- Upload a plugin `.jar`
- Choose an output folder
- Press **Obfuscate & Build** → get `*-obf.jar` that is hard to read but keeps working

## Build EXE
Every push to `main` triggers GitHub Actions to build `ObfuscateTool.exe`.
Download it from the **Actions** tab → latest run → **Artifacts**.

## Requirements
- Java (JRE 8+) installed on the machine running the EXE (ProGuard needs it).
