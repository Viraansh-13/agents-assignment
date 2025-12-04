import asyncio
import logging
import sys
import time
from collections import deque
from collections.abc import AsyncGenerator, AsyncIterator
from pathlib import Path
from typing import Optional, Union

import numpy as np
import sounddevice as sd
import whisper

from interrupt_handler import InterruptHandler
from stt_whisper import transcribe_audio  # your helper for Whisper transcription

# Global interrupt handler
handler = InterruptHandler()

from livekit import rtc
from livekit.agents import utils
from livekit.agents.types import TOPIC_TRANSCRIPTION
from livekit.agents.voice.avatar import (
    AudioSegmentEnd,
    AvatarOptions,
    AvatarRunner,
    DataStreamAudioReceiver,
    VideoGenerator,
)

sys.path.insert(0, str(Path(__file__).parent))
from wave_viz import WaveformVisualizer

logger = logging.getLogger("avatar-example")


class AudioWaveGenerator(VideoGenerator):
    def __init__(self, options: AvatarOptions):
        self._options = options
        self._audio_queue = asyncio.Queue[Union[rtc.AudioFrame, AudioSegmentEnd]]()
        self._audio_resampler: Optional[rtc.AudioResampler] = None

        self._canvas = np.zeros((options.video_height, options.video_width, 4), dtype=np.uint8)
        self._canvas.fill(255)
        self._wave_visualizer = WaveformVisualizer(sample_rate=options.audio_sample_rate)

        self._audio_bstream = utils.audio.AudioByteStream(
            sample_rate=options.audio_sample_rate,
            num_channels=options.audio_channels,
            samples_per_channel=options.audio_sample_rate // options.video_fps,
        )
        self._frame_ts: deque[float] = deque(maxlen=options.video_fps)

    async def push_audio(self, frame: rtc.AudioFrame | AudioSegmentEnd) -> None:
        await self._audio_queue.put(frame)

    def clear_buffer(self) -> None:
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        self._audio_bstream.flush()

    def __aiter__(self) -> AsyncIterator[rtc.VideoFrame | rtc.AudioFrame | AudioSegmentEnd]:
        return self._video_generation_impl()

    async def _video_generation_impl(self) -> AsyncGenerator[rtc.VideoFrame | rtc.AudioFrame | AudioSegmentEnd, None]:
        while True:
            try:
                frame = await asyncio.wait_for(
                    self._audio_queue.get(), timeout=0.5 / self._options.video_fps
                )
                self._audio_queue.task_done()
            except asyncio.TimeoutError:
                yield self._generate_frame(None)
                self._frame_ts.append(time.time())
                continue

            audio_frames: list[rtc.AudioFrame] = []

            if isinstance(frame, rtc.AudioFrame):
                handler.set_agent_state("speaking")  # speaking state

                if not self._audio_resampler and (
                    frame.sample_rate != self._options.audio_sample_rate
                    or frame.num_channels != self._options.audio_channels
                ):
                    self._audio_resampler = rtc.AudioResampler(
                        input_rate=frame.sample_rate,
                        output_rate=self._options.audio_sample_rate,
                        num_channels=self._options.audio_channels,
                    )

                if self._audio_resampler:
                    for f in self._audio_resampler.push(frame):
                        audio_frames += self._audio_bstream.push(f.data)
                else:
                    audio_frames += self._audio_bstream.push(frame.data)
            else:
                if self._audio_resampler:
                    for f in self._audio_resampler.flush():
                        audio_frames += self._audio_bstream.push(f.data)
                audio_frames += self._audio_bstream.flush()

            for audio_frame in audio_frames:
                video_frame = self._generate_frame(audio_frame)
                yield video_frame
                yield audio_frame
                self._frame_ts.append(time.time())

            if isinstance(frame, AudioSegmentEnd):
                handler.set_agent_state("silent")
                yield AudioSegmentEnd()

    def _generate_frame(self, audio_frame: rtc.AudioFrame | None) -> rtc.VideoFrame:
        canvas = self._canvas.copy()
        if audio_frame is None:
            audio_data = np.zeros((1, self._options.audio_channels))
        else:
            audio_data = np.frombuffer(audio_frame.data, dtype=np.int16).reshape(-1, audio_frame.num_channels)
        self._wave_visualizer.draw(canvas, audio_samples=audio_data, fps=self._get_fps())
        return rtc.VideoFrame(width=canvas.shape[1], height=canvas.shape[0],
                              type=rtc.VideoBufferType.RGBA, data=canvas.tobytes())

    def _get_fps(self) -> float | None:
        if len(self._frame_ts) < 2:
            return None
        return (len(self._frame_ts) - 1) / (self._frame_ts[-1] - self._frame_ts[0])


@utils.log_exceptions(logger=logger)
async def main(api_url: str, api_token: str):
    room = rtc.Room()
    await room.connect(api_url, api_token)

    # STT callback
    async def on_transcription_received(reader: rtc.TextStreamReader, participant_identity: str):
        async for audio_chunk in reader:  # real-time audio chunks
            user_text = await transcribe_audio(audio_chunk)  # use Whisper
            action = handler.process_user_input(user_text)

            if action == "ignore":
                continue
            elif action == "interrupt":
                await runner.stop()
            elif action == "respond":
                await runner.speak(user_text)

    room.register_text_stream_handler(TOPIC_TRANSCRIPTION, on_transcription_received)

    should_stop = asyncio.Event()

    @room.on("participant_disconnected")
    def _on_participant_disconnected(participant: rtc.RemoteParticipant):
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_AGENT:
            logging.info(f"Agent {participant.identity} disconnected, stopping worker")
            should_stop.set()

    @room.on("disconnected")
    def _on_disconnected():
        logging.info("Room disconnected, stopping worker")
        should_stop.set()

    avatar_options = AvatarOptions(video_width=1280, video_height=720, video_fps=30,
                                   audio_sample_rate=24000, audio_channels=1)
    video_gen = AudioWaveGenerator(avatar_options)
    global runner
    runner = AvatarRunner(room, audio_recv=DataStreamAudioReceiver(room), video_gen=video_gen, options=avatar_options)
    try:
        await runner.start()
        tasks = [asyncio.create_task(runner.wait_for_complete()),
                 asyncio.create_task(should_stop.wait())]
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        await utils.aio.cancel_and_wait(*tasks)
        await runner.aclose()
        await room.disconnect()
        logger.info("avatar runner stopped")


if __name__ == "__main__":
    import os
    from livekit.agents.cli.log import setup_logging

    setup_logging("DEBUG", devmode=True, console=True)

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_token = os.getenv("LIVEKIT_TOKEN")
    assert livekit_url and livekit_token, "LIVEKIT_URL and LIVEKIT_TOKEN must be set"

    asyncio.run(main(livekit_url, livekit_token))

