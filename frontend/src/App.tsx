import { useEffect, useState } from "react";
import { buySneaker, fetchStatus, paySneaker, resetDrop } from "./api";
import { InventoryStats } from "./components/InventoryStats";
import { Navbar } from "./components/Navbar";
import { RulesCard } from "./components/RulesCard";
import { UserActionCard } from "./components/UserActionCard";
import type { DropStatus } from "./types";

export default function App() {
  const [userId, setUserId] = useState(
    () => localStorage.getItem("sneakdrop_user_id") || "user_1",
  );
  const [status, setStatus] = useState<DropStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(true);

  const activeUserId = userId.trim() || "user_1";

  useEffect(() => {
    localStorage.setItem("sneakdrop_user_id", activeUserId);
    let mounted = true;

    const poll = async () => {
      try {
        const data = await fetchStatus(activeUserId);
        if (mounted) {
          setStatus(data);
          setIsBackendConnected(true);
        }
      } catch {
        if (mounted) setIsBackendConnected(false);
      }
    };

    poll();
    const interval = setInterval(poll, 1000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [activeUserId]);

  const executeAction = async (action: () => Promise<unknown>) => {
    try {
      setLoading(true);
      setError(null);
      await action();
      const updated = await fetchStatus(activeUserId);
      setStatus(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-100 text-zinc-900 antialiased dark:bg-zinc-900 dark:text-zinc-100">
      <Navbar
        userId={userId}
        onUserChange={setUserId}
        onReset={() => executeAction(resetDrop)}
        loading={loading}
      />

      <main className="mx-auto max-w-3xl space-y-5 px-4 py-8">
        {!isBackendConnected && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-700 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-300">
            Cannot reach backend API at{" "}
            <code className="font-mono font-semibold">
              http://localhost:8000
            </code>
            . Ensure the FastAPI server is running with{" "}
            <code className="font-mono font-semibold">
              uv run fastapi dev main.py
            </code>
            .
          </div>
        )}

        {status && (
          <>
            <InventoryStats
              available={status.available_pairs}
              held={status.held_pairs}
              sold={status.sold_pairs}
              total={status.total_pairs}
              waitlistCount={status.waitlist_count}
            />

            <UserActionCard
              status={status}
              userId={activeUserId}
              onBuy={() => executeAction(() => buySneaker(activeUserId))}
              onPay={(holdId) => executeAction(() => paySneaker(holdId))}
              loading={loading}
              errorMessage={error}
            />

            <RulesCard />
          </>
        )}
      </main>
    </div>
  );
}
