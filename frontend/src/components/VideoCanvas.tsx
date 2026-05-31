import { useEditor } from '../context/VideoEditorContext.tsx'
import { Monitor } from 'lucide-react'

export default function VideoCanvas() {
  const { video } = useEditor()
  const hasVideo = video.file || video.url

  if (!hasVideo) {
    return (
      <div className="flex-1 flex items-center justify-center bg-black relative">
        <div className="text-center">
          <Monitor className="w-16 h-16 text-terminal-dim/20 mx-auto mb-4" />
          <p className="text-terminal-dim text-sm mb-2">No video loaded</p>
          <p className="text-xs text-terminal-dim/60">
            Use <span className="text-neon">import</span> to load a video
          </p>
        </div>
        <div className="absolute top-3 left-3 text-[10px] text-terminal-dim/30 font-mono">
          ┌─ PREVIEW ────────────────┐
        </div>
        <div className="absolute bottom-3 right-3 text-[10px] text-terminal-dim/30 font-mono">
          └── idling ────────────────┘
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex items-center justify-center bg-black relative">
      {video.file && (
        <video
          src={video.url}
          className="max-w-full max-h-full object-contain"
          controls={false}
        />
      )}
      {!video.file && video.url && (
        <div className="text-center">
          <Link className="w-12 h-12 text-terminal-dim/30 mx-auto mb-3" />
          <p className="text-terminal-dim text-sm">YouTube video queued</p>
          <p className="text-xs text-terminal-dim/60 mt-1">Waiting for download...</p>
        </div>
      )}

      {/* Overlay info */}
      <div className="absolute top-3 left-3 text-[10px] text-terminal-dim/30 font-mono">
        ┌─ PREVIEW ────────────────┐
      </div>
      <div className="absolute bottom-3 right-3 text-[10px] text-terminal-dim/30 font-mono">
        └── {video.name} ──────────┘
      </div>
    </div>
  )
}

function Link(props: Record<string, unknown>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  )
}
