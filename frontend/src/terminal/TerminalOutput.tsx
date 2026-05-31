import { useEditor } from '../context/VideoEditorContext.tsx'

export default function TerminalOutput() {
  const { logs } = useEditor()

  const typeColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-400'
      case 'warn': return 'text-yellow-500'
      case 'error': return 'text-red-500'
      case 'system': return 'text-cyan-400'
      default: return 'text-terminal-dim'
    }
  }

  return (
    <div className="h-40 bg-black border-t border-terminal-border p-3 font-mono text-xs overflow-y-auto shrink-0">
      <div className="text-terminal-dim mb-1">$ ~/clipos/terminal.log</div>
      {logs.map((log, i) => (
        <div key={i} className="leading-5">
          <span className="text-terminal-dim">{log.timestamp}</span>{' '}
          <span className={typeColor(log.type)}>❯</span>{' '}
          <span className="text-terminal-text">{log.message}</span>
        </div>
      ))}
      <div className="inline-flex items-center gap-1">
        <span className="text-terminal-dim">[READY]</span>
        <span className="text-neon">❯</span>
        <span className="w-2 h-4 bg-neon motion-safe:animate-pulse" />
      </div>
    </div>
  )
}
