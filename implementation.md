# Setting Up a Basic CAD-MCP Server

This document outlines how to set up a minimal MCP server that can analyze DOM elements and click buttons in a browser. We'll focus on the core MCP server setup first before adding more complex functionality.

## Project Structure

```
cad-mcp/
├── server.py           # Main MCP server implementation
├── browser.py          # Browser automation functions
├── .env                # Environment variables
├── .env.example        # Template for environment variables
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation
└── .cursor/            # Cursor IDE configuration
    └── mcp.json        # MCP server configuration for Cursor
```

## 1. Setup Dependencies

First, let's create the `requirements.txt` file with the necessary dependencies:

```
browser-use>=0.5.0
langchain-anthropic>=0.1.0
python-dotenv>=1.0.0
fastmcp>=0.8.0
mcp[cli]>=0.12.0
playwright>=1.40.0
```

Install these dependencies in your virtual environment:

```bash
pip install -r requirements.txt
```

## 2. Environment Configuration

Create a `.env` file based on `.env.example`:

```
# .env.example
ANTHROPIC_API_KEY=your_anthropic_key_here
LOG_LEVEL=INFO
BROWSER_USE_LOGGING_LEVEL=INFO
LANGCHAIN_TRACING_V2=false
LANGCHAIN_VERBOSE=false
```

## 3. Browser Automation Module

Create a `browser.py` file with basic browser interaction functions:

```python
# browser.py
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
```

## 4. MCP Server Implementation

Create the main `server.py` file:

```python
# server.py
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import asyncio
from browser import setup_browser, click_button, analyze_dom

# Load environment variables
load_dotenv()

# Create the MCP server
mcp = FastMCP("CAD-MCP")

# Global browser instance to reuse
browser_instance = None

@mcp.tool()
async def navigate_to_page(url: str) -> str:
    """
    Navigate to a specific URL.
    
    Args:
        url: The URL to navigate to
        
    Returns:
        Status message
    """
    global browser_instance
    
    try:
        if browser_instance is None:
            browser_instance = await setup_browser(headless=False)
        
        await browser_instance.goto(url)
        
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Error navigating to {url}: {str(e)}"

@mcp.tool()
async def click_browser_button(selector: str) -> str:
    """
    Click a button in the browser using the provided selector.
    
    Args:
        selector: CSS selector or text selector for the button (e.g. "button:text('Login')" or "#submit-button")
        
    Returns:
        Status message
    """
    global browser_instance
    
    try:
        if browser_instance is None:
            return "Browser not initialized. Please navigate to a page first."
        
        result = await click_button(browser_instance, selector)
        
        if result["status"] == "success":
            return result["message"]
        else:
            return f"Error: {result['message']}"
    except Exception as e:
        return f"Error clicking button: {str(e)}"

@mcp.tool()
async def get_page_elements() -> str:
    """
    Analyze the current page and list all clickable elements.
    
    Returns:
        Information about buttons and links on the page
    """
    global browser_instance
    
    try:
        if browser_instance is None:
            return "Browser not initialized. Please navigate to a page first."
        
        result = await analyze_dom(browser_instance)
        
        if result["status"] == "success":
            # Format the results
            output = f"Current URL: {result['page_url']}\n\n"
            
            output += "BUTTONS:\n"
            for i, button in enumerate(result["buttons"]):
                if button["visible"]:
                    status = "disabled" if button["disabled"] else "enabled"
                    output += f"{i+1}. \"{button['text']}\" ({status})\n"
            
            output += "\nLINKS:\n"
            for i, link in enumerate(result["links"]):
                if link["visible"]:
                    output += f"{i+1}. \"{link['text']}\" -> {link['href']}\n"
            
            return output
        else:
            return f"Error: {result['message']}"
    except Exception as e:
        return f"Error analyzing page: {str(e)}"

@mcp.prompt()
def help_prompt() -> str:
    """Create a helpful prompt for users"""
    return """
    This MCP server can control a web browser to analyze and interact with web pages.
    
    Available tools:
    - navigate_to_page: Navigate to a specific URL
    - click_browser_button: Click a button on the current page
    - get_page_elements: Analyze the current page and list all clickable elements
    
    Example usage:
    1. "Navigate to https://www.rayon.design/"
    2. "List all clickable elements on the current page"
    3. "Click the button that says 'New Project'"
    """

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
```

## 5. MCP Configuration for Cursor

Create a `.cursor` directory and add an `mcp.json` file:

```json
{
  "name": "CAD-MCP",
  "description": "A simple MCP server for browser automation and CAD drawing",
  "path": "/d:/Projects/2025/cad-mcp/server.py",
  "command": "python server.py"
}
```

Make sure to update the `path` to match your actual project location.

## 6. Running the Server

To run the MCP server:

```bash
python server.py
```

Or, use the FastMCP CLI:

```bash
fastmcp run server.py
```

## 7. Using the MCP Server with Claude

Once your server is running, Claude can use it to:

1. **Navigate to a webpage**: `navigate_to_page("https://www.rayon.design/")`
2. **Analyze the page**: `get_page_elements()` to see what buttons are available
3. **Click a button**: `click_browser_button("button:text('New Project')")` to click a specific button

## 8. Example Interaction

Here's an example interaction with Claude:

**User**: "Navigate to Rayon.design and tell me what buttons are available"

**Claude**: 
*Claude would use the MCP server to navigate to the site and list available buttons*

**User**: "Click the button that says 'New Project'"

**Claude**:
*Claude would use the MCP server to click the button and report success or failure*