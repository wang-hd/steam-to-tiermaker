#!/usr/bin/env python3
"""
TierMaker Uploader

A simple script to upload Steam images to TierMaker.com for creating tier lists.
Finds the specific file input element and uploads all images from steam_images folder.

Author: AI Assistant
License: MIT
"""

import os
import time
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TierMakerUploader:
    """Simple class for uploading images to TierMaker.com"""
    
    def __init__(self, images_folder: str = "steam_images"):
        """Initialize the uploader with the images folder path."""
        self.images_folder = images_folder
        self.driver = None
        self.tiermaker_url = "https://tiermaker.com/single-use-tier-list/"
        
    def _setup_driver(self):
        """Setup Chrome WebDriver for TierMaker upload."""
        try:
            options = Options()
            
            # Make browser window visible
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            
            # User agent to avoid bot detection
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Anti-detection measures
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # SSL and network options
            options.add_argument("--ignore-ssl-errors=yes")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-quic")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            # Performance options
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--enable-unsafe-swiftshader")
            
            # Page load strategy - stop loading when DOM is ready
            options.page_load_strategy = 'eager'  # Stop loading when DOM is ready, don't wait for all resources
            
            # Keep browser open options
            options.add_experimental_option("detach", True)  # Keep browser open when script ends
            
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome WebDriver initialized successfully with eager page load strategy")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome WebDriver: {e}")
            logger.error("Make sure you have Chrome installed and chromedriver in your PATH")
            raise
    
    def get_image_files(self) -> List[str]:
        """Get list of all image files in the images folder."""
        if not os.path.exists(self.images_folder):
            logger.error(f"Images folder not found: {self.images_folder}")
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        image_files = []
        
        for filename in os.listdir(self.images_folder):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                filepath = os.path.join(self.images_folder, filename)
                image_files.append(filepath)
        
        logger.info(f"Found {len(image_files)} image files to upload")
        return image_files
    
    def upload_images_to_tiermaker(self) -> bool:
        """Upload all images to TierMaker.com"""
        try:
            # Setup driver
            self._setup_driver()
            
            # Navigate to TierMaker
            logger.info(f"Navigating to: {self.tiermaker_url}")
            self.driver.get(self.tiermaker_url)
            
            # Smart page loading strategy: stop when upload button is detected or after 10 seconds
            logger.info("Waiting for page to load with smart detection...")
            start_time = time.time()
            upload_button_found = False
            
            while time.time() - start_time < 10:  # Maximum 10 seconds
                try:
                    # Check if upload button/input is present
                    upload_elements = self.driver.find_elements(By.ID, "extra-images-input")
                    if not upload_elements:
                        upload_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file'][accept*='image']")
                    
                    if upload_elements:
                        logger.info("✅ Upload button/input detected - stopping page load")
                        upload_button_found = True
                        break
                    
                    # Check every 0.5 seconds
                    time.sleep(0.5)
                    
                except Exception as e:
                    # Continue checking even if there are temporary errors
                    time.sleep(0.5)
                    continue
            
            # Stop page loading if we haven't found the upload button yet
            if not upload_button_found:
                logger.info("⏰ 10 seconds elapsed - stopping page load")
                try:
                    self.driver.execute_script("window.stop();")
                    logger.info("✅ Stopped page loading after timeout")
                except Exception as e:
                    logger.info(f"Could not stop page loading: {e}")
            
            # Wait a moment for any essential elements to stabilize
            time.sleep(1)
            
            # Check if page loaded successfully
            page_title = self.driver.title
            current_url = self.driver.current_url
            logger.info(f"Page loaded - Title: '{page_title}', URL: {current_url}")
            
            # Set orientation to portrait
            logger.info("Setting orientation to portrait...")
            try:
                # Find the orientation picker select element
                orientation_select = self.driver.find_element(By.ID, "orientation-picker")
                
                # Create Select object and select portrait option
                select = Select(orientation_select)
                select.select_by_value("portrait")
                
                logger.info("✅ Orientation set to portrait successfully")
                
            except Exception as e:
                logger.warning(f"Could not set orientation to portrait: {e}")
                logger.info("Continuing with default orientation...")
            
            # Find the specific file input element
            logger.info("Looking for file upload input element...")
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # Look for the specific input element by ID
                file_input = wait.until(
                    EC.presence_of_element_located((By.ID, "extra-images-input"))
                )
                logger.info("✅ Found file input element by ID: extra-images-input")
                
                # Make the hidden input visible and interactable
                self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                self.driver.execute_script("arguments[0].style.visibility = 'visible';", file_input)
                self.driver.execute_script("arguments[0].style.opacity = '1';", file_input)
                
                # Wait a moment for the element to become visible
                time.sleep(2)
                
            except TimeoutException:
                # Fallback: try to find by other attributes
                try:
                    file_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='image']"))
                    )
                    logger.info("✅ Found file input element by CSS selector")
                    
                    # Make the hidden input visible and interactable
                    self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                    self.driver.execute_script("arguments[0].style.visibility = 'visible';", file_input)
                    self.driver.execute_script("arguments[0].style.opacity = '1';", file_input)
                    
                except TimeoutException:
                    logger.error("❌ Could not find file upload input element")
                    logger.error("The page structure may have changed or the page didn't load properly")
                    
                    # Try to find and click on upload-related buttons or areas
                    logger.info("Looking for upload buttons or clickable areas...")
                    try:
                        # Look for buttons with upload-related text
                        upload_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Upload') or contains(text(), 'Choose') or contains(text(), 'Select')]")
                        for btn in upload_buttons:
                            if btn.is_displayed():
                                logger.info(f"Found upload button: {btn.text}")
                                btn.click()
                                time.sleep(2)
                                # Try to find file input again after clicking
                                try:
                                    file_input = self.driver.find_element(By.ID, "extra-images-input")
                                    logger.info("✅ Found file input after clicking upload button")
                                    break
                                except:
                                    continue
                        
                        # If still no file input, try clicking on the action div
                        try:
                            action_div = self.driver.find_element(By.CSS_SELECTOR, "div.action")
                            if action_div.is_displayed():
                                logger.info("Clicking on action div...")
                                action_div.click()
                                time.sleep(2)
                                file_input = self.driver.find_element(By.ID, "extra-images-input")
                                logger.info("✅ Found file input after clicking action div")
                        except:
                            pass
                            
                    except Exception as e:
                        logger.info(f"Could not find upload buttons: {e}")
                    
                    # Debug: Print all input elements on the page
                    try:
                        inputs = self.driver.find_elements(By.TAG_NAME, "input")
                        logger.info(f"Found {len(inputs)} input elements on the page:")
                        for i, inp in enumerate(inputs):
                            try:
                                inp_type = inp.get_attribute("type")
                                inp_id = inp.get_attribute("id")
                                inp_class = inp.get_attribute("class")
                                inp_style = inp.get_attribute("style")
                                logger.info(f"  Input {i+1}: type='{inp_type}', id='{inp_id}', class='{inp_class}', style='{inp_style}'")
                            except:
                                logger.info(f"  Input {i+1}: [could not read attributes]")
                    except Exception as debug_error:
                        logger.error(f"Debug failed: {debug_error}")
                    
                    # Final check if we have a file input
                    try:
                        file_input = self.driver.find_element(By.ID, "extra-images-input")
                        logger.info("✅ Found file input after all attempts")
                    except:
                        logger.error("❌ Still could not find file input element")
                        return False
            
            # Get list of image files
            image_files = self.get_image_files()
            if not image_files:
                logger.error("No image files found to upload")
                return False
            
            # Upload all images
            logger.info(f"Uploading {len(image_files)} images to TierMaker...")
            
            # Convert file paths to absolute paths (required for file upload)
            absolute_paths = [os.path.abspath(img_path) for img_path in image_files]
            
            try:
                # Try to click on the file input first to ensure it's focused
                try:
                    file_input.click()
                    time.sleep(1)
                except:
                    logger.info("Could not click file input directly, trying JavaScript click...")
                    self.driver.execute_script("arguments[0].click();", file_input)
                    time.sleep(1)
                
                # Send all file paths to the input element
                # Use newline separation for multiple files
                file_paths_string = '\n'.join(absolute_paths)
                file_input.send_keys(file_paths_string)
                
                # Wait for upload to process
                time.sleep(5)
                
                logger.info("✅ All images uploaded successfully!")
                logger.info("🎉 TierMaker page is ready for tier list creation!")
                logger.info("Browser will remain open for you to create your tier list.")
                logger.info("Script is exiting - you can now use the browser freely.")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Error during file upload: {e}")
                logger.info("Trying alternative upload method...")
                
                # Try uploading files one by one as fallback
                try:
                    for i, file_path in enumerate(absolute_paths):
                        logger.info(f"Uploading file {i+1}/{len(absolute_paths)}: {os.path.basename(file_path)}")
                        file_input.send_keys(file_path)
                        time.sleep(1)  # Small delay between files
                    
                    logger.info("✅ All images uploaded successfully (one by one)!")
                    logger.info("🎉 TierMaker page is ready for tier list creation!")
                    logger.info("Browser will remain open for you to create your tier list.")
                    logger.info("Script is exiting - you can now use the browser freely.")
                    
                    return True
                    
                except Exception as e2:
                    logger.error(f"❌ Alternative upload method also failed: {e2}")
                    return False
            
        except Exception as e:
            logger.error(f"❌ Error during upload process: {e}")
            return False
    
    def close(self):
        """Close the WebDriver (optional - browser stays open by default)."""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main function to run the uploader."""
    uploader = TierMakerUploader()
    
    try:
        success = uploader.upload_images_to_tiermaker()
        if success:
            logger.info("🎉 Upload completed successfully!")
            logger.info("You can now create your tier list in the browser window.")
            # Don't close the browser automatically - let user decide when to close
        else:
            logger.error("❌ Upload failed. Please check the logs for details.")
            # Only close browser if upload failed
            uploader.close()
    except KeyboardInterrupt:
        logger.info("Uploading interrupted by user")
        uploader.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        uploader.close()


if __name__ == "__main__":
    main()
