from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import asyncio
from browser import setup_browser, click_button, analyze_dom, highlight_elements_on_page

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
            # Explicitly ensure browser is visible with a good window size
            browser_instance = await setup_browser(headless=False)
            # Set a larger window size for better visibility
            page = await browser_instance.page()
            await page.set_viewport_size({"width": 1280, "height": 800})
        
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

@mcp.tool()
async def highlight_page_elements() -> str:
    """
    Highlight interactive elements on the current page with visual indicators.
    
    Returns:
        Status message
    """
    global browser_instance
    
    try:
        if browser_instance is None:
            return "Browser not initialized. Please navigate to a page first."
        
        result = await highlight_elements_on_page(browser_instance)
        
        if result["status"] == "success":
            return "Successfully highlighted interactive elements on the page. You should now see visual indicators around buttons and links."
        else:
            return f"Error: {result['message']}"
    except Exception as e:
        return f"Error highlighting elements: {str(e)}"

@mcp.prompt()
def help_prompt() -> str:
    """Create a helpful prompt for users"""
    return """
    This MCP server can control a web browser to analyze and interact with web pages.
    
    Available tools:
    - navigate_to_page: Navigate to a specific URL
    - click_browser_button: Click a button on the current page
    - get_page_elements: Analyze the current page and list all clickable elements
    - highlight_page_elements: Highlight interactive elements on the current page with visual indicators
    
    Example usage:
    1. "Navigate to https://www.rayon.design/"
    2. "Highlight all interactive elements on the page"
    3. "List all clickable elements on the current page"
    4. "Click the button that says 'New Project'"
    """

if __name__ == "__main__":
    # Run the MCP server
    mcp.run() 