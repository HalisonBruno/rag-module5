export default function MetricsPanel({ metrics }) {
  const { total, byProvider, avgTime, sources } = metrics

  const cards = [
    { label: 'Total Queries', value: total, icon: '💬', color: 'acid' },
    { label: 'Avg Response Time', value: `${avgTime}ms`, icon: '⚡', color: 'amber' },
    { label: 'Providers Used', value: Object.keys(byProvider).length, icon: '🧠', color: 'purple' },
    { label: 'Sources Indexed', value: sources.length, icon: '📄', color: 'blue' },
  ]

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-ink-100 text-xl font-semibold mb-1">Metrics</h1>
        <p className="text-ink-500 text-sm mono mb-6">Session statistics</p>

        {/* Stat cards */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          {cards.map((card, i) => (
            <div
              key={i}
              className="bg-ink-800 border border-ink-700 rounded-2xl p-5 fade-up"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-2xl">{card.icon}</span>
              </div>
              <p className="text-3xl font-bold text-ink-100 mono mb-1">{card.value}</p>
              <p className="text-ink-500 text-xs">{card.label}</p>
            </div>
          ))}
        </div>

        {/* Provider breakdown */}
        {Object.keys(byProvider).length > 0 && (
          <div className="bg-ink-800 border border-ink-700 rounded-2xl p-5 mb-4 fade-up">
            <h2 className="text-ink-200 text-sm font-semibold mb-4">Queries by Provider</h2>
            <div className="space-y-3">
              {Object.entries(byProvider).map(([provider, count]) => {
                const pct = total > 0 ? Math.round((count / total) * 100) : 0
                return (
                  <div key={provider}>
                    <div className="flex justify-between text-xs mono mb-1">
                      <span className="text-ink-300">{provider}</span>
                      <span className="text-acid">{count} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 bg-ink-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-acid rounded-full transition-all duration-700"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Sources */}
        {sources.length > 0 && (
          <div className="bg-ink-800 border border-ink-700 rounded-2xl p-5 fade-up">
            <h2 className="text-ink-200 text-sm font-semibold mb-4">Document Sources</h2>
            <div className="space-y-2">
              {sources.map(src => (
                <div key={src} className="flex items-center gap-2 text-sm">
                  <span className="text-acid">📄</span>
                  <span className="text-ink-300 mono text-xs">{src}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {total === 0 && (
          <div className="text-center py-16">
            <p className="text-ink-500 text-sm">No data yet — start chatting to see metrics</p>
          </div>
        )}
      </div>
    </div>
  )
}
