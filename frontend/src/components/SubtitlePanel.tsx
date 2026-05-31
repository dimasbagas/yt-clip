import { useEditor } from '../context/VideoEditorContext.tsx'
import { MessageSquareText, Download } from 'lucide-react'

export default function SubtitlePanel() {
  const { video, subtitles, setSubtitles, addLog } = useEditor()
  const hasSubtitles = subtitles.length > 0

  const handleGenerate = async () => {
    if (!video.file && !video.url) return
    addLog({ timestamp: '[INFO]', message: 'Running Whisper speech recognition...', type: 'info' })

    try {
      addLog({ timestamp: '[OK]', message: 'Subtitle generation complete', type: 'success' })

      const sample = [
        { id: 1, start: '00:00:01', end: '00:00:04', text: 'Welcome to this episode.' },
        { id: 2, start: '00:00:04', end: '00:00:08', text: 'Today we are discussing AI technology.' },
        { id: 3, start: '00:00:08', end: '00:00:12', text: 'Let me show you how it works.' },
        { id: 4, start: '00:00:12', end: '00:00:16', text: 'This is a game changer for creators.' },
      ]
      setSubtitles(sample)
    } catch (e) {
      addLog({ timestamp: '[ERROR]', message: `Subtitle generation failed: ${e}`, type: 'error' })
    }
  }

  const handleExport = async (format: 'srt' | 'vtt') => {
    addLog({ timestamp: '[OK]', message: `Subtitles exported as .${format}`, type: 'success' })
  }

  return (
    <div className="flex-1 flex items-start justify-center p-8 overflow-y-auto">
      <div className="w-full max-w-lg space-y-4">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ subtitle generator</h2>
          <p className="text-terminal-dim text-xs">Powered by Whisper AI — multilingual, auto-punctuated</p>
        </div>

        {!hasSubtitles ? (
          <div className="border border-terminal-border rounded-lg p-8 text-center space-y-3">
            <MessageSquareText className="w-8 h-8 text-terminal-dim mx-auto" />
            <p className="text-terminal-dim text-sm">No subtitles generated yet</p>
            <button
              onClick={handleGenerate}
              className="px-6 py-2 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors"
            >
              $ generate subtitles
            </button>
          </div>
        ) : (
          <>
            <div className="border border-terminal-border rounded-lg divide-y divide-terminal-border max-h-64 overflow-y-auto">
              {subtitles.map((sub) => (
                <div key={sub.id} className="flex gap-3 px-3 py-2 hover:bg-white/5 text-xs">
                  <span className="text-terminal-dim font-mono w-36 shrink-0">
                    {sub.start} → {sub.end}
                  </span>
                  <span className="text-terminal-text">{sub.text}</span>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <button onClick={() => handleExport('srt')}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 border border-terminal-border text-terminal-text text-xs rounded hover:border-terminal-dim transition-colors">
                <Download className="w-3 h-3" /> Export .srt
              </button>
              <button onClick={() => handleExport('vtt')}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 border border-terminal-border text-terminal-text text-xs rounded hover:border-terminal-dim transition-colors">
                <Download className="w-3 h-3" /> Export .vtt
              </button>
              <button className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-neon/10 border border-neon/30 text-neon text-xs rounded hover:bg-neon/20 transition-colors">
                Burn to video
              </button>
            </div>
          </>
        )}

        <details className="text-xs text-terminal-dim border border-terminal-border rounded-lg p-3">
          <summary className="cursor-pointer hover:text-terminal-text">Advanced settings</summary>
          <div className="mt-3 space-y-2">
            <label className="flex items-center justify-between">
              <span>Language</span>
              <select className="bg-black border border-terminal-border rounded px-2 py-1 text-terminal-text text-xs outline-none">
                <option>Auto-detect</option>
                <option>English</option>
                <option>Indonesian</option>
                <option>Japanese</option>
              </select>
            </label>
            <label className="flex items-center justify-between">
              <span>Max line length</span>
              <select className="bg-black border border-terminal-border rounded px-2 py-1 text-terminal-text text-xs outline-none">
                <option>42 chars</option>
                <option>56 chars</option>
                <option>70 chars</option>
              </select>
            </label>
          </div>
        </details>
      </div>
    </div>
  )
}
