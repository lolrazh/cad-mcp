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
                
                // Highlight buttons with a red border for visibility
                allButtons.forEach(button => {
                    const originalBorder = button.style.border;
                    const originalOutline = button.style.outline;
                    
                    button.style.border = '2px solid red';
                    button.style.outline = '2px solid red';
                    
                    // Store original values as data attributes
                    button.dataset.originalBorder = originalBorder;
                    button.dataset.originalOutline = originalOutline;
                });
                
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
                
                // Highlight links with a blue border for visibility
                allLinks.forEach(link => {
                    const originalBorder = link.style.border;
                    const originalOutline = link.style.outline;
                    
                    link.style.border = '2px solid blue';
                    link.style.outline = '2px solid blue';
                    
                    // Store original values as data attributes
                    link.dataset.originalBorder = originalBorder;
                    link.dataset.originalOutline = originalOutline;
                });
                
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

async def highlight_elements_on_page(browser: Browser) -> Dict[str, Any]:
    """
    Highlight all interactive elements on the page with a visible pulsing effect.
    
    Args:
        browser: Browser instance
        
    Returns:
        Dictionary with status information
    """
    try:
        # Add a style tag with keyframe animation for the pulsing effect
        await browser.evaluate("""
            () => {
                // Remove any existing highlight style to avoid duplicates
                const existingStyle = document.getElementById('mcp-highlight-style');
                if (existingStyle) {
                    existingStyle.remove();
                }
                
                // Create a style element for our highlight effects
                const style = document.createElement('style');
                style.id = 'mcp-highlight-style';
                style.innerHTML = `
                    @keyframes mcpPulse {
                        0% { box-shadow: 0 0 0 0px rgba(66, 133, 244, 0.7); }
                        50% { box-shadow: 0 0 0 5px rgba(66, 133, 244, 0.5); }
                        100% { box-shadow: 0 0 0 0px rgba(66, 133, 244, 0.7); }
                    }
                    
                    .mcp-highlight-button {
                        position: relative;
                        border: 2px solid #4285F4 !important;
                        animation: mcpPulse 1.5s infinite !important;
                        z-index: 9999 !important;
                    }
                    
                    .mcp-highlight-link {
                        position: relative;
                        border: 2px solid #0F9D58 !important;
                        animation: mcpPulse 1.5s infinite !important;
                        z-index: 9999 !important;
                    }
                    
                    .mcp-element-label {
                        position: absolute;
                        top: -10px;
                        left: 0;
                        background: #333;
                        color: white;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 12px;
                        white-space: nowrap;
                        z-index: 10000;
                    }
                `;
                document.head.appendChild(style);
                
                // Highlight interactive elements
                const interactiveElements = {
                    buttons: Array.from(document.querySelectorAll('button')),
                    links: Array.from(document.querySelectorAll('a')),
                    inputs: Array.from(document.querySelectorAll('input[type="button"], input[type="submit"]')),
                    clickableElements: Array.from(document.querySelectorAll('[role="button"], [onclick]'))
                };
                
                // Process all buttons
                interactiveElements.buttons.forEach((el, index) => {
                    if (el.offsetParent !== null) { // Only highlight visible elements
                        el.classList.add('mcp-highlight-button');
                        
                        // Add label with button text
                        const label = document.createElement('div');
                        label.className = 'mcp-element-label';
                        label.textContent = 'Button: ' + (el.innerText.trim() || '[No Text]');
                        el.style.position = 'relative';
                        el.appendChild(label);
                    }
                });
                
                // Process all links
                interactiveElements.links.forEach((el, index) => {
                    if (el.offsetParent !== null) { // Only highlight visible elements
                        el.classList.add('mcp-highlight-link');
                        
                        // Add label with link text
                        const label = document.createElement('div');
                        label.className = 'mcp-element-label';
                        label.textContent = 'Link: ' + (el.innerText.trim() || '[No Text]');
                        el.style.position = 'relative';
                        el.appendChild(label);
                    }
                });
                
                // Process other clickable elements
                interactiveElements.clickableElements.forEach((el, index) => {
                    if (el.offsetParent !== null && !el.matches('button, a')) { // Only highlight visible non-button/link elements
                        el.classList.add('mcp-highlight-button');
                        
                        // Add label
                        const label = document.createElement('div');
                        label.className = 'mcp-element-label';
                        label.textContent = 'Clickable: ' + (el.innerText.trim() || '[No Text]');
                        el.style.position = 'relative';
                        el.appendChild(label);
                    }
                });
                
                return {
                    buttonCount: interactiveElements.buttons.length,
                    linkCount: interactiveElements.links.length,
                    clickableCount: interactiveElements.clickableElements.length
                };
            }
        """);
        
        return {
            "status": "success",
            "message": "Elements highlighted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error highlighting elements: {str(e)}"
        } 