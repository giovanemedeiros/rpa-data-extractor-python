"""
Browser manager and factory using Playwright Sync API.
Provides context management, viewport settings, and graceful teardown.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page

load_dotenv()

class BrowserManager:
    # Manages the lifecycle and configuration of the Playwright Chromium browser.

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, headless: Optional[bool] = None) -> None:
        if headless is not None:
            self.headless = headless
        else:
            self.headless = os.getenv("HEADLESS", "true").strip().lower() in ("true", "1")

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start(self) -> Page:
        # Starts Playwright, launches Chromium, and configures context and page.
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(viewport={'width': 1920, 'height': 1080}, user_agent=self.DEFAULT_USER_AGENT)
        self._page = self._context.new_page()
        self._page.set_default_timeout(30000)
        return self._page

    def close(self) -> None:
        # Gracefully closes page, context, browser, and playwright instances.
        if self._page:
            self._page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def __enter__(self) -> Page:
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
