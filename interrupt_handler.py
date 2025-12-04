class InterruptHandler:
    def __init__(self, ignore_words=None, interrupt_words=None):
        self.ignore_words = ignore_words or ['yeah', 'ok', 'hmm', 'right', 'uh-huh']
        self.interrupt_words = interrupt_words or ['wait', 'stop', 'no', 'pause']
        self.agent_state = "silent"  # or "speaking"

    def set_agent_state(self, state):
        assert state in ["speaking", "silent"]
        self.agent_state = state

    def should_interrupt(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            if any(word in words for word in self.interrupt_words):
                return True
            return False
        else:
            return False

    def is_ignore_word(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            return all(word in self.ignore_words for word in words)
        return False

    def process_user_input(self, user_text):
        if self.should_interrupt(user_text):
            print("Interrupting agent!")
            return "interrupt"
        elif self.is_ignore_word(user_text):
            print("Ignoring filler while speaking")
            return "ignore"
        else:
            print("Processing user input normally")
            return "respond"

class InterruptHandler:
    def __init__(self, ignore_words=None, interrupt_words=None):
        self.ignore_words = ignore_words or ['yeah', 'ok', 'hmm', 'right', 'uh-huh']
        self.interrupt_words = interrupt_words or ['wait', 'stop', 'no', 'pause']
        self.agent_state = "silent"  # or "speaking"

    def set_agent_state(self, state):
        assert state in ["speaking", "silent"]
        self.agent_state = state

    def should_interrupt(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            if any(word in words for word in self.interrupt_words):
                return True
            return False
        else:
            return False

    def is_ignore_word(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            return all(word in self.ignore_words for word in words)
        return False

class InterruptHandler:
    def __init__(self, ignore_words=None, interrupt_words=None):
        self.ignore_words = ignore_words or ['yeah', 'ok', 'hmm', 'right', 'uh-huh']
        self.interrupt_words = interrupt_words or ['wait', 'stop', 'no', 'pause']
        self.agent_state = "silent"  # or "speaking"

    def set_agent_state(self, state):
        assert state in ["speaking", "silent"]
        self.agent_state = state

    def should_interrupt(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            if any(word in words for word in self.interrupt_words):
                return True
            return False
        else:
            return False

    def is_ignore_word(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            return all(word in self.ignore_words for word in words)
        return False

class InterruptHandler:
    def __init__(self, ignore_words=None, interrupt_words=None):
        self.ignore_words = ignore_words or ['yeah', 'ok', 'hmm', 'right', 'uh-huh']
        self.interrupt_words = interrupt_words or ['wait', 'stop', 'no', 'pause']
        self.agent_state = "silent"  # or "speaking"

    def set_agent_state(self, state):
        assert state in ["speaking", "silent"]
        self.agent_state = state

    def should_interrupt(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            if any(word in words for word in self.interrupt_words):
                return True
            return False
        else:
            return False

    def is_ignore_word(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            return all(word in self.ignore_words for word in words)
        return False
class InterruptHandler:
    def __init__(self, ignore_words=None, interrupt_words=None):
        self.ignore_words = ignore_words or ['yeah', 'ok', 'hmm', 'right', 'uh-huh']
        self.interrupt_words = interrupt_words or ['wait', 'stop', 'no', 'pause']
        self.agent_state = "silent"  # or "speaking"
    def set_agent_state(self, state):
        assert state in ["speaking", "silent"]
        self.agent_state = state
        
    def should_interrupt(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            if any(word in words for word in self.interrupt_words):
                return True
            return False
        else:
            return False

    def is_ignore_word(self, user_text):
        words = user_text.lower().split()
        if self.agent_state == "speaking":
            return all(word in self.ignore_words for word in words)
        return False



    def process_user_input(self, user_text):
        if self.should_interrupt(user_text):
            print("Interrupting agent!")
            return "interrupt"
        elif self.is_ignore_word(user_text):
            print("Ignoring filler while speaking")
            return "ignore"
        else:
            print("Processing user input normally")
            return "respond"
