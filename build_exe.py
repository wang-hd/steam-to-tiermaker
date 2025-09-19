#!/usr/bin/env python3
"""
Build Script for Steam to TierMaker GUI Executable

This script creates a standalone executable using PyInstaller.

Usage:
    python build_exe.py

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
    
    # Check other dependencies
    required_packages = ["selenium", "requests", "PIL"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} not found. Please install requirements:")
            print(f"   pip install -r requirements_gui.txt")
            return False
    
    return True


def create_spec_file():
    """Create PyInstaller spec file for better control."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['steam_tiermaker_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('steam_image_scraper.py', '.'),
        ('tiermaker_uploader.py', '.'),
    ],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'requests',
        'PIL',
        'PIL.Image',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'threading',
        'queue',
        'time',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SteamToTierMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    onefile=True,  # Create a single executable file
)
'''
    
    with open('steam_tiermaker.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build directory")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned dist directory")
    
    # Build using spec file
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "steam_tiermaker.spec"
        ])
        print("✅ Executable built successfully!")
        
        # Check if executable was created
        exe_path = Path("dist/SteamToTierMaker.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            print("\n🎉 Build completed successfully!")
            print(f"📁 Single executable file: {exe_path.absolute()}")
            print("\n📝 Instructions:")
            print("1. The single executable file is in the 'dist' folder")
            print("2. Copy SteamToTierMaker.exe to any location you want")
            print("3. Make sure Chrome browser is installed on the target machine")
            print("4. Run SteamToTierMaker.exe directly - no installation needed!")
            print("5. The app will create config.json automatically on first run")
            
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True


def main():
    """Main build function."""
    print("🚀 Steam to TierMaker - Executable Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    required_files = [
        "steam_tiermaker_gui.py",
        "steam_image_scraper.py", 
        "tiermaker_uploader.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please run this script from the project root directory")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        print("\n✅ Build process completed successfully!")
        return True
    else:
        print("\n❌ Build process failed!")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
