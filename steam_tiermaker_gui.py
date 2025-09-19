#!/usr/bin/env python3
"""
Steam to TierMaker GUI Application

A standalone GUI application that combines Steam image scraping and TierMaker uploading
into a single executable with a simple interface.

Author: AI Assistant
License: MIT
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import os
import sys
import json
import time
from typing import Dict, Any

# Import our modules
from steam_image_scraper import SteamImageScraper
from tiermaker_uploader import TierMakerUploader


class SteamTierMakerGUI:
    """Main GUI application for Steam to TierMaker workflow."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Steam to TierMaker - Image Scraper & Uploader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configuration
        self.config_file = "config.json"
        self.config = self.load_config()
        
        # Language system
        self.language = self.config.get("language", "chinese")
        self.translations = self.load_translations()
        
        # State variables
        self.is_running = False
        self.current_step = ""
        
        # Queue for thread-safe GUI updates
        self.log_queue = queue.Queue()
        
        # Setup GUI
        self.setup_gui()
        
        # Start log queue processor
        self.process_log_queue()
    
    def load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation strings for different languages."""
        return {
            "english": {
                "title": "Steam to TierMaker - Image Scraper & Uploader",
                "config": "Configuration",
                "steam_url": "Steam Library URL:",
                "output_folder": "Output Folder:",
                "browse": "Browse",
                "start_process": "Start Process",
                "stop": "Stop",
                "clear_log": "Clear Log",
                "progress": "Progress",
                "ready": "Ready to start...",
                "status_ready": "Ready",
                "language": "Language:",
                "placeholder_url": "https://steamcommunity.com/profiles/<your steam id>/games/?tab=all",
                "error_url": "Please enter a Steam library URL",
                "error_folder": "Please specify an output folder",
                "starting": "Starting Steam image scraping...",
                "navigating": "Navigating to Steam library...",
                "login_required": "Steam login required!",
                "login_instructions": "Please log in to Steam in the browser window that opened.",
                "login_waiting": "Waiting for login to complete...",
                "login_detected": "Login detected! Starting download process...",
                "login_timeout": "Login timeout. Please make sure you are logged in.",
                "loading_content": "Loading all content by scrolling...",
                "found_images": "Found {count} total images to download",
                "no_images": "No images found to download",
                "starting_downloads": "Starting image downloads...",
                "downloading": "Downloading: {current}/{total} ({percent:.1f}%) - {game}",
                "failed_download": "Failed to download: {game}",
                "failed_list": "{count} images failed to download:",
                "all_success": "All images downloaded successfully!",
                "download_summary": "Download Summary:",
                "total_found": "Total images found: {count}",
                "successful": "Successful downloads: {count}",
                "failed": "Failed downloads: {count}",
                "summary_saved": "Summary saved to: {file}",
                "scraping_completed": "Steam image scraping completed!",
                "uploading": "Starting TierMaker upload...",
                "process_completed": "Process completed successfully!",
                "browser_ready": "Browser is open with your images ready for tier list creation!",
                "upload_failed": "TierMaker upload failed",
                "process_failed": "Process failed: {error}",
                "process_stopped": "Process stopped by user",
                "process_completed_status": "Process completed"
            },
            "chinese": {
                "title": "Steam 到 TierMaker - 图片抓取器和上传器",
                "config": "配置",
                "steam_url": "Steam 游戏库链接:",
                "output_folder": "输出文件夹:",
                "browse": "浏览",
                "start_process": "开始处理",
                "stop": "停止",
                "clear_log": "清除日志",
                "progress": "进度",
                "ready": "准备开始...",
                "status_ready": "就绪",
                "language": "语言:",
                "placeholder_url": "https://steamcommunity.com/profiles/<你的steam id>/games/?tab=all",
                "error_url": "请输入 Steam 游戏库链接",
                "error_folder": "请指定输出文件夹",
                "starting": "开始 Steam 图片抓取...",
                "navigating": "正在导航到 Steam 游戏库...",
                "login_required": "需要 Steam 登录!",
                "login_instructions": "请在打开的浏览器窗口中登录 Steam。",
                "login_waiting": "等待登录完成...",
                "login_detected": "检测到登录! 开始下载过程...",
                "login_timeout": "登录超时。请确保您已登录。",
                "loading_content": "通过滚动加载所有内容...",
                "found_images": "找到 {count} 张图片需要下载",
                "no_images": "未找到要下载的图片",
                "starting_downloads": "开始图片下载...",
                "downloading": "正在下载: {current}/{total} ({percent:.1f}%) - {game}",
                "failed_download": "下载失败: {game}",
                "failed_list": "{count} 张图片下载失败:",
                "all_success": "所有图片下载成功!",
                "download_summary": "下载摘要:",
                "total_found": "找到的图片总数: {count}",
                "successful": "成功下载: {count}",
                "failed": "下载失败: {count}",
                "summary_saved": "摘要已保存到: {file}",
                "scraping_completed": "Steam 图片抓取完成!",
                "uploading": "开始 TierMaker 上传...",
                "process_completed": "处理完成!",
                "browser_ready": "浏览器已打开，您的图片已准备好创建等级列表!",
                "upload_failed": "TierMaker 上传失败",
                "process_failed": "处理失败: {error}",
                "process_stopped": "用户停止了处理",
                "process_completed_status": "处理完成"
            }
        }
    
    def t(self, key: str, **kwargs) -> str:
        """Get translated string for current language."""
        text = self.translations.get(self.language, {}).get(key, key)
        return text.format(**kwargs) if kwargs else text
    
    def switch_language(self, language: str):
        """Switch application language and reload the app."""
        if language != self.language:
            self.language = language
            # Save language preference to config
            self.config["language"] = language
            self.save_config()
            self.reload_app()
    
    def reload_app(self):
        """Reload the entire application with new language."""
        # Save current state
        current_url = self.url_var.get() if hasattr(self, 'url_var') else ""
        current_output = self.output_var.get() if hasattr(self, 'output_var') else "steam_images"
        
        # Check if current URL is placeholder text
        old_placeholder = "https://steamcommunity.com/profiles/<your steam id>/games/?tab=all"
        if self.language == "chinese":
            old_placeholder = "https://steamcommunity.com/profiles/<你的steam id>/games/?tab=all"
        
        is_placeholder = current_url == old_placeholder or current_url == ""
        
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate the GUI
        self.setup_gui()
        
        # Restore previous values
        if hasattr(self, 'url_var'):
            if is_placeholder:
                # Set new placeholder text
                new_placeholder = self.t("placeholder_url")
                self.url_var.set(new_placeholder)
                # Set the entry widget to gray
                self.set_url_entry_gray()
            else:
                # Restore actual URL
                self.url_var.set(current_url)
        
        if hasattr(self, 'output_var'):
            self.output_var.set(current_output)
        
        # Restart log queue processor
        self.process_log_queue()
    
    def set_url_entry_gray(self):
        """Set the URL entry widget to gray color for placeholder."""
        # Find the URL entry widget and set it to gray
        def find_and_set_gray(widget):
            if isinstance(widget, ttk.Entry):
                widget.config(foreground='gray')
                return True
            for child in widget.winfo_children():
                if find_and_set_gray(child):
                    return True
            return False
        
        for widget in self.root.winfo_children():
            find_and_set_gray(widget)
    
    def update_ui_language(self):
        """Update all UI text to current language."""
        self.root.title(self.t("title"))
        # This method is no longer used since we reload the entire app
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "steam_library_url": "",
            "output_folder": "steam_images",
            "delay_between_downloads": 0.1,
            "scroll_pause": 0.1,
            "max_scroll_attempts": 1000,
            "language": "english"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Could not load config file: {e}. Using defaults.")
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        return default_config
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_message(f"Error saving config: {e}", "ERROR")
    
    def setup_gui(self):
        """Setup the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Steam to TierMaker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Language switch
        language_frame = ttk.Frame(main_frame)
        language_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(language_frame, text=self.t("language")).pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value=self.language)
        language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                    values=["english", "chinese"], state="readonly", width=10)
        language_combo.pack(side=tk.LEFT, padx=(10, 0))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text=self.t("config"), padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Steam URL
        ttk.Label(config_frame, text=self.t("steam_url")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.url_var = tk.StringVar(value=self.config.get("steam_library_url", ""))
        url_entry = ttk.Entry(config_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Add placeholder text
        placeholder_text = self.t("placeholder_url")
        
        def on_focus_in(event):
            if self.url_var.get() == placeholder_text:
                self.url_var.set("")
                url_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not self.url_var.get():
                self.url_var.set(placeholder_text)
                url_entry.config(foreground='gray')
        
        # Set initial placeholder if empty
        if not self.url_var.get():
            self.url_var.set(placeholder_text)
            url_entry.config(foreground='gray')
        
        url_entry.bind('<FocusIn>', on_focus_in)
        url_entry.bind('<FocusOut>', on_focus_out)
        
        # Output folder
        ttk.Label(config_frame, text=self.t("output_folder")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_var = tk.StringVar(value=self.config.get("output_folder", "steam_images"))
        output_entry = ttk.Entry(config_frame, textvariable=self.output_var, width=60)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        browse_btn = ttk.Button(config_frame, text=self.t("browse"), command=self.browse_folder)
        browse_btn.grid(row=1, column=2, padx=(10, 0), pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Create custom style for start button
        style = ttk.Style()
        style.configure("Start.TButton", 
                       background="#4CAF50",  # Green background
                       foreground="white",    # White text
                       font=("Arial", 10, "bold"),
                       padding=(20, 10))
        style.map("Start.TButton",
                 background=[('active', '#45a049')])  # Darker green when hovered
        
        self.run_button = ttk.Button(button_frame, text=self.t("start_process"), 
                                   command=self.start_process, style="Start.TButton")
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text=self.t("stop"), 
                                    command=self.stop_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text=self.t("clear_log"), 
                                     command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text=self.t("progress"), padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=20, width=80)
        self.log_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value=self.t("status_ready"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def on_language_change(self, event=None):
        """Handle language change."""
        new_language = self.language_var.get()
        if new_language != self.language:
            self.switch_language(new_language)
    
    def browse_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log queue for thread-safe display."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log_queue.put(log_entry)
    
    def process_log_queue(self):
        """Process log messages from queue and display in GUI."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_log_queue)
    
    def clear_log(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, message: str):
        """Update progress display."""
        self.status_var.set(message)
        self.log_message(message)
    
    def start_process(self):
        """Start the Steam scraping and TierMaker upload process."""
        if self.is_running:
            return
        
        # Validate inputs
        steam_url = self.url_var.get().strip()
        placeholder_text = self.t("placeholder_url")
        if not steam_url or steam_url == placeholder_text:
            messagebox.showerror("Error", self.t("error_url"))
            return
        
        output_folder = self.output_var.get().strip()
        if not output_folder:
            messagebox.showerror("Error", self.t("error_folder"))
            return
        
        # Update config
        self.config["steam_library_url"] = steam_url
        self.config["output_folder"] = output_folder
        self.save_config()
        
        # Update UI state
        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.clear_log()
        
        # Start process in separate thread
        self.process_thread = threading.Thread(target=self.run_workflow, daemon=True)
        self.process_thread.start()
    
    def stop_process(self):
        """Stop the current process."""
        self.is_running = False
        self.update_progress(self.t("process_stopped"))
        self.finish_process()
    
    def finish_process(self):
        """Finish the process and update UI."""
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set(self.t("process_completed_status"))
    
    def run_workflow(self):
        """Run the complete workflow in a separate thread."""
        try:
            self.update_progress(self.t("starting"))
            
            # Step 1: Steam Image Scraping
            self.current_step = "scraping"
            scraper = SteamImageScraper(self.config_file)
            
            # Override URL if provided
            if self.url_var.get().strip():
                scraper.url = self.url_var.get().strip()
                scraper.config['steam_library_url'] = self.url_var.get().strip()
            
            # Override output folder
            scraper.output_folder = self.output_var.get().strip()
            scraper.config['output_folder'] = self.output_var.get().strip()
            
            # Create output folder
            os.makedirs(scraper.output_folder, exist_ok=True)
            
            if not self.is_running:
                return
            
            self.update_progress(self.t("navigating"))
            
            # Use the original scraper method and capture results
            scrape_results = scraper.scrape_images()
            
            if not self.is_running:
                scraper.close()
                return
            
            # Display download statistics
            if scrape_results:
                total_found = scrape_results.get("total_images_found", 0)
                successful = scrape_results.get("successful_downloads", 0)
                failed = scrape_results.get("failed_downloads", 0)
                failed_games = scrape_results.get("failed_games", [])
                
                self.log_message(f"📊 Download Summary:", "INFO")
                self.log_message(f"  Total images found: {total_found}", "INFO")
                self.log_message(f"  Successful downloads: {successful}", "SUCCESS")
                self.log_message(f"  Failed downloads: {failed}", "ERROR" if failed > 0 else "SUCCESS")
                
                # Display failed game names
                if failed_games:
                    self.log_message(f"\n❌ Failed to download {len(failed_games)} games:", "ERROR")
                    for i, game_name in enumerate(failed_games, 1):
                        self.log_message(f"  [{i}] {game_name}", "ERROR")
                else:
                    self.log_message("✅ All games downloaded successfully!", "SUCCESS")
            
            self.update_progress(self.t("scraping_completed"))
            scraper.close()
            
            # Step 2: TierMaker Upload
            self.current_step = "uploading"
            self.update_progress(self.t("uploading"))
            
            uploader = TierMakerUploader(scraper.output_folder)
            
            if not self.is_running:
                return
            
            success = uploader.upload_images_to_tiermaker()
            
            if success:
                self.update_progress(self.t("process_completed"))
                self.update_progress(self.t("browser_ready"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"{self.t('process_completed')}\n\n{self.t('browser_ready')}\nYou can now create your tier list!"))
            else:
                self.update_progress(self.t("upload_failed"))
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"{self.t('upload_failed')}. Check the log for details."))
            
        except Exception as e:
            error_msg = self.t("process_failed", error=str(e))
            self.update_progress(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, self.finish_process)
    


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the application
    app = SteamTierMakerGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Quit", "Process is running. Do you want to quit?"):
                app.is_running = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
