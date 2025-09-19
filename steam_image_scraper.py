#!/usr/bin/env python3
"""
Steam Library Image Scraper with Selenium

This script scrapes game images from a Steam library page using Selenium WebDriver
to handle JavaScript-rendered content. It finds all <img> tags under <picture> elements
and downloads the images to a local folder.

Author: AI Assistant
License: MIT
"""

import os
import json
import requests
import time
import re
from typing import List, Dict
import logging
from io import BytesIO
from PIL import Image

# Selenium imports
from selenium import webdriver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SteamImageScraper:
    """Main class for scraping Steam library images using Selenium."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the scraper with configuration."""
        self.config = self._load_config(config_file)
        self.output_folder = self.config['output_folder']
        self.url = self.config['steam_library_url']
        
        # Setup Chrome WebDriver
        self.driver = None
        self._setup_driver()
        
        # Create output folder
        os.makedirs(self.output_folder, exist_ok=True)
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "steam_library_url": "",
            "output_folder": "steam_images",
            "delay_between_downloads": 1.0,
            "scroll_pause": 2,
            "max_scroll_attempts": 10
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}. Using defaults.")
        else:
            logger.info(f"Config file not found. Creating default config at {config_file}")
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        return default_config
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with anti-detection measures."""
        try:
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            # Anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            self.driver = webdriver.Chrome(options=options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome WebDriver: {e}")
            logger.error("Make sure you have Chrome installed and chromedriver in your PATH")
            raise
    
    def _scroll_to_load_all_content(self):
        """Scroll to the bottom of the page to load all lazy-loaded content."""
        logger.info("Scrolling to load all content...")
        
        # Get initial page height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        window_height = self.driver.execute_script("return window.innerHeight")
        current_scroll = 0
        scroll_increment = window_height
        attempts = 0
        max_attempts = self.config.get('max_scroll_attempts', 1000)
        scroll_pause = self.config.get('scroll_pause', 0.1)
        
        while attempts < max_attempts:
            # Scroll to next position
            current_scroll += scroll_increment
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            time.sleep(scroll_pause)
            
            # Check if we've reached the bottom
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if current_scroll >= new_height:
                logger.info("Reached bottom of page")
                break
            
            # Check if new content loaded
            if new_height > last_height:
                logger.info(f"New content loaded, height increased to {new_height}")
                last_height = new_height
            
            attempts += 1
            if attempts % 10 == 0:
                logger.info(f"Scroll attempt {attempts}/{max_attempts}, position: {current_scroll}, height: {new_height}")
        
        # Scroll back to top for consistent starting position
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        logger.info("All content loaded, ready for download process")

    def extract_images(self) -> List[Dict[str, str]]:
        """Extract all image elements from the page, focusing on picture elements."""
        logger.info("Extracting image elements...")
        
        # First, try to find source elements under picture elements
        picture_sources = self.driver.execute_script("""
        const pictureElements = document.querySelectorAll('picture');
        const sources = [];
        
        pictureElements.forEach(picture => {
            // Get the img element first to get the game name
            const img = picture.querySelector('img');
            const gameName = img ? img.getAttribute('alt') || 'no_alt' : 'no_alt';
            
            const firstSource = picture.querySelector('source');
            if (firstSource) {
                const srcset = firstSource.getAttribute('srcset');
                if (srcset) {
                    // Get the first URL from srcset (before any space or comma)
                    const firstUrl = srcset.split(/[\\s,]/)[0];
                    sources.push({
                        src: firstUrl,
                        srcset: srcset,
                        media: firstSource.getAttribute('media') || '',
                        alt: gameName,
                        parent: 'picture_source'
                    });
                } else if (img) {
                    // Use img element as fallback only when source has no srcset
                    sources.push({
                        src: img.getAttribute('src') || img.getAttribute('data-src'),
                        alt: gameName,
                        title: img.getAttribute('title') || '',
                        parent: 'picture_img'
                    });
                }
            } else if (img) {
                // Use img element as fallback only when no source element exists
                sources.push({
                    src: img.getAttribute('src') || img.getAttribute('data-src'),
                    alt: gameName,
                    title: img.getAttribute('title') || '',
                    parent: 'picture_img'
                });
            }
        });
        
        return sources;
        """)
        
        logger.info(f"Found {len(picture_sources)} sources under picture elements")
        
        return picture_sources
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be safe for filesystem."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra spaces and limit length
        filename = re.sub(r'\s+', '_', filename.strip())
        if len(filename) > 100:
            filename = filename[:100]
        return filename
    
    def _check_if_image_exists(self, img_info: Dict[str, str]) -> bool:
        """Check if an image file already exists on disk."""
        src = img_info.get('src', '')
        alt = img_info.get('alt', 'no_alt')
        title = img_info.get('title', '')
        
        # Generate filename (same logic as download_image)
        filename_base = alt if alt != 'no_alt' else title
        if not filename_base:
            url_hash = str(hash(src))[-8:]
            filename_base = f"image_{url_hash}"
        
        filename = self.sanitize_filename(filename_base)
        filepath = os.path.join(self.output_folder, f"{filename}.jpg")
        
        return os.path.exists(filepath)

    def download_image(self, img_info: Dict[str, str]) -> bool:
        """Download a single image."""
        src = img_info.get('src', '')
        alt = img_info.get('alt', 'no_alt')
        title = img_info.get('title', '')
        srcset = img_info.get('srcset', '')
        parent = img_info.get('parent', '')
        
        if not src or (not src.startswith("http") and not src.startswith("https")):
            logger.debug(f"Skipping invalid URL: {src}")
            return False
        
        # Generate filename
        filename_base = alt if alt != 'no_alt' else title
        if not filename_base:
            # Generate filename from URL
            url_hash = str(hash(src))[-8:]
            filename_base = f"image_{url_hash}"
        
        filename = self.sanitize_filename(filename_base)
        filepath = os.path.join(self.output_folder, f"{filename}.jpg")
        
        try:
            logger.info(f"Downloading: {filename} ({parent})")
            logger.info(f"Source: {src}")
            
            if "defaultappheader.png" in src:
                logger.warning(f"⚠️ Image for {filename} is not loading")
                return False
            
            response = requests.get(src, timeout=30)
            response.raise_for_status()
            
            # Convert to RGB and save as JPEG
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image.save(filepath, "JPEG")
            logger.info(f"✅ Saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save {filename}: {e}")
            return False
    
    def scrape_images(self) -> dict:
        """Main method to scrape images from Steam library page.
        
        Returns:
            dict: Dictionary containing download statistics and failed game names
        """
        if not self.url:
            logger.error("No Steam library URL provided in config. Please update config.json")
            return {
                "total_images_found": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "failed_games": [],
                "success": False
            }
        
        try:
            logger.info(f"Navigating to: {self.url}")
            self.driver.get(self.url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if user is logged in by examining body element class
            body_classes = self.driver.execute_script("return document.body.className;")
            
            if "login" in body_classes.lower():
                logger.info("🔐 Steam login required!")
                logger.info("Please log in to Steam in the browser window that opened.")
                logger.info("Waiting for login to complete...")
                
                # Wait for login to complete by checking page reload
                max_wait_time = 300  # 5 minutes
                wait_interval = 3  # Check every 2 seconds
                waited_time = 0
                
                while waited_time < max_wait_time:
                    time.sleep(wait_interval)
                    waited_time += wait_interval
                    
                    # Check if page has been reloaded/changed
                    current_body_classes = self.driver.execute_script("return document.body.className;")
                    
                    # If no longer on login page, break
                    if "login" not in current_body_classes.lower():
                        logger.info("✅ Login detected! Starting download process...")
                        break
                
                # Final check
                body_classes = self.driver.execute_script("return document.body.className;")
                if "login" in body_classes.lower():
                    logger.error("❌ Login timeout. Please make sure you are logged in.")
                    logger.error("You may need to:")
                    logger.error("1. Complete the login process in the browser")
                    logger.error("2. Navigate to your Steam library page manually")
                    logger.error("3. Make sure your profile is set to PUBLIC")
                    return
            
            # First, scroll to load all content and get total picture count
            logger.info("Loading all content by scrolling to bottom...")
            self._scroll_to_load_all_content()
            
            # Get all picture elements after content is loaded
            all_images = self.extract_images()
            total_images = len(all_images)
            logger.info(f"Found {total_images} total images to download")
            
            if total_images == 0:
                logger.warning("No images found to download")
                return {
                    "total_images_found": 0,
                    "successful_downloads": 0,
                    "failed_downloads": 0,
                    "failed_games": [],
                    "success": False
                }
            
            # Get page height for scroll calculations
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            logger.info(f"Page height: {page_height}px")
            
            # Download images while scrolling proportionally
            successful_downloads = 0
            failed_downloads = 0
            failed_images = []  # Store failed images for retry
            
            logger.info("Starting scroll-while-downloading process...")
            logger.info(f"Total images to download: {total_images}")
            
            for i, img_info in enumerate(all_images):
                # Calculate download progress percentage
                download_progress = (i + 1) / total_images
                percentage = download_progress * 100
                
                # Calculate corresponding scroll position based on progress
                target_scroll = int(page_height * download_progress)
                
                # Scroll to the calculated position
                self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")
                time.sleep(0.1)  # Brief pause for scroll
                
                # Download the image with detailed progress logging
                game_name = img_info.get('alt', 'unknown')
                logger.info(f"[{i + 1}/{total_images}] ({percentage:.1f}%) Downloading: {game_name}")
                
                if self.download_image(img_info):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                    failed_images.append((i, img_info))  # Store index and image info for retry
                    logger.error(f"❌ Failed to download: {game_name}")
                
                # Log progress summary every 5 images for more frequent updates
                if (i + 1) % 5 == 0 or i == total_images - 1:
                    logger.info(f"📊 Progress Update: {i + 1}/{total_images} ({percentage:.1f}%) - "
                              f"Successful: {successful_downloads}, Failed: {failed_downloads}")
                
                # Small delay between downloads
                time.sleep(self.config['delay_between_downloads'])
            
            # Retry failed downloads
            if failed_images:
                logger.info(f"\n🔄 Retrying {len(failed_images)} failed downloads...")
                retry_successful = 0
                retry_failed = 0
                
                for retry_index, (original_index, img_info) in enumerate(failed_images):
                    # Calculate scroll position for this specific image
                    download_progress = (original_index + 1) / total_images
                    target_scroll = int(page_height * download_progress)
                    
                    # Scroll to the position
                    self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")
                    time.sleep(0.1)
                    
                    game_name = img_info.get('alt', 'unknown')
                    retry_progress = (retry_index + 1) / len(failed_images) * 100
                    logger.info(f"[RETRY {retry_index + 1}/{len(failed_images)}] ({retry_progress:.1f}%) Retrying: {game_name}")
                    
                    if self.download_image(img_info):
                        retry_successful += 1
                        successful_downloads += 1
                        failed_downloads -= 1
                        logger.info(f"✅ Retry successful: {game_name}")
                    else:
                        retry_failed += 1
                        logger.error(f"❌ Retry failed: {game_name}")
                    
                    time.sleep(self.config['delay_between_downloads'])
                
                logger.info(f"🔄 Retry complete: {retry_successful} recovered, {retry_failed} still failed")
            
            # Print final failure summary
            if failed_downloads > 0:
                logger.warning(f"⚠️ {failed_downloads} images failed to download:")
                for original_index, img_info in failed_images:
                    if not self._check_if_image_exists(img_info):
                        logger.warning(f"[{original_index + 1}] {img_info.get('alt', 'unknown')}")
            else:
                logger.info("✅ All images downloaded successfully!")
            
            # Create summary
            logger.info(f"\n✅ Download complete! {successful_downloads} successful, {failed_downloads} failed")
            
            # Collect failed game names
            failed_games = []
            if failed_images:
                for original_index, img_info in failed_images:
                    if not self._check_if_image_exists(img_info):
                        failed_games.append(img_info.get('alt', 'unknown'))
            
            # Create return statistics
            result = {
                "total_images_found": total_images,
                "successful_downloads": successful_downloads,
                "failed_downloads": failed_downloads,
                "failed_games": failed_games,
                "success": True
            }
            
            # Save summary to file
            summary = {
                "total_images_found": total_images,
                "successful_downloads": successful_downloads,
                "failed_downloads": failed_downloads,
                "failed_games": failed_games,
                "source_url": self.url,
                "output_directory": os.path.abspath(self.output_folder),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            summary_file = os.path.join(self.output_folder, "download_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Summary saved to: {summary_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return {
                "total_images_found": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "failed_games": [],
                "success": False,
                "error": str(e)
            }
        finally:
            self.close()
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")


def main():
    """Main function to run the scraper."""
    scraper = SteamImageScraper()
    
    try:
        scraper.scrape_images()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        scraper.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        scraper.close()


if __name__ == "__main__":
    main()