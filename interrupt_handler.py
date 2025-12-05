# interrupt_handler.py
"""Interrupt handler module.

Provides InterruptHandler: attach to a livekit AgentSession to implement the
"ignore backchannels while agent speaks, interrupt on commands" logic.
"""

import asyncio
import logging
from typing import Optional, Callable

from .config import get_interrupt_words, get_ignore_words, get_decision_timeout
from .tokenizer import tokenize_text

logger = logging.getLogger("interrupt_handler")


class InterruptHandler:
    """
    Handles VAD + STT events and decides whether to call session.interrupt().

    Usage:
        handler = InterruptHandler()
        handler.attach_to_session(session)

    Requirements:
        - `session.on(event_name)` must register callback functions for:
            "agent_started_speaking", "agent_stopped_speaking",
            "user_started_speaking", "user_input_transcribed"
        - the "user_input_transcribed" callback will receive an event object
          with attributes:
              .transcript (str)  -- partial or final transcript
              .is_final (bool)   -- whether it's final
    """

    def __init__(
        self,
        interrupt_words=None,
        ignore_words=None,
        decision_timeout: Optional[float] = None,
        interrupt_fn: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            interrupt_words: set of tokens that always cause immediate interrupt
            ignore_words: set of filler tokens that should be ignored while speaking
            decision_timeout: seconds to wait for decisive partials before treating as false interruption
            interrupt_fn: optional callable to execute instead of `session.interrupt()` (useful for tests)
        """
        self.interrupt_words = interrupt_words or get_interrupt_words()
        self.ignore_words = ignore_words or get_ignore_words()
        self.decision_timeout = decision_timeout if decision_timeout is not None else get_decision_timeout()
        self._interrupt_fn = interrupt_fn  # override for testing or custom behavior

        # internal state
        self._agent_speaking = False
        self._pending = None  # dict: {"task": asyncio.Task, "accumulated_text": str}
        self._session = None

    # --------------------------
    # Public API
    # --------------------------
    def attach_to_session(self, session):
        """Attach event listeners to a session object with `.on(event, callback)`."""
        self._session = session
        session.on("agent_started_speaking", self._on_agent_started)
        session.on("agent_stopped_speaking", self._on_agent_stopped)
        session.on("user_started_speaking", self._on_user_started)
        session.on("user_input_transcribed", self._on_user_transcribed)
        logger.debug("InterruptHandler attached to session.")

    def detach(self):
        """Detach - best-effort (depending on session API)."""
        # Many SDKs don't expose an 'off' API in the same style; if available, remove listeners here.
        self._session = None
        self._clear_pending()

    # --------------------------
    # Event handlers (internal)
    # --------------------------
    def _on_agent_started(self, ev):
        logger.debug("InterruptHandler: agent started speaking")
        self._agent_speaking = True
        self._clear_pending()

    def _on_agent_stopped(self, ev):
        logger.debug("InterruptHandler: agent stopped speaking")
        self._agent_speaking = False
        self._clear_pending()

    def _on_user_started(self, ev):
        logger.debug("InterruptHandler: user started speaking event")
        if not self._agent_speaking:
            # normal flow - agent is not speaking
            return

        if self._pending is None:
            # create the pending decision task
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._pending_timeout_task())
            self._pending = {"task": task, "accumulated_text": ""}
            logger.debug("InterruptHandler: started pending decision task")

    def _on_user_transcribed(self, ev):
        """Handle partial/final transcripts.

        `ev` expected to have: .transcript (str), .is_final (bool)
        """
        if not self._agent_speaking or self._pending is None:
            # not in a pending decision state -> ignore here
            return

        text = (getattr(ev, "transcript", "") or "").strip()
        is_final = getattr(ev, "is_final", False)
        logger.debug("InterruptHandler: received transcript (final=%s) '%s'", is_final, text)

        # accumulate
        self._pending["accumulated_text"] += " " + text

        tokens = tokenize_text(self._pending["accumulated_text"])
        logger.debug("InterruptHandler: tokens so far: %s", tokens)

        # 1) immediate interrupt if any interrupt word present
        for t in tokens:
            if t in self.interrupt_words:
                logger.info("InterruptHandler: detected interrupt token '%s' -> interrupting", t)
                self._clear_pending()
                self._call_interrupt()
                return

        # 2) if any non-ignore token -> treat as user intent -> interrupt
        if any((t not in self.ignore_words) for t in tokens):
            logger.info("InterruptHandler: detected non-ignore token(s) -> interrupting (tokens=%s)", tokens)
            self._clear_pending()
            self._call_interrupt()
            return

        # otherwise, only filler tokens seen; continue waiting for timeout or more partials
        logger.debug("InterruptHandler: only ignore tokens so far. waiting for more partials or timeout.")

    # --------------------------
    # Internal helpers
    # --------------------------
    def _call_interrupt(self):
        """Invoke the session interrupt (or the override callback)."""
        try:
            if self._interrupt_fn:
                self._interrupt_fn()
            elif self._session:
                # call session.interrupt() provided by LiveKit Agents SDK
                self._session.interrupt()
            else:
                logger.warning("InterruptHandler: no session and no interrupt_fn configured")
        except Exception as exc:
            logger.exception("InterruptHandler: failed to interrupt: %s", exc)

    async def _pending_timeout_task(self):
        """Wait for the configured timeout. If no decision is reached, clear pending (false interruption)."""
        try:
            await asyncio.sleep(self.decision_timeout)
        except asyncio.CancelledError:
            # decision already made -> nothing to do
            return

        logger.debug("InterruptHandler: decision timeout elapsed -> treating as false interruption")
        self._pending = None

    def _clear_pending(self):
        if self._pending:
            task = self._pending.get("task")
            if task and not task.done():
                task.cancel()
            self._pending = None
