import { useEditor } from '../context/VideoEditorContext.tsx'
import { Scissors, Play } from 'lucide-react'

export default function ClipEditor() {
  const { clipStart, setClipStart, clipEnd, setClipEnd, addLog, video } = useEditor()

  const isValid = clipStart !== clipEnd && clipStart < clipEnd

  const handleApply = () => {
    if (!isValid) return
    addLog({ timestamp: '[INFO]', message: `Clip set: ${clipStart} → ${clipEnd}`, type: 'info' })
    addLog({ timestamp: '[OK]', message: 'Clip range locked', type: 'success' })
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ clip editor</h2>
          <p className="text-terminal-dim text-xs">Set the in & out points for your clip</p>
        </div>

        {/* Time inputs */}
        <div className="flex items-center gap-4 justify-center">
          <TimeInput label="START" value={clipStart} onChange={setClipStart} />
          <div className="flex flex-col items-center gap-1">
            <Scissors className="w-4 h-4 text-neon" />
            <span className="text-[10px] text-terminal-dim">TRIM</span>
          </div>
          <TimeInput label="END" value={clipEnd} onChange={setClipEnd} />
        </div>

        {/* Timeline scrubber */}
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-terminal-dim/60">
            <span>{clipStart}</span>
            <span>{clipEnd}</span>
          </div>
          <div className="relative h-2 bg-terminal-border rounded-full">
            <div
              className="absolute top-0 h-full bg-neon/30 rounded-full"
              style={{ left: '0%', right: '0%' }}
            />
            <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-neon rounded-full left-0 -ml-1.5 shadow-[0_0_6px_#00ff41]" />
            <div className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-neon rounded-full right-0 -mr-1.5 shadow-[0_0_6px_#00ff41]" />
          </div>
        </div>

        {/* Info */}
        <div className="bg-black/50 border border-terminal-border rounded-lg p-3 text-xs space-y-1">
          <div className="flex justify-between">
            <span className="text-terminal-dim">Duration</span>
            <span className="text-terminal-text font-mono">{clipEnd}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-terminal-dim">Source</span>
            <span className="text-terminal-text">{video.name || '—'}</span>
          </div>
        </div>

        <button
          onClick={handleApply}
          disabled={!isValid}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4" />
          $ apply clip range
        </button>
      </div>
    </div>
  )
}

function TimeInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div className="space-y-1">
      <label className="text-[10px] text-terminal-dim block text-center">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="00:00:00"
        className="w-28 bg-black border border-terminal-border rounded px-3 py-2 text-center text-sm text-neon font-mono outline-none focus:border-neon/50 transition-colors"
      />
    </div>
  )
}
