import type { DropStatus } from "../types";

interface UserActionCardProps {
  status: DropStatus;
  userId: string;
  onBuy: () => void;
  onPay: (holdId: number) => void;
  loading: boolean;
  errorMessage: string | null;
}

function formatCountdown(seconds: number): string {
  // Clamp to 0 to prevent flashing negative seconds if polling lags behind server expiry
  const safe = Math.max(0, seconds);
  const m = Math.floor(safe / 60);
  const s = safe % 60;
  return `${m}:${s < 10 ? "0" : ""}${s}`;
}

export function UserActionCard({
  status,
  userId,
  onBuy,
  onPay,
  loading,
  errorMessage,
}: UserActionCardProps) {
  const { active_hold, waitlist_position, purchased_count, available_pairs } =
    status;

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex items-center justify-between border-b border-zinc-100 pb-3.5 dark:border-zinc-800/80">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Current Shopper
          </span>
          <h2 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
            {userId}
          </h2>
        </div>
        <div className="text-right">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Purchased
          </span>
          <div className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
            {purchased_count} / 2 pairs
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-4 rounded-lg bg-red-50 p-3 text-xs text-red-700 dark:bg-red-950/50 dark:text-red-300">
          {errorMessage}
        </div>
      )}

      {active_hold ? (
        <div className="mt-4 space-y-3.5">
          <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 dark:border-amber-900/40 dark:bg-amber-950/20">
            <div className="flex items-center justify-between">
              <div>
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/60 dark:text-amber-200">
                  Hold Reserved
                </span>
                <h3 className="mt-1 text-base font-bold text-zinc-900 dark:text-zinc-100">
                  Sneaker Pair #{active_hold.pair_number}
                </h3>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-medium uppercase text-zinc-500">
                  Hold Countdown
                </span>
                <div
                  className={`text-2xl font-black tabular-nums tracking-tight ${
                    active_hold.remaining_seconds < 60
                      ? "animate-pulse text-red-600 dark:text-red-400"
                      : "text-amber-600 dark:text-amber-400"
                  }`}
                >
                  {formatCountdown(active_hold.remaining_seconds)}
                </div>
              </div>
            </div>

            <p className="mt-2 text-xs text-zinc-600 dark:text-zinc-400">
              Complete your payment before the timer expires, or this pair will
              be returned to stock.
            </p>
          </div>

          <div>
            {active_hold.payment_status === "PENDING" ? (
              <div className="flex items-center justify-center gap-2 rounded-xl border border-zinc-200 bg-zinc-50 py-3 text-xs font-medium text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
                <span className="inline-block h-2 w-2 animate-ping rounded-full bg-amber-500" />
                Payment processing... simulating payment gateway webhook
                settlement
              </div>
            ) : (
              <button
                onClick={() => onPay(active_hold.hold_id)}
                disabled={loading || active_hold.remaining_seconds <= 0}
                className="w-full rounded-xl bg-zinc-900 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
              >
                {loading ? "Initiating Payment..." : "Pay for Pair Now"}
              </button>
            )}
          </div>
        </div>
      ) : waitlist_position !== null ? (
        <div className="mt-4 rounded-xl border border-sky-200 bg-sky-50/70 p-4 dark:border-sky-900/40 dark:bg-sky-950/20">
          <div className="flex items-center justify-between">
            <div>
              <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-medium text-sky-800 dark:bg-sky-900/60 dark:text-sky-200">
                In Waiting Line
              </span>
              <h3 className="mt-1 text-base font-bold text-zinc-900 dark:text-zinc-100">
                Position #{waitlist_position}
              </h3>
            </div>
            <div className="text-right text-xs font-semibold text-sky-600 dark:text-sky-400">
              Queue Place: #{waitlist_position}
            </div>
          </div>
          <p className="mt-2 text-xs text-zinc-600 dark:text-zinc-400">
            Stock is currently held. When someone's hold runs out, you will
            automatically get that pair with your own 5 minutes.
          </p>
        </div>
      ) : purchased_count >= 2 ? (
        <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-center dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">
            Maximum Limit Reached
          </p>
          <p className="mt-1 text-xs text-zinc-500">
            You have already purchased the maximum allowed 2 pairs.
          </p>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          <div className="text-xs text-zinc-500">
            {available_pairs > 0
              ? "Pairs are available! Click Buy to hold one pair for 5 minutes."
              : "All pairs are held or sold. Click below to join the waiting line."}
          </div>
          <button
            onClick={onBuy}
            disabled={loading}
            className={`w-full rounded-xl py-3 text-sm font-semibold text-white shadow-sm transition disabled:opacity-50 ${
              available_pairs > 0
                ? "bg-emerald-600 hover:bg-emerald-500"
                : "bg-sky-600 hover:bg-sky-500"
            }`}
          >
            {loading
              ? "Processing..."
              : available_pairs > 0
                ? "Buy Now (Reserve Pair)"
                : "Join Waiting Line"}
          </button>
        </div>
      )}
    </div>
  );
}
