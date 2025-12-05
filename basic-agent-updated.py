# basic-agent-updated.py
import logging
from dotenv import load_dotenv

from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    cli,
    metrics,
    room_io,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# local modules (must be in same directory or in PYTHONPATH)
from prewarm import prewarm
from agent_impl import MyAgent
from interrupt_handler import InterruptHandler
from config import get_decision_timeout

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic-agent")

load_dotenv()

# create server and attach prewarm function
server = AgentServer()
server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    # enrich logs with the room name
    ctx.log_context_fields = {"room": ctx.room.name}

    # create the AgentSession (same options as in the modular implementation)
    session = AgentSession(
        stt="deepgram/nova-3",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        resume_false_interruption=True,
        false_interruption_timeout=1.0,
    )

    # metrics collection (usage logging)
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info("Usage summary: %s", summary)

    ctx.add_shutdown_callback(log_usage)

    # instantiate and attach the interrupt handler
    interrupt_handler = InterruptHandler(decision_timeout=get_decision_timeout())
    interrupt_handler.attach_to_session(session)

    # start the session with your agent implementation
    try:
        await session.start(
            agent=MyAgent(),
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    # Uncomment to enable Krisp BVC noise cancellation if desired:
                    # noise_cancellation=noise_cancellation.BVC(),
                )
            ),
        )
    finally:
        # best-effort cleanup: detach handler and flush logs/usage
        try:
            interrupt_handler.detach()
        except Exception:
            logger.exception("Failed to detach interrupt handler cleanly.")
        # log usage one more time in case the shutdown callback didn't run yet
        try:
            await log_usage()
        except Exception:
            logger.exception("Failed to log usage on shutdown.")


if __name__ == "__main__":
    # run the LiveKit agent server entrypoint
    cli.run_app(server)
