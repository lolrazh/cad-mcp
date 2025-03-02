from typing import Awaitable, Callable
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import warnings

load_dotenv()

warnings.filterwarnings("ignore")

browser = Browser(
    config=BrowserConfig(
        chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    )
)

llm = ChatAnthropic(model_name="claude-3-5-sonnet-latest")

task_template = """
perform the following task
{task}
"""

async def run_browser_agent(task: str, on_step: Callable[[], Awaitable[None]]):
    """Run the browser-use agent with the specified task."""
    agent = Agent(
        task=task_template.format(task=task),
        browser=browser,
        llm=llm,
        register_new_step_callback=on_step,
        register_done_callback=on_step,
    )

    result = await agent.run()

    await browser.close()
    
    return result.final_result()