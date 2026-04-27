import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import MetricsPanel from './components/MetricsPanel'

export default function App() {
  const [sessionId, setSessionId] = useState(() => `session-${Date.now()}`)
  const [sessions, setSessions] = useState([])
  const [messages, setMessages] = useState([])
  const [metrics, setMetrics] = useState({ total: 0, byProvider: {}, avgTime: 0, sources: [] })
  const [provider, setProvider] = useState('claude')
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState('chat') // 'chat' | 'metrics'

  // load sessions list on mount
  useEffect(() => {
    fetchSessions()
  }, [])

  async function fetchSessions() {
    try {
      const res = await fetch('/api/sessions')
      const data = await res.json()
      setSessions(data.sessions || [])
    } catch {}
  }

  async function fetchSession(id) {
    try {
      const res = await fetch(`/api/session/${id}`)
      const data = await res.json()
      const history = data.history || []
      const msgs = []
      for (let i = 0; i < history.length; i += 2) {
        if (history[i] && history[i + 1]) {
          msgs.push({ role: 'user', content: history[i].content, id: i })
          msgs.push({ role: 'assistant', content: history[i + 1].content, id: i + 1 })
        }
      }
      setMessages(msgs)
      setSessionId(id)
    } catch {}
  }

  async function sendMessage(question) {
    if (!question.trim() || loading) return

    const userMsg = { role: 'user', content: question, id: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId, provider })
      })
      const data = await res.json()

      const assistantMsg = {
        role: 'assistant',
        content: data.answer,
        id: Date.now() + 1,
        meta: {
          provider: data.provider,
          model: data.model,
          chunks: data.chunks_used,
          sources: data.sources_used,
          time: data.response_time_ms,
          subQuestions: data.sub_questions,
        }
      }

      setMessages(prev => [...prev, assistantMsg])

      // update metrics
      setMetrics(prev => {
        const byProvider = { ...prev.byProvider }
        byProvider[data.provider] = (byProvider[data.provider] || 0) + 1
        const total = prev.total + 1
        const avgTime = Math.round((prev.avgTime * prev.total + data.response_time_ms) / total)
        const sources = [...new Set([...prev.sources, ...(data.sources_used || [])])]
        return { total, byProvider, avgTime, sources }
      })

      fetchSessions()
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Error connecting to the agent API. Make sure the server is running on port 8001.',
        id: Date.now() + 1,
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  function newSession() {
    setSessionId(`session-${Date.now()}`)
    setMessages([])
  }

  return (
    <div className="flex h-screen bg-ink-900 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSession={sessionId}
        onSelectSession={fetchSession}
        onNewSession={newSession}
        view={view}
        onSetView={setView}
      />

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {view === 'chat' ? (
          <ChatPanel
            messages={messages}
            loading={loading}
            provider={provider}
            onProviderChange={setProvider}
            onSend={sendMessage}
            sessionId={sessionId}
          />
        ) : (
          <MetricsPanel metrics={metrics} />
        )}
      </main>
    </div>
  )
}
