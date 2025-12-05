# session_entry.py
"""Creates the agent server entrypoint and wires the InterruptHandler to the session."""

import logging

from livekit.agents import AgentServer, AgentSession, JobContext, metrics, MetricsCollectedEvent, room_io
from livekit.agents import cli
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .agent_impl import MyAgent
from .interrupt_handler import InterruptHandler
from .prewarm import prewarm
from .config import get_decision_timeout

logger = logging.getLogger("session_entry")
server = AgentServer()
server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

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

    # attach metrics logging (same as original)
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # create and attach the interrupt handler
    handler = InterruptHandler(decision_timeout=get_decision_timeout())
    handler.attach_to_session(session)

    # start the session with your agent
    await session.start(
        agent=MyAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # optional: noise_cancellation=...
            )
        ),
    )

    # After session end: detach handler (best-effort)
    handler.detach()


if __name__ == "__main__":
    cli.run_app(server)
