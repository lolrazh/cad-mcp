from browser_use import Browser, BrowserConfig
import asyncio
from typing import Dict, Any

async def setup_browser(headless: bool = False) -> Browser:
    """Initialize and return a browser instance."""
    browser_config = BrowserConfig(headless=headless)
    return Browser(browser_config)

async def click_button(
    browser: Browser, 
    selector: str
) -> Dict[str, Any]:
    """
    Click a button in the browser using the provided selector.
    
    Args:
        browser: Browser instance
        selector: CSS selector or text selector for the button
        
    Returns:
        Dictionary with status and message
    """
    try:
        # Check if the button exists
        exists = await browser.is_visible(selector, timeout=3000)
        
        if not exists:
            return {
                "status": "error",
                "message": f"Button with selector '{selector}' not found"
            }
        
        # Click the button
        await browser.click(selector)
        
        return {
            "status": "success",
            "message": f"Successfully clicked button with selector '{selector}'"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clicking button: {str(e)}"
        }

async def analyze_dom(browser: Browser) -> Dict[str, Any]:
    """
    Analyze the DOM and return information about clickable elements.
    
    Args:
        browser: Browser instance
        
    Returns:
        Dictionary with DOM analysis results
    """
    try:
        # Get all buttons
        buttons = await browser.evaluate("""
            () => {
                const allButtons = Array.from(document.querySelectorAll('button'));
                return allButtons.map(button => ({
                    text: button.innerText.trim(),
                    visible: button.offsetParent !== null,
                    disabled: button.disabled,
                    classes: button.className,
                    id: button.id
                }));
            }
        """)
        
        # Get all links
        links = await browser.evaluate("""
            () => {
                const allLinks = Array.from(document.querySelectorAll('a'));
                return allLinks.map(link => ({
                    text: link.innerText.trim(),
                    href: link.href,
                    visible: link.offsetParent !== null,
                    classes: link.className,
                    id: link.id
                }));
            }
        """)
        
        return {
            "status": "success",
            "buttons": buttons,
            "links": links,
            "page_url": await browser.url()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing DOM: {str(e)}"
        } 