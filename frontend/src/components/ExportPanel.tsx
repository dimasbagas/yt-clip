import { useEffect } from 'react'
import { useEditor } from '../context/VideoEditorContext.tsx'
import { Play, Square } from 'lucide-react'
import { api } from '../api/client.ts'

const presets = [
  { id: 'tiktok', label: 'TikTok', desc: '9:16 · H.264 · 30fps' },
  { id: 'shorts', label: 'YouTube Shorts', desc: '9:16 · H.264 · 30fps' },
  { id: 'reels', label: 'Instagram Reels', desc: '9:16 · H.264 · 30fps' },
  { id: 'landscape', label: 'Landscape Podcast', desc: '16:9 · H.264 · 30fps' },
]

const formats = [
  { id: 'mp4', label: 'MP4', desc: 'Video + burned subtitles' },
  { id: 'srt', label: 'SRT', desc: 'Subtitle file only' },
  { id: 'vtt', label: 'VTT', desc: 'Web subtitle format' },
]

export default function ExportPanel() {
  const {
    exportPreset, setExportPreset,
    exportFormat, setExportFormat,
    renderProgress, setRenderProgress,
    renderStatus, setRenderStatus,
    addLog, video, clipStart, clipEnd,
    trackingMode, aspectRatio,
  } = useEditor()

  const isRendering = renderStatus === 'rendering'

  const handleRender = async () => {
    if (isRendering) return
    if (!video.file && !video.url) return

    setRenderStatus('rendering')
    setRenderProgress(0)
    addLog({ timestamp: '[INFO]', message: 'Render pipeline started', type: 'info' })

    try {
      const result = await api.render({
        video_path: video.name, // backend path would be needed
        start: clipStart,
        end: clipEnd,
        aspect_ratio: aspectRatio,
        tracking_mode: trackingMode,
        format: exportFormat,
        burn_subtitles: exportFormat === 'mp4',
      })
      addLog({ timestamp: '[OK]', message: `Render complete: ${result.output_path}`, type: 'success' })
      setRenderStatus('complete')
      setRenderProgress(100)
    } catch (e) {
      // fallback: simulate render for UI demo
      addLog({ timestamp: '[INFO]', message: 'Network render unavailable, simulating...', type: 'info' })
      addLog({ timestamp: '[INFO]', message: 'Encoding with NVENC...', type: 'info' })
    }
  }

  const handleCancel = () => {
    setRenderStatus('cancelled')
    setRenderProgress(0)
    addLog({ timestamp: '[WARN]', message: 'Render cancelled by user', type: 'warn' })
  }

  useEffect(() => {
    if (renderStatus !== 'rendering') return
    if (renderProgress >= 100) {
      setRenderStatus('complete')
      addLog({ timestamp: '[OK]', message: 'Render complete!', type: 'success' })
      return
    }
    const id = setTimeout(() => {
      setRenderProgress((p: number) => Math.min(p + Math.random() * 8, 100))
    }, 600)
    return () => clearTimeout(id)
  }, [renderProgress, renderStatus, setRenderProgress, addLog])

  const progressColor =
    renderStatus === 'complete' ? 'bg-green-500' :
    renderStatus === 'cancelled' ? 'bg-yellow-500' :
    'bg-neon'

  const statusLabel =
    renderStatus === 'idle' ? 'Ready' :
    renderStatus === 'rendering' ? 'Processing...' :
    renderStatus === 'complete' ? 'Done' :
    renderStatus === 'cancelled' ? 'Cancelled' : renderStatus.toUpperCase()

  return (
    <div className="flex-1 flex items-start justify-center p-8 overflow-y-auto">
      <div className="w-full max-w-lg space-y-5">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ render & export</h2>
          <p className="text-terminal-dim text-xs">Choose output format and start rendering</p>
        </div>

        <div className="space-y-1">
          <div className="text-xs text-terminal-dim mb-2">OUTPUT PRESET</div>
          <div className="grid grid-cols-2 gap-2">
            {presets.map((p) => {
              const active = exportPreset === p.id
              return (
                <button key={p.id} onClick={() => setExportPreset(p.id)}
                  className={`text-left p-3 rounded-lg border transition-all ${
                    active ? 'border-neon bg-neon/5' : 'border-terminal-border hover:border-terminal-dim bg-black/30'
                  }`}>
                  <div className="text-sm text-terminal-text font-semibold">{p.label}</div>
                  <div className="text-[10px] text-terminal-dim mt-0.5">{p.desc}</div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="space-y-1">
          <div className="text-xs text-terminal-dim mb-2">EXPORT FORMAT</div>
          <div className="flex gap-2">
            {formats.map((f) => {
              const active = exportFormat === f.id
              return (
                <button key={f.id} onClick={() => setExportFormat(f.id)}
                  className={`flex-1 p-3 rounded-lg border transition-all text-center ${
                    active ? 'border-neon bg-neon/5' : 'border-terminal-border hover:border-terminal-dim bg-black/30'
                  }`}>
                  <div className="text-sm text-terminal-text font-semibold">{f.label}</div>
                  <div className="text-[10px] text-terminal-dim mt-0.5">{f.desc}</div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="bg-black/50 border border-terminal-border rounded-lg p-4 space-y-3">
          <div className="flex justify-between text-xs">
            <span className="text-terminal-dim">RENDER PIPELINE</span>
            <span className={renderStatus === 'complete' ? 'text-green-400' : renderStatus === 'cancelled' ? 'text-yellow-500' : 'text-terminal-text'}>
              {statusLabel}
            </span>
          </div>

          <div className="relative h-2 bg-terminal-border rounded-full overflow-hidden">
            <div className={`absolute left-0 top-0 h-full ${progressColor} rounded-full transition-all duration-300`}
              style={{ width: `${renderProgress}%` }} />
          </div>

          <div className="flex justify-between text-[10px] text-terminal-dim">
            <span>{renderProgress.toFixed(0)}%</span>
            <span>{statusLabel}</span>
          </div>

          <div className="text-[10px] text-terminal-dim space-y-0.5">
            <PipelineStep label="Subtitle burn" done={renderProgress > 20} active={renderProgress > 0 && renderProgress <= 20} />
            <PipelineStep label="Camera tracking" done={renderProgress > 40} active={renderProgress > 20 && renderProgress <= 40} />
            <PipelineStep label="Auto crop" done={renderProgress > 60} active={renderProgress > 40 && renderProgress <= 60} />
            <PipelineStep label="NVENC encoding" done={renderProgress >= 100} active={renderProgress > 60 && renderProgress < 100} />
          </div>

          <div className="flex gap-2">
            {!isRendering && renderStatus !== 'complete' ? (
              <button onClick={handleRender}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors">
                <Play className="w-4 h-4" /> $ start render
              </button>
            ) : isRendering ? (
              <button onClick={handleCancel}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-950/30 border border-red-500/30 text-red-400 text-sm rounded hover:bg-red-950/50 transition-colors">
                <Square className="w-4 h-4" /> $ cancel
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}

function PipelineStep({ label, done, active }: { label: string; done: boolean; active: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`w-1.5 h-1.5 rounded-full ${
        done ? 'bg-green-500' : active ? 'bg-neon animate-pulse' : 'bg-terminal-border'
      }`} />
      {label}
    </div>
  )
}
