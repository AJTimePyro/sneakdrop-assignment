"""Sneakdrop concurrent simulation: verifies no overselling and correct waitlisting.

Usage:
    uv run python simulate.py --mode burst --users 100
    uv run python simulate.py --mode burst --users 100 --pay-ratio 1   # nobody abandons
    uv run python simulate.py --mode realistic --users 50 --stock 20

Exits with status 1 if overselling or request failures are detected.
"""

import argparse
import asyncio
import random
import sys
import time
import uuid
from collections import Counter

import httpx

POLL_INTERVAL = 0.5
SETTLE_TIMEOUT = 150.0

# Non-200 /buy statuses that are expected business outcomes, not errors.
BUY_STATUS_LABELS = {409: "hold_conflict", 400: "max_limit"}
# Outcomes where the user obtained a hold ("pay_failed" = hold, but payment didn't complete).
HOLD_LABELS = ("paid", "abandoned", "pay_failed")
LABELS = (*HOLD_LABELS, "waitlisted", "hold_conflict", "max_limit", "error")

Outcome = tuple[str, str]  # (label, failure detail or "")


async def wait_for_payment(client: httpx.AsyncClient, payment_id: int | str) -> Outcome:
    """Poll until the payment webhook settles as SUCCEEDED/FAILED, or time out."""
    deadline = time.monotonic() + SETTLE_TIMEOUT
    while time.monotonic() < deadline:
        await asyncio.sleep(POLL_INTERVAL)
        check = await client.get(f"/payment/{payment_id}")
        if check.status_code != 200:
            return "pay_failed", f"Check payment {check.status_code}: {check.text}"
        status = check.json().get("status")
        if status == "SUCCEEDED":
            return "paid", ""
        if status == "FAILED":
            return "pay_failed", f"Payment {payment_id} FAILED"
    return "pay_failed", f"Payment {payment_id} unsettled after {SETTLE_TIMEOUT:.0f}s"


async def simulate_user(
    client: httpx.AsyncClient, user_id: str, realistic: bool, pay_ratio: float
) -> Outcome:
    if realistic:
        await asyncio.sleep(random.uniform(0.05, 2.0))
    held = False  # any failure after a hold is granted must still count as a hold
    try:
        buy = await client.post("/buy", json={"user_id": user_id})
        if buy.status_code in BUY_STATUS_LABELS:
            return BUY_STATUS_LABELS[buy.status_code], ""
        if buy.status_code != 200:
            return "error", f"Buy {buy.status_code}: {buy.text}"

        data = buy.json()
        if "position" in data:
            return "waitlisted", ""
        if "hold_id" not in data:
            return "error", f"Unexpected /buy response: {data}"
        held = True

        if random.random() >= pay_ratio:
            return "abandoned", ""
        if realistic:
            await asyncio.sleep(random.uniform(0.2, 1.0))

        pay = await client.post("/pay", json={"hold_id": data["hold_id"]})
        payment_id = pay.json().get("payment_id") if pay.status_code == 200 else None
        if not payment_id:
            return "pay_failed", f"Pay {pay.status_code}: {pay.text}"
        return await wait_for_payment(client, payment_id)
    except (httpx.HTTPError, ValueError) as exc:  # network, timeout, or bad JSON
        return ("pay_failed" if held else "error"), f"{type(exc).__name__}: {exc}"


async def wait_until_healthy(client: httpx.AsyncClient, attempts: int = 4) -> bool:
    for _ in range(attempts):
        try:
            (await client.get("/health")).raise_for_status()
            return True
        except httpx.HTTPError:
            await asyncio.sleep(0.5)
    return False


def report(
    args: argparse.Namespace, counts: Counter, errors: list[str], seconds: float
) -> bool:
    holds = sum(counts[label] for label in HOLD_LABELS)
    print("=" * 44)
    print(f"Duration: {seconds:.2f}s")
    print(f"Holds acquired: {holds}")
    for label in LABELS:
        print(f"  {label:<14}{counts[label]}")
    print("=" * 44)

    # Holds (which include every paid order) must never exceed stock. Assumes the
    # hold TTL is much longer than the run, so no hold expires and gets re-issued.
    oversold = holds > args.stock
    if oversold:
        print(
            f"❌ FAIL: overselling (holds={holds}, paid={counts['paid']}, stock={args.stock})"
        )
    else:
        print(f"✓ PASS: no overselling ({counts['waitlisted']} users waitlisted)")
    if errors:
        print(f"❌ {len(errors)} failed requests, e.g.:")
        for detail in errors[:5]:
            print(f"  • {detail}")
    return not oversold and not errors


async def run(args: argparse.Namespace) -> bool:
    client = httpx.AsyncClient(
        base_url=args.url.rstrip("/"),
        limits=httpx.Limits(max_connections=args.concurrency),
        timeout=httpx.Timeout(15.0, connect=5.0),
    )
    async with client:
        if not await wait_until_healthy(client):
            print(f"❌ Backend not healthy at {args.url}")
            print("   Is it running? e.g. cd backend && uv run fastapi dev")
            return False

        # Scopes user IDs to this run so back-to-back runs don't hit 409/400.
        run_id = uuid.uuid4().hex[:6]
        print(
            f"🚀 {args.mode} | users={args.users} pay={args.pay_ratio:.0%} "
            f"concurrency={args.concurrency} stock={args.stock}"
        )
        users = [
            simulate_user(
                client, f"user_{run_id}_{i}", args.mode == "realistic", args.pay_ratio
            )
            for i in range(1, args.users + 1)
        ]

        counts: Counter[str] = Counter()
        errors: list[str] = []
        live = sys.stdout.isatty()  # carriage-return progress only makes sense on a TTY
        start = time.perf_counter()
        for done, finished in enumerate(asyncio.as_completed(users), 1):
            label, detail = await finished
            counts[label] += 1
            if detail:
                errors.append(detail)
            if live:
                failed = counts["error"] + counts["pay_failed"]
                print(
                    f"\r{done}/{args.users} | paid {counts['paid']} | "
                    f"waitlisted {counts['waitlisted']} | failed {failed}",
                    end="",
                    flush=True,
                )
        seconds = time.perf_counter() - start
    if live:
        print()
    return report(args, counts, errors, seconds)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sneakdrop concurrent traffic simulator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["burst", "realistic"],
        default="burst",
        help="burst: everyone hits /buy at once; realistic: staggered with delays.",
    )
    parser.add_argument("--users", type=int, default=100, help="Simulated users.")
    parser.add_argument(
        "--stock", type=int, default=20, help="Pairs available in the seeded DB."
    )
    parser.add_argument(
        "--pay-ratio",
        type=float,
        default=0.8,
        help="Fraction of hold-holders who pay (1 = nobody abandons).",
    )
    parser.add_argument(
        "--concurrency", type=int, default=50, help="Max open connections."
    )
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL.")
    args = parser.parse_args()

    try:
        sys.exit(0 if asyncio.run(run(args)) else 1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
