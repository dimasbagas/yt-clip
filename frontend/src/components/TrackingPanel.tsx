import { useEditor } from '../context/VideoEditorContext.tsx'

const modes = [
  { id: 'podcast', icon: '🎙', label: 'Podcast', desc: 'Dual speaker, smooth switching' },
  { id: 'interview', icon: '🎤', label: 'Interview', desc: 'Q&A style, focus on active speaker' },
  { id: 'gaming', icon: '🎮', label: 'Gaming', desc: 'Facecam tracking, stable crop' },
  { id: 'streamer', icon: '📡', label: 'Streamer', desc: 'Single speaker, center-locked' },
  { id: 'cinematic', icon: '🎬', label: 'Cinematic', desc: 'Slow pans, wide-to-tight' },
]

export default function TrackingPanel() {
  const { trackingMode, setTrackingMode, addLog } = useEditor()

  const handleApply = () => {
    addLog({ timestamp: '[INFO]', message: `Camera mode: ${trackingMode}`, type: 'info' })
    addLog({ timestamp: '[OK]', message: 'Speaker tracking configured', type: 'success' })
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="w-full max-w-lg space-y-5">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ camera tracking</h2>
          <p className="text-terminal-dim text-xs">AI-powered speaker detection & auto-focus</p>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {modes.map((mode) => {
            const active = trackingMode === mode.id
            return (
              <button
                key={mode.id}
                onClick={() => setTrackingMode(mode.id)}
                className={`text-left p-3 rounded-lg border transition-all ${
                  active
                    ? 'border-neon bg-neon/5'
                    : 'border-terminal-border hover:border-terminal-dim bg-black/30'
                }`}
              >
                <div className="text-lg mb-1">{mode.icon}</div>
                <div className="text-sm text-terminal-text font-semibold">{mode.label}</div>
                <div className="text-[10px] text-terminal-dim mt-0.5">{mode.desc}</div>
              </button>
            )
          })}
        </div>

        <div className="bg-black/50 border border-terminal-border rounded-lg p-3 text-xs space-y-1">
          <div className="flex items-center gap-2 text-terminal-dim">
            <span className="w-2 h-2 bg-green-500 rounded-full inline-block animate-pulse" />
            YOLOv8 model: <span className="text-terminal-text">ready</span>
          </div>
          <div className="text-terminal-dim">
            Pipeline: Face detection → Speaker diarization → Smooth interpolation
          </div>
        </div>

        <button
          onClick={handleApply}
          className="w-full px-4 py-2.5 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors"
        >
          $ apply tracking
        </button>
      </div>
    </div>
  )
}
