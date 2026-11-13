"""Macaroon-style capability token minting and attenuation."""
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any

class CapabilityToken:
    def __init__(self, token_id: str, tool: str, caveats: List[str], signature: str):
        self.token_id = token_id
        self.tool = tool
        self.caveats = caveats
        self.signature = signature

    def attenuate(self, caveat: str, current_key: bytes) -> "CapabilityToken":
        """Appends a caveat and binds it to the signature chain."""
        new_caveats = list(self.caveats) + [caveat]
        h = hmac.new(current_key, caveat.encode("utf-8"), hashlib.sha256).digest()
        return CapabilityToken(self.token_id, self.tool, new_caveats, h.hex())

class MacaroonMint:
    """Mints and verifies cryptographically attenuated capability tokens."""

    def __init__(self, secret_key: str = "root_master_agent_secret_key_99"):
        self.secret_key = secret_key.encode("utf-8")

    def mint(self, token_id: str, tool: str, initial_caveats: Optional[List[str]] = None) -> CapabilityToken:
        caveats = initial_caveats or []
        sig = hmac.new(self.secret_key, f"{token_id}:{tool}".encode("utf-8"), hashlib.sha256).digest()
        curr_sig = sig
        for c in caveats:
            curr_sig = hmac.new(curr_sig, c.encode("utf-8"), hashlib.sha256).digest()
        return CapabilityToken(token_id, tool, caveats, curr_sig.hex())

    def verify(self, token: CapabilityToken, requested_tool: str, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if token.tool != requested_tool:
            return False, f"Tool mismatch: token is for {token.tool}, requested {requested_tool}"

        # Verify cryptographic chain
        sig = hmac.new(self.secret_key, f"{token.token_id}:{token.tool}".encode("utf-8"), hashlib.sha256).digest()
        curr_sig = sig
        for c in token.caveats:
            curr_sig = hmac.new(curr_sig, c.encode("utf-8"), hashlib.sha256).digest()

        if curr_sig.hex() != token.signature:
            return False, "Invalid cryptographic signature chain (tampered token)"

        # Check caveats against context
        for c in token.caveats:
            if "<=" in c:
                k, v = c.split("<=", 1)
                k = k.strip()
                limit = float(v.strip())
                if k not in context or float(context[k]) > limit:
                    return False, f"Caveat violation: {k} must be <= {limit}"
            elif "==" in c:
                k, v = c.split("==", 1)
                k = k.strip()
                target = v.strip()
                if k not in context or str(context[k]) != target:
                    return False, f"Caveat violation: {k} must be == {target}"

        return True, None
