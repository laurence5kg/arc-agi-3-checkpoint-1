"""Small adversarial checks for the new response-to-action measurement."""
import unittest
from extract_responses import action_owners,metadata

def action(t,name='ACTION1'):return {'generated_tokens':t,'action':{'id':name}}

class Boundaries(unittest.TestCase):
    def test_analysis_then_batch_then_terminal(self):
        owners,boundary,initial=action_owners([10,20,7,8],[action(0,'RESET'),action(30),action(0),action(7)])
        self.assertEqual(dict(owners),{1:2,2:1});self.assertEqual((boundary,initial),(3,1))
    def test_no_action_is_all_terminal(self):self.assertEqual(action_owners([10,20],[])[1],0)
    def test_partial_completion_charge_rejected(self):
        with self.assertRaises(AssertionError):action_owners([10,20],[action(15)])
    def test_unknown_initial_action_rejected(self):
        with self.assertRaises(AssertionError):action_owners([10],[action(0)])
    def test_missing_response_rejected(self):
        with self.assertRaises(AssertionError):action_owners([10],[action(20)])
    def test_zero_token_response_ambiguous(self):
        with self.assertRaises(AssertionError):action_owners([0,10],[action(10)])
    def test_invented_action_marker_not_used(self):
        self.assertEqual(action_owners([10],[])[0],{})
    def test_count_mismatch_rejected(self):
        with self.assertRaises(AssertionError):metadata('finish_reason: length\ntool_call_count: 1\nraw_tool_calls:\n[]\n[THINKING]\na')

if __name__=='__main__':unittest.main()
