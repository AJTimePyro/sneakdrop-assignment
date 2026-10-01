export function RulesCard() {
  const rules = [
    {
      num: 1,
      text: "Clicking Buy holds 1 pair for 5 minutes. If unpaid, it returns to stock.",
    },
    {
      num: 2,
      text: "1 pair held at a time, maximum of 2 pairs purchased per user.",
    },
    {
      num: 3,
      text: "If stock is 0, join the waiting line. Expired holds automatically pass to the next user in line.",
    },
    {
      num: 4,
      text: "Simulated asynchronous payment webhooks with realistic delay.",
    },
    {
      num: 5,
      text: "Live real-time drop status: pairs left, hold countdown, and waiting line rank.",
    },
  ];

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
        Drop Rules & Specifications
      </h3>
      <div className="mt-3 space-y-2">
        {rules.map((rule) => (
          <div
            key={rule.num}
            className="flex items-start gap-2.5 text-xs text-zinc-600 dark:text-zinc-400"
          >
            <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-[10px] font-bold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              {rule.num}
            </span>
            <span>{rule.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
