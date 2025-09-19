#!/usr/bin/env python3
"""
Main Entry Point for Steam to TierMaker Workflow

This script provides the complete workflow for crawling Steam library images
and uploading them to TierMaker.com for creating tier lists.

Usage:
    python main.py                           # Use config.json for Steam URL
    python main.py "steam_url_here"          # Use specific Steam URL
    python main.py --help                    # Show help message

Author: AI Assistant
License: MIT
"""

import sys
import argparse
import logging
from tiermaker_uploader import TierMakerUploader
from steam_image_scraper import SteamImageScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def crawl_and_upload(steam_url: str = None, config_file: str = "config.json"):
    """
    Complete workflow: crawl Steam images and upload to TierMaker.
    
    Args:
        steam_url: Steam library URL (if None, uses config file)
        config_file: Path to config file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Starting complete crawl+upload process...")
    
    # Step 1: Crawl Steam images
    logger.info("Step 1: Crawling Steam images...")
    scraper = SteamImageScraper(config_file)
    
    # Override URL if provided
    if steam_url:
        scraper.url = steam_url
        scraper.config['steam_library_url'] = steam_url
    
    try:
        scraper.scrape_images()
        logger.info("✅ Steam image crawling completed!")
    except Exception as e:
        logger.error(f"❌ Steam crawling failed with error: {e}")
        return False
    finally:
        # Close the scraper's browser
        scraper.close()
    
    # Step 2: Upload to TierMaker
    logger.info("Step 2: Uploading to TierMaker...")
    uploader = TierMakerUploader()
    
    try:
        success = uploader.upload_images_to_tiermaker()
        if success:
            logger.info("Crawl+Upload complete!")
            logger.info("Your browser is now open on TierMaker with all images uploaded.")
            logger.info("You can now create your tier list!")
            return True
        else:
            logger.error("❌ TierMaker upload failed")
            return False
    except Exception as e:
        logger.error(f"❌ Upload process failed: {e}")
        return False
    # Note: We don't close the uploader's browser - it stays open for user interaction


def main():
    try:
        success = crawl_and_upload()
        
        if success:
            logger.info("Process completed successfully.")
        else:
            logger.error("Process failed. Check the logs above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
