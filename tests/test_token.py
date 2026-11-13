"""Unit tests for agent-tool-permission-capability-token."""
import unittest
from agent_tool_permission_capability_token.token import MacaroonMint

class TestCapabilityToken(unittest.TestCase):
    def setUp(self):
        self.mint = MacaroonMint("test_secret_123")

    def test_mint_and_verify_valid(self):
        tok = self.mint.mint("t1", "shell_exec", ["max_time <= 10"])
        ok, err = self.mint.verify(tok, "shell_exec", {"max_time": 5})
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_tool_mismatch(self):
        tok = self.mint.mint("t2", "read_file")
        ok, err = self.mint.verify(tok, "write_file", {})
        self.assertFalse(ok)
        self.assertIn("Tool mismatch", err)

    def test_tamper_signature_rejection(self):
        tok = self.mint.mint("t3", "api_call", ["env == dev"])
        tok.signature = "deadbeef" * 8
        ok, err = self.mint.verify(tok, "api_call", {"env": "dev"})
        self.assertFalse(ok)
        self.assertIn("tampered", err)

if __name__ == "__main__":
    unittest.main()
