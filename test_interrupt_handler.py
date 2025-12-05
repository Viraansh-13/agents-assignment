# tests/test_interrupt_handler.py
import asyncio
import pytest
from interrupt_handler import InterruptHandler

class MockSession:
    def __init__(self):
        self._listeners = {}
        self.interrupted = False

    def on(self, event_name, cb):
        self._listeners.setdefault(event_name, []).append(cb)

    def emit(self, event_name, ev=None):
        for cb in self._listeners.get(event_name, []):
            cb(ev)

    def interrupt(self):
        self.interrupted = True

class TransEv:
    def __init__(self, transcript, is_final=False):
        self.transcript = transcript
        self.is_final = is_final

@pytest.mark.asyncio
async def test_ignore_backchannel_no_interrupt():
    session = MockSession()
    handler = InterruptHandler(decision_timeout=0.05, interrupt_fn=None)
    handler.attach_to_session(session)

    # agent starts speaking
    session.emit("agent_started_speaking")
    # user starts speaking
    session.emit("user_started_speaking")
    # partial arrives: backchannel "yeah"
    session.emit("user_input_transcribed", TransEv("yeah", is_final=False))
    # wait for timeout to clear pending
    await asyncio.sleep(0.06)
    assert not session.interrupted

@pytest.mark.asyncio
async def test_interrupt_on_stop():
    session = MockSession()
    handler = InterruptHandler(decision_timeout=0.2)
    handler.attach_to_session(session)

    session.emit("agent_started_speaking")
    session.emit("user_started_speaking")
    # immediate interrupt token
    session.emit("user_input_transcribed", TransEv("stop", is_final=False))
    # slight wait for handler to process
    await asyncio.sleep(0.01)
    assert session.interrupted
