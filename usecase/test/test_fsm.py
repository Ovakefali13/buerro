
import unittest
from .. import StateMachine

class TestFSM(unittest.TestCase):

    def test_fsm_validate_string(self):
        def _first_word(text):
            return text.split(None, 1)

        def start_transition(data):
            word, remainder = _first_word(data['text'])
            if word == "Python":
                next_state = "is_state"
                return next_state, {'text': remainder}
            return "error_state", None

        def is_state_transition(data):
            word, remainder = _first_word(data['text'])
            if word == "is":
                return "adj_state", {'text': remainder}
            return "error_state", None

        def adj_transition(data):
            if data['text'] == "great.":
                return "pos_state", None
            if data['text'] == 'shit.':
                return "neg_state", None
            return "error_state", None

        str_to_val = "Python is great."

        m = StateMachine()
        m.add_state("start", start_transition)
        m.add_state("is_state", is_state_transition)
        m.add_state("adj_state", adj_transition)
        m.add_state("pos_state", None, end_state=True)
        m.add_state("neg_state", None, end_state=True)
        m.add_state("error_state", None, end_state=True)
        m.set_start("start")

        data = m.advance({'text':str_to_val})
        data = m.advance(data)
        data = m.advance(data)

        self.assertEqual(m.get_state(), "pos_state".upper())

        str_to_inval = "Python is shit."
        m.reset()
        data = m.advance({'text':str_to_inval})
        data = m.advance(data)
        data = m.advance(data)

        self.assertEqual(m.get_state(), "neg_state".upper())



