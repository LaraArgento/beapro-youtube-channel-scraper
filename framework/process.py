import logging
from .datasources import *  # test
from .exceptions import BusinessException, InterruptException, SystemException
from .state import STATE
# from selenium.webdriver.common.by import By
# Import de Web Bot
from botcity.web import WebBot, Browser, By

logger = logging.getLogger(__name__)


'''
process.py
    Add the steps to your automation process here.
'''


def process_item(item):
    """
    Runs the steps of the automation process for each item and checks if the process has received an interruption request from the BotCity Orchestrator.
    """
    STATE.raise_for_interrupt_requested()

    logger.info(f"Item processing has started: {item}.")
    bot = STATE.webbot

    channel = item.get("channel")
    # Starts the browser
    bot.browse(f"https://www.youtube.com/@{channel}")

    bot.wait(500)
    
    # Find the <title> element and check its text    
    title_element = bot.page_title()
    if title_element == "404 Not Found":
        raise BusinessException(f"The YouTube channel '{channel}' was not found.")
    
    element = bot.find_element(
        selector='//yt-content-metadata-view-model[@class="yt-page-header-view-model__page-header-content-metadata yt-content-metadata-view-model yt-content-metadata-view-model--inline yt-content-metadata-view-model--medium-text"]',
        by=By.XPATH)

    lines = [line for line in element.text.strip().split('\n')
             if line.strip() != '•']
    channel_name = lines[0].strip('@')
    subscribers = lines[1]
    videos = lines[2]

    result_message = f"Channel name: {channel_name} | Number of subscribers: {subscribers} | Number of videos: {videos}"
    return result_message
