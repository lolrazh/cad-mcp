#!/usr/bin/env python3
import asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from browser import run_browser_agent

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("cad_mcp")

# In-memory storage for search results
search_results = {}

@mcp.tool()
async def find_drawing_methods(shape_name: str, context: Context) -> str:
    """Search rayon.design for CAD drawing methods.
    
    Args:
        shape_name: The shape or object you want to draw
    """
    
    # Create the search task
    task = f"""
0. Start by going to: https://www.rayon.design/
1. Navigate to the CAD drawing interface by clicking on the "New Model" button on the top right
2. Once in the drawing interface, look for the toolbar at the bottom center of the screen (DO NOT USE THE QUICK HELP BUTTONS) - this dock bar contains all the drawing elements and tools
3. Some drawing options may be hidden - look for arrow icons that can be clicked to expand additional drawing options
4. Identify tools and methods that can be used to draw a "{shape_name}"
5. Document the steps needed to draw a "{shape_name}" using the available tools
6. Note any specific parameters or settings required for drawing a "{shape_name}"
7. Return a detailed list of steps to draw a "{shape_name}" including which buttons to click and actions to take
"""
    
    search_results[context.request_id] = f"Search for '{shape_name}' drawing methods in progress. Check back in 30 seconds"

    asyncio.create_task(
        perform_search(context.request_id, shape_name, task, context)
    )    
    
    return f"Search for '{shape_name}' drawing methods started. Please wait for 2 minutes, then you can retrieve results using the resource URI: resource://search_results/{context.request_id}. Use a terminal sleep statement to wait for 2 minutes."

async def perform_search(request_id: str, shape_name: str, task: str, context: Context):
    """Perform the actual search for drawing methods in the background."""
    try:
        step_count = 0
        
        async def step_handler(*args, **kwargs):
            nonlocal step_count
            step_count += 1
            await context.info(f"Step {step_count} completed")
            await context.report_progress(step_count)
        
        result = await run_browser_agent(task=task, on_step=step_handler)
        
        search_results[request_id] = result
    
    except Exception as e:
        # Store the error with the request ID
        search_results[request_id] = f"Error: {str(e)}"
        await context.error(f"Error searching for '{shape_name}' drawing methods: {str(e)}")

@mcp.resource(uri="resource://search_results/{request_id}")
async def get_search_results(request_id: str) -> str:
    """Get the search results for a given request ID.
    
    Args:
        request_id: The ID of the request to get the search results for
    """
    # Check if the results exist
    if request_id not in search_results:
        return f"No search results found for request ID: {request_id}"
    
    # Return the successful search results
    return search_results[request_id]

@mcp.tool()
async def draw_shape(shape_name: str, context: Context) -> str:
    """Draw a shape in rayon.design CAD interface.
    
    Args:
        shape_name: Name of the shape to draw (e.g., square, circle, triangle)
    """
    
    task = f"""
1. Go to https://www.rayon.design/
2. Navigate to the CAD drawing interface by clicking on the "New Model" button on the top right
3. Look for the toolbar at the bottom center of the screen (DO NOT USE THE QUICK HELP BUTTONS) - this dock bar contains all the drawing elements and tools
4. Some drawing options may be hidden - look for arrow icons that can be clicked to expand additional drawing options
5. Identify the tools needed to draw a "{shape_name}"
6. Select the appropriate tool for drawing a "{shape_name}"
7. Draw the "{shape_name}" in the center of the canvas
8. If applicable, adjust the size and properties of the "{shape_name}" to make it clearly visible
9. Save the drawing if possible
"""
    
    # Start the background task for drawing
    asyncio.create_task(
        perform_drawing(shape_name, task, context)
    )
    
    # Return a message immediately
    return f"Drawing of '{shape_name}' started. Your drawing is being processed."

async def perform_drawing(shape_name: str, task: str, context: Context):
    """Perform the actual CAD drawing in the background."""
    try:
        step_count = 0
        
        async def step_handler(*args, **kwargs):
            nonlocal step_count
            step_count += 1
            await context.info(f"Drawing step {step_count} completed")
            await context.report_progress(step_count)
        
        result = await run_browser_agent(task=task, on_step=step_handler)
        
        # Report completion
        await context.info(f"Drawing of '{shape_name}' has been completed successfully!")
        return result
    
    except Exception as e:
        error_msg = f"Error drawing '{shape_name}': {str(e)}"
        await context.error(error_msg)
        return error_msg

if __name__ == "__main__":
    mcp.run(transport='stdio') 