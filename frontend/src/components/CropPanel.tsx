import { useEditor } from '../context/VideoEditorContext.tsx'

const ratios = [
  { id: '9:16', icon: '📱', label: '9:16', desc: 'TikTok / Shorts / Reels' },
  { id: '16:9', icon: '🖥', label: '16:9', desc: 'Landscape / YouTube' },
  { id: '1:1', icon: '⬛', label: '1:1', desc: 'Square / Instagram' },
]

export default function CropPanel() {
  const { aspectRatio, setAspectRatio, addLog } = useEditor()

  const handleApply = () => {
    addLog({ timestamp: '[INFO]', message: `Aspect ratio set to ${aspectRatio}`, type: 'info' })
    addLog({ timestamp: '[OK]', message: 'Auto-crop configured', type: 'success' })
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="w-full max-w-lg space-y-5">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ portrait conversion</h2>
          <p className="text-terminal-dim text-xs">AI smart crop with subject centering</p>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {ratios.map((ratio) => {
            const active = aspectRatio === ratio.id
            return (
              <button
                key={ratio.id}
                onClick={() => setAspectRatio(ratio.id)}
                className={`p-4 rounded-lg border transition-all text-center ${
                  active
                    ? 'border-neon bg-neon/5'
                    : 'border-terminal-border hover:border-terminal-dim bg-black/30'
                }`}
              >
                <div className="text-2xl mb-2">{ratio.icon}</div>
                <div className="text-sm text-terminal-text font-semibold">{ratio.label}</div>
                <div className="text-[10px] text-terminal-dim mt-1">{ratio.desc}</div>
              </button>
            )
          })}
        </div>

        <div className="bg-black/50 border border-terminal-border rounded-lg p-3 text-xs space-y-1">
          <div className="flex items-center gap-2 text-terminal-dim">
            <span className="w-2 h-2 bg-green-500 rounded-full inline-block animate-pulse" />
            AI tracking: <span className="text-terminal-text">active</span>
          </div>
          <div className="text-terminal-dim">
            Smart crop with face detection + subject centering
          </div>
        </div>

        <button
          onClick={handleApply}
          className="w-full px-4 py-2.5 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors"
        >
          $ apply crop
        </button>
      </div>
    </div>
  )
}
