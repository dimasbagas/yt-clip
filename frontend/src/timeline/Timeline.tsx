import { useEditor } from '../context/VideoEditorContext.tsx'
import { Scissors } from 'lucide-react'

export default function Timeline() {
  const { video, clipStart, clipEnd } = useEditor()
  const hasVideo = video.file || video.url

  return (
    <div className="h-32 bg-terminal-surface border-t border-terminal-border flex flex-col shrink-0">
      <div className="h-7 border-b border-terminal-border flex items-center px-3 gap-4 text-xs text-terminal-dim">
        <span className="text-neon font-semibold">TIMELINE</span>
        <span className="font-mono">{clipStart}</span>
        <Scissors className="w-3 h-3" />
        <span className="font-mono">{clipEnd}</span>
        <div className="flex-1" />
        <button className="hover:text-terminal-text transition-colors">◁</button>
        <button className="hover:text-terminal-text transition-colors">▷</button>
      </div>

      <div className="flex-1 flex items-center justify-center relative">
        {!hasVideo ? (
          <div className="text-center text-terminal-dim">
            <div className="text-lg mb-1">🎬</div>
            <div className="text-xs">No video loaded</div>
          </div>
        ) : (
          <div className="w-full mx-4 relative">
            {/* Waveform placeholder */}
            <div className="flex items-end gap-px h-16">
              {Array.from({ length: 80 }, (_, i) => (
                <div
                  key={i}
                  className="flex-1 bg-neon/20 rounded-t"
                  style={{ height: `${20 + Math.random() * 60}%` }}
                />
              ))}
            </div>
            {/* Clip range overlay */}
            <div className="absolute top-0 left-[10%] right-[20%] h-full border-x border-neon/50 bg-neon/5">
              <div className="absolute -left-[1px] top-0 w-[2px] h-full bg-neon shadow-[0_0_8px_#00ff41]" />
              <div className="absolute -right-[1px] top-0 w-[2px] h-full bg-neon shadow-[0_0_8px_#00ff41]" />
            </div>
          </div>
        )}
      </div>

      <div className="h-6 border-t border-terminal-border flex items-center px-3">
        <div className="flex-1 h-1 bg-terminal-border rounded-full relative">
          <div className="absolute left-[10%] top-0 h-full w-[70%] bg-neon rounded-full" />
        </div>
      </div>
    </div>
  )
}
