export default function Sidebar({ sessions, currentSession, onSelectSession, onNewSession, view, onSetView }) {
  return (
    <aside className="w-56 flex-shrink-0 bg-ink-800 border-r border-ink-700 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-ink-700">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-acid flex items-center justify-center">
            <span className="text-ink-900 text-xs font-bold mono">R</span>
          </div>
          <div>
            <p className="text-ink-100 text-sm font-semibold leading-none">RAG Agent</p>
            <p className="text-ink-400 text-xs mono mt-0.5">v5.0</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="p-3 border-b border-ink-700 space-y-1">
        <button
          onClick={() => onSetView('chat')}
          className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 transition-colors ${
            view === 'chat'
              ? 'bg-ink-700 text-acid'
              : 'text-ink-300 hover:bg-ink-700 hover:text-ink-100'
          }`}
        >
          <span>💬</span> Chat
        </button>
        <button
          onClick={() => onSetView('metrics')}
          className={`w-full text-left px-3 py-2 rounded text-sm flex items-center gap-2 transition-colors ${
            view === 'metrics'
              ? 'bg-ink-700 text-acid'
              : 'text-ink-300 hover:bg-ink-700 hover:text-ink-100'
          }`}
        >
          <span>📊</span> Metrics
        </button>
      </nav>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="flex items-center justify-between mb-2">
          <p className="text-ink-400 text-xs mono uppercase tracking-wider">Sessions</p>
          <button
            onClick={onNewSession}
            className="text-acid hover:text-acid-dim text-xs mono font-bold transition-colors"
            title="New session"
          >
            + New
          </button>
        </div>

        {sessions.length === 0 && (
          <p className="text-ink-500 text-xs mono mt-4 text-center">No sessions yet</p>
        )}

        <div className="space-y-1">
          {sessions.map(id => (
            <button
              key={id}
              onClick={() => onSelectSession(id)}
              className={`w-full text-left px-2 py-1.5 rounded text-xs mono truncate transition-colors ${
                id === currentSession
                  ? 'bg-ink-700 text-acid'
                  : 'text-ink-400 hover:bg-ink-700 hover:text-ink-200'
              }`}
            >
              {id === currentSession && <span className="inline-block w-1.5 h-1.5 rounded-full bg-acid mr-1.5 pulse-acid" />}
              {id.replace('session-', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-ink-700">
        <p className="text-ink-500 text-xs mono text-center">
          Module 5 · Memory Agent
        </p>
      </div>
    </aside>
  )
}
