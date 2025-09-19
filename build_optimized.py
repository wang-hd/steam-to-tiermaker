#!/usr/bin/env python3
"""
Optimized Build Script for Steam to TierMaker GUI Executable

This script creates a smaller executable by excluding unnecessary modules.

Usage:
    python build_optimized.py

Author: AI Assistant
License: MIT
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller is installed")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")
    
    return True


def build_optimized_executable():
    """Build an optimized smaller executable."""
    print("🔨 Building optimized executable (smaller size)...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build directory")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned dist directory")
    
    # PyInstaller command with size optimizations
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single file
        "--windowed",                   # No console
        "--name=SteamToTierMaker",      # Executable name
        "--clean",                      # Clean cache
        "--noconfirm",                  # Don't ask for confirmation
        
        # SIZE OPTIMIZATIONS:
        "--strip",                      # Remove debug symbols
        "--optimize=2",                 # Python optimization level
        
        # EXCLUDE UNNECESSARY MODULES (saves ~10-20 MB):
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=IPython",
        "--exclude-module=jupyter",
        "--exclude-module=notebook",
        "--exclude-module=tkinter.test",
        "--exclude-module=test",
        "--exclude-module=unittest",
        "--exclude-module=doctest",
        "--exclude-module=pdb",
        "--exclude-module=profile",
        "--exclude-module=pstats",
        "--exclude-module=cProfile",
        "--exclude-module=multiprocessing.dummy",
        "--exclude-module=concurrent.futures",
        "--exclude-module=asyncio",
        "--exclude-module=email",
        "--exclude-module=html",
        "--exclude-module=http",
        "--exclude-module=urllib",
        "--exclude-module=xml",
        "--exclude-module=json",
        "--exclude-module=csv",
        "--exclude-module=sqlite3",
        "--exclude-module=dbm",
        "--exclude-module=zipfile",
        "--exclude-module=tarfile",
        "--exclude-module=gzip",
        "--exclude-module=bz2",
        "--exclude-module=lzma",
        "--exclude-module=zlib",
        "--exclude-module=hashlib",
        "--exclude-module=hmac",
        "--exclude-module=secrets",
        "--exclude-module=ssl",
        "--exclude-module=ftplib",
        "--exclude-module=poplib",
        "--exclude-module=imaplib",
        "--exclude-module=smtplib",
        "--exclude-module=socketserver",
        "--exclude-module=wsgiref",
        "--exclude-module=wsgi",
        "--exclude-module=cgi",
        "--exclude-module=cgitb",
        "--exclude-module=webbrowser",
        "--exclude-module=calendar",
        "--exclude-module=datetime",
        "--exclude-module=time",
        "--exclude-module=locale",
        "--exclude-module=gettext",
        "--exclude-module=codecs",
        "--exclude-module=encodings",
        "--exclude-module=unicodedata",
        "--exclude-module=stringprep",
        "--exclude-module=readline",
        "--exclude-module=rlcompleter",
        "--exclude-module=cmd",
        "--exclude-module=shlex",
        "--exclude-module=configparser",
        "--exclude-module=netrc",
        "--exclude-module=xdrlib",
        "--exclude-module=plistlib",
        "--exclude-module=uu",
        "--exclude-module=binascii",
        "--exclude-module=base64",
        "--exclude-module=binhex",
        "--exclude-module=quopri",
        "--exclude-module=uu",
        "--exclude-module=encodings",
        
        # Include only essential data files
        "--add-data=config.json;.",
        
        # Essential hidden imports only
        "--hidden-import=selenium.webdriver.chrome",
        "--hidden-import=selenium.webdriver.chrome.options",
        "--hidden-import=selenium.webdriver.common.by",
        "--hidden-import=selenium.webdriver.support.ui",
        "--hidden-import=selenium.webdriver.support.expected_conditions",
        "--hidden-import=requests.adapters",
        "--hidden-import=requests.auth",
        "--hidden-import=PIL.Image",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        
        # Main script
        "steam_tiermaker_gui.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Optimized executable built successfully!")
        
        # Check if executable was created
        exe_path = Path("dist/SteamToTierMaker.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Optimized executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Compare with original size estimate
            original_size = 70  # Estimated original size
            savings = original_size - size_mb
            savings_percent = (savings / original_size) * 100
            
            print(f"💾 Size reduction: {savings:.1f} MB ({savings_percent:.1f}% smaller)")
            
            print("\n🎉 Optimized build completed successfully!")
            print(f"📁 Single executable file: {exe_path.absolute()}")
            print("\n📝 Instructions:")
            print("1. The optimized executable is in the 'dist' folder")
            print("2. Copy SteamToTierMaker.exe to any location you want")
            print("3. Make sure Chrome browser is installed on the target machine")
            print("4. Run SteamToTierMaker.exe directly")
            print("5. The app will create config.json automatically on first run")
            
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def main():
    """Main build function."""
    print("🚀 Steam to TierMaker - Optimized Executable Builder")
    print("=" * 60)
    print("This build excludes unnecessary modules to reduce file size")
    print()
    
    # Check if we're in the right directory
    required_files = [
        "steam_tiermaker_gui.py",
        "steam_image_scraper.py", 
        "tiermaker_uploader.py",
        "config.json"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please run this script from the project root directory")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Build optimized executable
    if build_optimized_executable():
        print("\n✅ Optimized build process completed successfully!")
        return True
    else:
        print("\n❌ Optimized build process failed!")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
