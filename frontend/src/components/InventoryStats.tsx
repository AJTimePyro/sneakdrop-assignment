interface InventoryStatsProps {
  available: number;
  held: number;
  sold: number;
  total: number;
  waitlistCount: number;
}

export function InventoryStats({
  available,
  held,
  sold,
  total,
  waitlistCount,
}: InventoryStatsProps) {
  const stats = [
    {
      label: "Pairs Left",
      value: available,
      subtext: `of ${total} total`,
      color: "text-emerald-600 dark:text-emerald-400",
      bg: "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60",
    },
    {
      label: "On Hold",
      value: held,
      subtext: "reserved 5m",
      color: "text-amber-600 dark:text-amber-400",
      bg: "bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/60",
    },
    {
      label: "Sold",
      value: sold,
      subtext: "confirmed paid",
      color: "text-zinc-700 dark:text-zinc-300",
      bg: "bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800",
    },
    {
      label: "Waiting Line",
      value: waitlistCount,
      subtext: "in queue",
      color: "text-sky-600 dark:text-sky-400",
      bg: "bg-sky-50 dark:bg-sky-950/40 border-sky-200 dark:border-sky-800/60",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`rounded-xl border p-3.5 shadow-sm transition ${stat.bg}`}
        >
          <div className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
            {stat.label}
          </div>
          <div
            className={`mt-1 text-2xl font-bold tracking-tight ${stat.color}`}
          >
            {stat.value}
          </div>
          <div className="mt-0.5 text-[11px] text-zinc-400 dark:text-zinc-500">
            {stat.subtext}
          </div>
        </div>
      ))}
    </div>
  );
}
