# test_interrupt_handler.py
from interrupt_handler import InterruptHandler
import asyncio

# Create the handler
handler = InterruptHandler()

async def simulate_agent():
    user_inputs = [
        ("speaking", "yeah"),           # should ignore
        ("silent", "yeah"),             # should respond
        ("speaking", "yeah stop"),      # should interrupt
        ("silent", "ok let's go"),      # should respond
        ("speaking", "uh-huh hmm"),     # should ignore
        ("speaking", "yeah wait now"),  # should interrupt
    ]

    for state, text in user_inputs:
        print(f"\nAgent state: {state} | User says: '{text}'")
        handler.set_agent_state(state)
        action = handler.process_user_input(text)
        print("Action:", action)
        await asyncio.sleep(0.5)  # simulate small delay between inputs

if __name__ == "__main__":
    asyncio.run(simulate_agent())

