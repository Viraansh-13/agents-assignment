# agent_impl.py
import logging
from livekit.agents import Agent
from livekit.agents.llm import function_tool
from livekit.agents import RunContext

logger = logging.getLogger("agent_impl")


class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "Your name is Kelly. You would interact with users via voice. "
                "with that in mind keep your responses concise and to the point. "
                "do not use emojis, asterisks, markdown, or other special characters in your responses. "
                "You are curious and friendly, and have a sense of humor. "
                "you will speak english to the user"
            )
        )

    async def on_enter(self):
        self.session.generate_reply()

    @function_tool
    async def lookup_weather(self, context: RunContext, location: str, latitude: str, longitude: str):
        logger.info(f"Looking up weather for {location}")
        return "sunny with a temperature of 70 degrees."
