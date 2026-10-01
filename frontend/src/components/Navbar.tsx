interface NavbarProps {
  userId: string;
  onUserChange: (newUserId: string) => void;
  onReset: () => void;
  loading: boolean;
}

export function Navbar({
  userId,
  onUserChange,
  onReset,
  loading,
}: NavbarProps) {
  const handleRandomUser = () => {
    const randomId = `user_${Math.floor(1000 + Math.random() * 9000)}`;
    onUserChange(randomId);
  };

  return (
    <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 text-sm font-black text-white dark:bg-zinc-100 dark:text-zinc-900">
            S
          </span>
          <div>
            <h1 className="text-base font-bold tracking-tight text-zinc-900 dark:text-white">
              SNEAKDROP
            </h1>
            <p className="text-xs text-zinc-500">20 Limited Edition Pairs</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-lg border border-zinc-200 bg-zinc-50 px-2.5 py-1 dark:border-zinc-800 dark:bg-zinc-900">
            <span className="text-xs text-zinc-500">User:</span>
            <input
              type="text"
              value={userId}
              onChange={(e) => onUserChange(e.target.value)}
              className="w-24 bg-transparent text-xs font-semibold text-zinc-800 focus:outline-none dark:text-zinc-200"
              title="Click to edit User ID"
            />
            <button
              onClick={handleRandomUser}
              className="rounded px-1.5 py-0.5 text-[11px] font-medium text-zinc-600 hover:bg-zinc-200 dark:text-zinc-400 dark:hover:bg-zinc-800"
              title="Switch to random user"
            >
              🎲 Switch
            </button>
          </div>

          <button
            onClick={onReset}
            disabled={loading}
            className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 shadow-sm transition hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
            title="Reset database to 20 available pairs"
          >
            {loading ? "Working..." : "Reset Drop"}
          </button>
        </div>
      </div>
    </header>
  );
}
