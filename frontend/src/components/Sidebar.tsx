import { useEditor } from '../context/VideoEditorContext.tsx'

interface NavItem {
  icon: string
  label: string
  section: string
}

const navItems: NavItem[] = [
  { icon: '📁', label: 'import', section: 'import' },
  { icon: '✂', label: 'clip', section: 'clip' },
  { icon: '💬', label: 'subtitles', section: 'subtitles' },
  { icon: '🎯', label: 'tracking', section: 'tracking' },
  { icon: '📐', label: 'crop', section: 'crop' },
  { icon: '⚡', label: 'render', section: 'render' },
]

export default function Sidebar() {
  const { currentSection, setSection, video } = useEditor()

  return (
    <nav className="w-48 bg-terminal-surface border-r border-terminal-border flex flex-col shrink-0">
      <div className="p-3 border-b border-terminal-border">
        <div className="text-xs text-terminal-dim mb-2">NAVIGATION</div>
        <div className="space-y-0.5">
          {navItems.map((item) => (
            <button
              key={item.label}
              onClick={() => setSection(item.section)}
              className={`w-full flex items-center gap-2 px-3 py-1.5 text-sm rounded transition-colors ${
                currentSection === item.section
                  ? 'bg-neon/10 text-neon border-l-2 border-neon'
                  : 'text-terminal-dim hover:text-terminal-text hover:bg-white/5'
              }`}
            >
              <span className="text-xs">{item.icon}</span>
              <span>$ {item.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="p-3 border-b border-terminal-border">
        <div className="text-xs text-terminal-dim mb-2">PRESET</div>
        <PresetButton label="TikTok" />
        <PresetButton label="YouTube Shorts" />
        <PresetButton label="Instagram Reels" />
        <PresetButton label="Landscape" />
      </div>

      <div className="p-3 mt-auto">
        <div className="text-xs text-terminal-dim mb-1">STORAGE</div>
        <div className="text-xs text-terminal-text">
          <div>Source: <span className={video.file ? 'text-neon' : 'text-terminal-dim'}>{video.file ? video.name : 'empty'}</span></div>
          <div>Temp: <span className="text-yellow-500">—</span></div>
        </div>
      </div>
    </nav>
  )
}

function PresetButton({ label }: { label: string }) {
  return (
    <button className="w-full text-left px-3 py-1 text-xs text-terminal-dim hover:text-terminal-text hover:bg-white/5 rounded transition-colors">
      {label}
    </button>
  )
}
