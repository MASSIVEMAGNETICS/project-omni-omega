#!/usr/bin/env python3
"""
OmniLoader Studio - GUI Installer
Production-grade local-first AI model manager

Features:
- Choose installation directory
- Choose installation options (shortcuts, venv)
- Real-time progress display
- "Run Now" button on completion
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil

# Constants
APP_NAME = "OmniLoader Studio"
VERSION = "1.0.0"

# Default installation directory
DEFAULT_INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))


class InstallerGUI:
    """Main installer GUI class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Installer")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)
        
        # Installation state
        self.install_dir = tk.StringVar(value=DEFAULT_INSTALL_DIR)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_startmenu_shortcut = tk.BooleanVar(value=True)
        self.create_venv = tk.BooleanVar(value=True)
        self.install_mode = tk.StringVar(value="full")
        self.is_installing = False
        self.installation_complete = False
        
        # Apply dark theme
        self._apply_theme()
        
        # Build UI
        self._build_ui()
        
    def _apply_theme(self):
        """Apply dark neon theme matching OmniLoader Studio."""
        self.root.configure(bg="#0a0a0a")
        
        # Style configuration
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure dark theme colors
        style.configure(".", 
            background="#0a0a0a",
            foreground="#00ff41",
            fieldbackground="#0a0a0a",
            font=("Segoe UI", 10))
        
        style.configure("TFrame", background="#0a0a0a")
        style.configure("TLabel", background="#0a0a0a", foreground="#00ff41")
        style.configure("TButton", 
            background="#1a001a", 
            foreground="#ff00ff",
            bordercolor="#ff00ff",
            focuscolor="#ff00ff",
            padding=(10, 5))
        style.map("TButton",
            background=[("active", "#2a002a"), ("pressed", "#3a003a")])
        
        style.configure("TCheckbutton", 
            background="#0a0a0a", 
            foreground="#00ff41")
        style.map("TCheckbutton",
            background=[("active", "#0a0a0a")])
        
        style.configure("TRadiobutton",
            background="#0a0a0a",
            foreground="#00ff41")
        style.map("TRadiobutton",
            background=[("active", "#0a0a0a")])
        
        style.configure("TEntry",
            fieldbackground="#0a0a0a",
            foreground="#00ff41",
            insertcolor="#ff00ff")
        
        style.configure("TLabelframe", 
            background="#0a0a0a", 
            foreground="#ff00ff",
            bordercolor="#9d00ff")
        style.configure("TLabelframe.Label", 
            background="#0a0a0a", 
            foreground="#ff00ff")
        
        # Progress bar style
        style.configure("Neon.Horizontal.TProgressbar",
            troughcolor="#0a0a0a",
            background="#ff00ff",
            bordercolor="#9d00ff",
            lightcolor="#ff00ff",
            darkcolor="#9d00ff")
        
    def _build_ui(self):
        """Build the installer user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._build_header(main_frame)
        
        # Notebook for pages
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Page 1: Installation Location
        self.page_location = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.page_location, text="📁 Location")
        self._build_location_page(self.page_location)
        
        # Page 2: Installation Options
        self.page_options = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.page_options, text="⚙️ Options")
        self._build_options_page(self.page_options)
        
        # Page 3: Progress
        self.page_progress = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.page_progress, text="📊 Progress")
        self._build_progress_page(self.page_progress)
        
        # Bottom buttons
        self._build_buttons(main_frame)
        
    def _build_header(self, parent):
        """Build the header section with logo and title."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ASCII art title (simplified for GUI)
        title_label = tk.Label(
            header_frame,
            text="🤖 OmniLoader Studio",
            font=("Segoe UI", 24, "bold"),
            fg="#ff00ff",
            bg="#0a0a0a"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="One-Click GUI Installer",
            font=("Segoe UI", 12),
            fg="#00ff41",
            bg="#0a0a0a"
        )
        subtitle_label.pack()
        
        version_label = tk.Label(
            header_frame,
            text=f"Version {VERSION}",
            font=("Segoe UI", 9),
            fg="#9d00ff",
            bg="#0a0a0a"
        )
        version_label.pack()
        
    def _build_location_page(self, parent):
        """Build the installation location selection page."""
        # Description
        desc_label = tk.Label(
            parent,
            text="Choose where to install OmniLoader Studio:",
            font=("Segoe UI", 11),
            fg="#00ff41",
            bg="#0a0a0a",
            anchor="w"
        )
        desc_label.pack(fill=tk.X, pady=(0, 10))
        
        # Directory selection frame
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=5)
        
        dir_label = ttk.Label(dir_frame, text="Installation Directory:")
        dir_label.pack(anchor="w")
        
        entry_frame = ttk.Frame(dir_frame)
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(entry_frame, textvariable=self.install_dir, width=60)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(entry_frame, text="Browse...", command=self._browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Space requirements info
        info_frame = ttk.LabelFrame(parent, text="Space Requirements", padding="10")
        info_frame.pack(fill=tk.X, pady=20)
        
        space_info = tk.Label(
            info_frame,
            text="• Base installation: ~50 MB\n"
                 "• Python dependencies: ~2-5 GB (varies by model adapters)\n"
                 "• AI Models: 1-30+ GB each (downloaded separately)\n\n"
                 "Recommended: At least 10 GB free disk space",
            font=("Segoe UI", 10),
            fg="#00ff41",
            bg="#0a0a0a",
            justify="left",
            anchor="w"
        )
        space_info.pack(fill=tk.X)
        
    def _build_options_page(self, parent):
        """Build the installation options page."""
        # Installation mode
        mode_frame = ttk.LabelFrame(parent, text="Installation Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            mode_frame, 
            text="Full Installation (Recommended) - All features and dependencies",
            variable=self.install_mode,
            value="full"
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            mode_frame,
            text="Minimal Installation - Core dependencies only",
            variable=self.install_mode,
            value="minimal"
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            mode_frame,
            text="Custom Installation - Choose specific components",
            variable=self.install_mode,
            value="custom"
        ).pack(anchor="w", pady=2)
        
        # Virtual environment option
        venv_frame = ttk.LabelFrame(parent, text="Python Environment", padding="10")
        venv_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(
            venv_frame,
            text="Create virtual environment (Recommended)",
            variable=self.create_venv
        ).pack(anchor="w", pady=2)
        
        venv_info = tk.Label(
            venv_frame,
            text="A virtual environment keeps OmniLoader's dependencies isolated from your system Python.",
            font=("Segoe UI", 9),
            fg="#9d00ff",
            bg="#0a0a0a",
            wraplength=500,
            justify="left"
        )
        venv_info.pack(anchor="w", pady=(5, 0))
        
        # Shortcuts
        shortcut_frame = ttk.LabelFrame(parent, text="Shortcuts", padding="10")
        shortcut_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(
            shortcut_frame,
            text="Create Desktop shortcut",
            variable=self.create_desktop_shortcut
        ).pack(anchor="w", pady=2)
        
        ttk.Checkbutton(
            shortcut_frame,
            text="Create Start Menu shortcut",
            variable=self.create_startmenu_shortcut
        ).pack(anchor="w", pady=2)
        
    def _build_progress_page(self, parent):
        """Build the progress display page."""
        # Status label
        self.status_label = tk.Label(
            parent,
            text="Ready to install",
            font=("Segoe UI", 11),
            fg="#ff00ff",
            bg="#0a0a0a"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            parent,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            style="Neon.Horizontal.TProgressbar",
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Percentage label
        self.percent_label = tk.Label(
            parent,
            text="0%",
            font=("Segoe UI", 10),
            fg="#00ff41",
            bg="#0a0a0a"
        )
        self.percent_label.pack()
        
        # Log output
        log_frame = ttk.LabelFrame(parent, text="Installation Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create text widget with scrollbar
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            height=12,
            bg="#0a0a0a",
            fg="#00ff41",
            insertbackground="#ff00ff",
            selectbackground="#9d00ff",
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=log_scroll.set
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)
        
        # Configure log text tags for colored output
        self.log_text.tag_configure("info", foreground="#00ff41")
        self.log_text.tag_configure("success", foreground="#00ff41")
        self.log_text.tag_configure("warning", foreground="#ffff00")
        self.log_text.tag_configure("error", foreground="#ff0066")
        self.log_text.tag_configure("step", foreground="#ff00ff")
        
    def _build_buttons(self, parent):
        """Build the bottom button row."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side - Back button
        self.back_btn = ttk.Button(button_frame, text="← Back", command=self._go_back)
        self.back_btn.pack(side=tk.LEFT)
        
        # Right side buttons
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.next_btn = ttk.Button(button_frame, text="Next →", command=self._go_next)
        self.next_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.install_btn = ttk.Button(button_frame, text="🚀 Install", command=self._start_installation)
        self.install_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.install_btn.pack_forget()  # Hide initially
        
        self.run_btn = ttk.Button(button_frame, text="▶ Run Now", command=self._run_application)
        self.run_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.run_btn.pack_forget()  # Hide initially
        
    def _browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(
            initialdir=self.install_dir.get(),
            title="Select Installation Directory"
        )
        if directory:
            self.install_dir.set(directory)
            
    def _go_back(self):
        """Go to previous page."""
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.select(current - 1)
            self._update_buttons()
            
    def _go_next(self):
        """Go to next page."""
        current = self.notebook.index(self.notebook.select())
        if current < 2:
            self.notebook.select(current + 1)
            self._update_buttons()
            
    def _update_buttons(self):
        """Update button visibility based on current page."""
        current = self.notebook.index(self.notebook.select())
        
        # Back button
        if current == 0:
            self.back_btn.config(state=tk.DISABLED)
        else:
            self.back_btn.config(state=tk.NORMAL)
            
        # Next/Install buttons
        if current == 2:  # Progress page
            self.next_btn.pack_forget()
            if not self.is_installing and not self.installation_complete:
                self.install_btn.pack(side=tk.RIGHT, padx=(5, 0))
            if self.installation_complete:
                self.run_btn.pack(side=tk.RIGHT, padx=(5, 0))
        else:
            self.install_btn.pack_forget()
            self.run_btn.pack_forget()
            self.next_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
    def _log(self, message, tag="info"):
        """Add a message to the log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        
    def _update_progress(self, value, status=None):
        """Update progress bar and status."""
        self.progress_var.set(value)
        self.percent_label.config(text=f"{int(value)}%")
        if status:
            self.status_label.config(text=status)
        self.root.update()
        
    def _start_installation(self):
        """Start the installation process."""
        if self.is_installing:
            return
            
        self.is_installing = True
        self.install_btn.config(state=tk.DISABLED)
        self.back_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        
        # Run installation in a separate thread
        thread = threading.Thread(target=self._run_installation)
        thread.daemon = True
        thread.start()
        
    def _run_installation(self):
        """Run the actual installation process."""
        try:
            install_dir = self.install_dir.get()
            
            # Step 1: Validate directory (5%)
            self._update_progress(0, "Validating installation directory...")
            self._log(f"Installation directory: {install_dir}", "step")
            
            if not os.path.exists(install_dir):
                self._log("Creating installation directory...", "info")
                os.makedirs(install_dir, exist_ok=True)
            
            self._update_progress(5, "Directory validated")
            self._log("✓ Directory validated", "success")
            
            # Step 2: Check Python (10%)
            self._update_progress(10, "Checking Python installation...")
            self._log("[1/6] Checking Python installation...", "step")
            
            try:
                result = subprocess.run(
                    [sys.executable, "--version"],
                    capture_output=True,
                    text=True
                )
                python_version = result.stdout.strip()
                self._log(f"✓ {python_version} found", "success")
            except Exception as e:
                self._log(f"✗ Python check failed: {e}", "error")
                self._installation_failed("Python is required but not found")
                return
                
            self._update_progress(15)
            
            # Step 3: Create virtual environment (30%)
            if self.create_venv.get():
                self._update_progress(20, "Creating virtual environment...")
                self._log("[2/6] Creating virtual environment...", "step")
                
                venv_path = os.path.join(install_dir, "venv")
                if not os.path.exists(venv_path):
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "venv", venv_path],
                            check=True,
                            capture_output=True
                        )
                        self._log("✓ Virtual environment created", "success")
                    except subprocess.CalledProcessError as e:
                        self._log(f"✗ Failed to create virtual environment: {e}", "error")
                        self._installation_failed("Failed to create virtual environment")
                        return
                else:
                    self._log("✓ Virtual environment already exists", "success")
                    
            self._update_progress(30)
            
            # Step 4: Install dependencies (70%)
            self._update_progress(35, "Installing dependencies...")
            self._log("[3/6] Installing dependencies...", "step")
            self._log("This may take 5-15 minutes depending on your internet connection...", "info")
            
            # Get pip path
            if self.create_venv.get():
                venv_path = os.path.join(install_dir, "venv")
                if os.name == "nt":
                    pip_path = os.path.join(venv_path, "Scripts", "pip")
                    python_path = os.path.join(venv_path, "Scripts", "python")
                else:
                    pip_path = os.path.join(venv_path, "bin", "pip")
                    python_path = os.path.join(venv_path, "bin", "python")
            else:
                pip_path = [sys.executable, "-m", "pip"]
                python_path = sys.executable
                
            # Upgrade pip
            self._log("Upgrading pip...", "info")
            try:
                if isinstance(pip_path, list):
                    subprocess.run(pip_path + ["install", "--upgrade", "pip"], 
                                   check=True, capture_output=True)
                else:
                    subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                                   check=True, capture_output=True)
                self._log("✓ pip upgraded", "success")
            except subprocess.CalledProcessError:
                self._log("⚠ pip upgrade failed, continuing...", "warning")
                
            self._update_progress(40)
            
            # Install requirements
            requirements_file = os.path.join(install_dir, "requirements.txt")
            if os.path.exists(requirements_file):
                self._log("Installing from requirements.txt...", "info")
                try:
                    if isinstance(pip_path, list):
                        cmd = pip_path + ["install", "-r", requirements_file]
                    else:
                        cmd = [pip_path, "install", "-r", requirements_file]
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    
                    # Stream output
                    for line in iter(process.stdout.readline, ''):
                        if line.strip():
                            # Show package installation progress
                            if "Collecting" in line or "Installing" in line or "Successfully" in line:
                                self._log(line.strip(), "info")
                            # Update progress incrementally
                            current = self.progress_var.get()
                            if current < 65:
                                self._update_progress(current + 0.5)
                                
                    process.wait()
                    if process.returncode == 0:
                        self._log("✓ All dependencies installed", "success")
                    else:
                        self._log("⚠ Some dependencies may have failed to install", "warning")
                        
                except Exception as e:
                    self._log(f"⚠ Dependency installation had issues: {e}", "warning")
            else:
                self._log("⚠ requirements.txt not found", "warning")
                
            self._update_progress(70)
            
            # Step 5: Validate installation (80%)
            self._update_progress(75, "Validating installation...")
            self._log("[4/6] Validating installation...", "step")
            
            validate_script = os.path.join(install_dir, "validate_install.py")
            if os.path.exists(validate_script):
                try:
                    if isinstance(python_path, str):
                        result = subprocess.run(
                            [python_path, validate_script],
                            capture_output=True,
                            text=True,
                            cwd=install_dir
                        )
                    else:
                        result = subprocess.run(
                            [sys.executable, validate_script],
                            capture_output=True,
                            text=True,
                            cwd=install_dir
                        )
                    if result.returncode == 0:
                        self._log("✓ Installation validated", "success")
                    else:
                        self._log("⚠ Validation had issues, but installation completed", "warning")
                except Exception as e:
                    self._log(f"⚠ Validation skipped: {e}", "warning")
            else:
                self._log("⚠ Validation script not found, skipping", "warning")
                
            self._update_progress(80)
            
            # Step 6: Create shortcuts (90%)
            self._update_progress(85, "Creating shortcuts...")
            self._log("[5/6] Creating shortcuts...", "step")
            
            if os.name == "nt":  # Windows
                self._create_windows_shortcuts(install_dir)
            else:
                self._log("⚠ Shortcuts not created (non-Windows OS)", "warning")
                
            self._update_progress(90)
            
            # Step 7: Finalize (100%)
            self._update_progress(95, "Finalizing installation...")
            self._log("[6/6] Finalizing installation...", "step")
            
            self._update_progress(100, "Installation complete!")
            self._log("", "info")
            self._log("═" * 50, "success")
            self._log("   INSTALLATION COMPLETE!", "success")
            self._log("═" * 50, "success")
            self._log("", "info")
            self._log("OmniLoader Studio has been installed successfully!", "success")
            self._log("", "info")
            self._log("To launch OmniLoader Studio:", "info")
            self._log("  • Click 'Run Now' button below", "info")
            self._log("  • Or use the Desktop/Start Menu shortcut", "info")
            self._log("  • Or run OmniLoader.bat in the installation directory", "info")
            self._log("", "info")
            self._log("Access URLs after launch:", "info")
            self._log("  • Studio UI: http://localhost:8501", "info")
            self._log("  • API Docs:  http://localhost:8000/docs", "info")
            
            # Enable Run Now button
            self.installation_complete = True
            self.root.after(0, self._show_run_button)
            
        except Exception as e:
            self._log(f"✗ Installation failed: {e}", "error")
            self._installation_failed(str(e))
            
    def _create_windows_shortcuts(self, install_dir):
        """Create Windows shortcuts for the application."""
        try:
            # Desktop shortcut
            if self.create_desktop_shortcut.get():
                desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
                shortcut_path = os.path.join(desktop, "OmniLoader Studio.lnk")
                target = os.path.join(install_dir, "OmniLoader.bat")
                
                ps_script = f'''
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{target}"
                $Shortcut.WorkingDirectory = "{install_dir}"
                $Shortcut.Description = "OmniLoader Studio - Production-grade local-first AI model manager"
                $Shortcut.Save()
                '''
                
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    check=False
                )
                
                if os.path.exists(shortcut_path):
                    self._log(f"✓ Desktop shortcut created", "success")
                else:
                    self._log("⚠ Could not create desktop shortcut", "warning")
                    
            # Start Menu shortcut
            if self.create_startmenu_shortcut.get():
                start_menu = os.path.join(
                    os.environ.get("APPDATA", ""),
                    "Microsoft", "Windows", "Start Menu", "Programs"
                )
                omni_folder = os.path.join(start_menu, "OmniLoader Studio")
                os.makedirs(omni_folder, exist_ok=True)
                
                shortcut_path = os.path.join(omni_folder, "OmniLoader Studio.lnk")
                target = os.path.join(install_dir, "OmniLoader.bat")
                
                ps_script = f'''
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{target}"
                $Shortcut.WorkingDirectory = "{install_dir}"
                $Shortcut.Description = "OmniLoader Studio - Production-grade local-first AI model manager"
                $Shortcut.Save()
                '''
                
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    check=False
                )
                
                if os.path.exists(shortcut_path):
                    self._log(f"✓ Start Menu shortcut created", "success")
                else:
                    self._log("⚠ Could not create Start Menu shortcut", "warning")
                    
        except Exception as e:
            self._log(f"⚠ Shortcut creation failed: {e}", "warning")
            
    def _installation_failed(self, message):
        """Handle installation failure."""
        self.is_installing = False
        self.root.after(0, lambda: self._show_failure(message))
        
    def _show_failure(self, message):
        """Show installation failure message."""
        self.status_label.config(text="Installation failed", fg="#ff0066")
        self.install_btn.config(state=tk.NORMAL)
        self.back_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL)
        messagebox.showerror("Installation Failed", message)
        
    def _show_run_button(self):
        """Show the Run Now button after successful installation."""
        self.is_installing = False
        self.install_btn.pack_forget()
        self.run_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.cancel_btn.config(text="Close", state=tk.NORMAL)
        self.back_btn.config(state=tk.DISABLED)
        
    def _run_application(self):
        """Launch OmniLoader Studio."""
        install_dir = self.install_dir.get()
        
        # Try to find the launcher
        if os.name == "nt":
            launcher = os.path.join(install_dir, "OmniLoader.bat")
            if os.path.exists(launcher):
                self._log("Launching OmniLoader Studio...", "step")
                subprocess.Popen(
                    ["cmd", "/c", "start", "", launcher],
                    cwd=install_dir,
                    shell=True
                )
                self.root.after(2000, self.root.destroy)
            else:
                messagebox.showwarning(
                    "Launcher Not Found",
                    f"Could not find OmniLoader.bat in {install_dir}"
                )
        else:
            launcher = os.path.join(install_dir, "run_omni.sh")
            if os.path.exists(launcher):
                self._log("Launching OmniLoader Studio...", "step")
                subprocess.Popen(
                    ["bash", launcher],
                    cwd=install_dir
                )
                self.root.after(2000, self.root.destroy)
            else:
                messagebox.showwarning(
                    "Launcher Not Found",
                    f"Could not find run_omni.sh in {install_dir}"
                )
                
    def _cancel(self):
        """Cancel installation or close the application."""
        if self.is_installing:
            if messagebox.askyesno("Cancel Installation", 
                                   "Are you sure you want to cancel the installation?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    
    # Set icon if available
    try:
        # Try to set a custom icon (if available)
        pass
    except Exception:
        pass
        
    app = InstallerGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
