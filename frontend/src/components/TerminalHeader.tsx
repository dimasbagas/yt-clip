import { useState, useEffect } from 'react'
import { api } from '../api/client.ts'

export default function TerminalHeader() {
  const [time, setTime] = useState(new Date())
  const [backend, setBackend] = useState<'checking' | 'online' | 'offline'>('checking')

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    let cancelled = false
    const check = () =>
      api.health()
        .then(() => { if (!cancelled) setBackend('online') })
        .catch(() => { if (!cancelled) { setBackend('offline') } })

    check()
    const id = setInterval(check, 5000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  const backendColor = backend === 'online' ? 'text-green-500' : backend === 'offline' ? 'text-red-500' : 'text-yellow-500'
  const backendLabel = backend === 'online' ? 'CONNECTED' : backend === 'offline' ? 'OFFLINE' : 'SCANNING'

  return (
    <header className="h-9 bg-terminal-surface border-b border-terminal-border flex items-center px-4 select-none shrink-0">
      <div className="flex items-center gap-2 text-neon font-semibold tracking-wide text-sm">
        <span className="text-green-500">◆</span>
        <span>CLIPOS</span>
        <span className="text-terminal-dim font-normal">v0.1.0</span>
      </div>

      <div className="flex-1 flex justify-center gap-6 text-xs text-terminal-dim">
        <span className="text-terminal-text">MODE: <span className="text-neon">EDIT</span></span>
        <span>AI: <span className="text-green-500">STANDBY</span></span>
        <span>GPU: <span className="text-yellow-500">NVENC</span></span>
        <span>API: <span className={backendColor}>{backendLabel}</span></span>
      </div>

      <div className="text-xs text-terminal-dim font-mono">
        {time.toLocaleTimeString('en-GB')}
      </div>
    </header>
  )
}
