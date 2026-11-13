"""CLI for agent-tool-permission-capability-token."""
import sys
import argparse
from .token import MacaroonMint

def main():
    parser = argparse.ArgumentParser(description="Agent Tool Permission Capability Token CLI")
    parser.add_argument("--demo", action="store_true", help="Run capability token minting and attenuation demo")
    args = parser.parse_args()

    if args.demo:
        mint = MacaroonMint()
        token = mint.mint("tok_101", "query_database", ["max_rows <= 100", "env == staging"])
        print(f"[+] Minted token: id={token.token_id}, tool={token.tool}, caveats={token.caveats}")
        ok, err = mint.verify(token, "query_database", {"max_rows": 50, "env": "staging"})
        print(f"[+] Verified in staging with 50 rows: {ok}")
        bad, bad_err = mint.verify(token, "query_database", {"max_rows": 500, "env": "staging"})
        print(f"[!] Verified with 500 rows: ok={bad}, error='{bad_err}'")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
