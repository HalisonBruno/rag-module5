import { useRef, useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'

function Message({ msg }) {
  const isUser = msg.role === 'user'

  return (
    <div className={`fade-up flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-acid flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-ink-900 text-xs font-bold">AI</span>
        </div>
      )}

      <div className={`max-w-2xl ${isUser ? 'order-first' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? 'bg-ink-700 text-ink-100 rounded-tr-sm'
            : msg.error
              ? 'bg-red-900/30 border border-red-700/50 text-red-300 rounded-tl-sm'
              : 'bg-ink-800 border border-ink-700 text-ink-100 rounded-tl-sm'
        }`}>
          {isUser ? (
            <p>{msg.content}</p>
          ) : (
            <div className="prose-dark">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Meta info for assistant messages */}
        {!isUser && msg.meta && (
          <div className="mt-1.5 flex flex-wrap gap-2">
            <span className="mono text-xs text-ink-500 bg-ink-800 px-2 py-0.5 rounded border border-ink-700">
              {msg.meta.provider} / {msg.meta.model}
            </span>
            <span className="mono text-xs text-ink-500 bg-ink-800 px-2 py-0.5 rounded border border-ink-700">
              {msg.meta.chunks} chunks
            </span>
            <span className="mono text-xs text-ink-500 bg-ink-800 px-2 py-0.5 rounded border border-ink-700">
              {msg.meta.time}ms
            </span>
            {msg.meta.sources?.map(s => (
              <span key={s} className="mono text-xs text-acid/70 bg-acid/10 px-2 py-0.5 rounded border border-acid/20">
                📄 {s}
              </span>
            ))}
            {msg.meta.subQuestions?.length > 1 && (
              <span className="mono text-xs text-amber-rag/70 bg-amber-rag/10 px-2 py-0.5 rounded border border-amber-rag/20">
                🔍 {msg.meta.subQuestions.length} sub-questions
              </span>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-full bg-ink-600 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-ink-200 text-xs font-bold">U</span>
        </div>
      )}
    </div>
  )
}

export default function ChatPanel({ messages, loading, provider, onProviderChange, onSend, sessionId }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function handleSend() {
    if (!input.trim()) return
    onSend(input.trim())
    setInput('')
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-ink-700 bg-ink-800/50">
        <div>
          <h1 className="text-ink-100 text-sm font-semibold">Document Intelligence Chat</h1>
          <p className="text-ink-500 text-xs mono">{sessionId}</p>
        </div>

        {/* Provider toggle */}
        <div className="flex items-center gap-1 bg-ink-800 border border-ink-700 rounded-lg p-1">
          {['claude', 'openai'].map(p => (
            <button
              key={p}
              onClick={() => onProviderChange(p)}
              className={`px-3 py-1 rounded text-xs mono font-medium transition-all ${
                provider === p
                  ? 'bg-acid text-ink-900'
                  : 'text-ink-400 hover:text-ink-200'
              }`}
            >
              {p === 'claude' ? '🧠 Claude' : '⚡ OpenAI'}
            </button>
          ))}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-acid/10 border border-acid/20 flex items-center justify-center mb-4">
              <span className="text-3xl">🔍</span>
            </div>
            <h2 className="text-ink-200 text-lg font-semibold mb-1">Ask your documents</h2>
            <p className="text-ink-500 text-sm max-w-sm">
              This agent searches your knowledge base and answers using AI with full conversation memory.
            </p>
          </div>
        )}

        {messages.map(msg => <Message key={msg.id} msg={msg} />)}

        {loading && (
          <div className="fade-up flex gap-3">
            <div className="w-7 h-7 rounded-full bg-acid flex items-center justify-center flex-shrink-0">
              <span className="text-ink-900 text-xs font-bold">AI</span>
            </div>
            <div className="bg-ink-800 border border-ink-700 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-5">
                <span className="w-1.5 h-1.5 bg-acid rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-acid rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-acid rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-ink-700 bg-ink-800/30">
        <div className="flex gap-3 items-end bg-ink-800 border border-ink-700 rounded-2xl px-4 py-3 focus-within:border-acid/50 transition-colors">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask a question about your documents..."
            rows={1}
            className="flex-1 bg-transparent text-ink-100 placeholder-ink-500 text-sm resize-none outline-none max-h-32"
            style={{ lineHeight: '1.5' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-8 h-8 rounded-xl bg-acid disabled:bg-ink-700 disabled:text-ink-500 text-ink-900 flex items-center justify-center transition-all hover:bg-acid-dim disabled:cursor-not-allowed"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z"/>
            </svg>
          </button>
        </div>
        <p className="text-ink-600 text-xs mono text-center mt-2">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
