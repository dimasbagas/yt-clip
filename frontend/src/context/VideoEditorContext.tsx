import { createContext, useContext, useState, useCallback, type ReactNode, type Dispatch, type SetStateAction } from 'react'

export interface Subtitle {
  id: number
  start: string
  end: string
  text: string
}

export interface Log {
  timestamp: string
  message: string
  type: 'info' | 'success' | 'warn' | 'error' | 'system'
}

export interface VideoInfo {
  file: File | null
  url: string
  name: string
  duration: number
}

interface EditorState {
  currentSection: string
  video: VideoInfo
  clipStart: string
  clipEnd: string
  subtitles: Subtitle[]
  trackingMode: string
  aspectRatio: string
  exportFormat: string
  exportPreset: string
  renderProgress: number
  renderStatus: string
  logs: Log[]
  setSection: (section: string) => void
  setVideo: (video: VideoInfo) => void
  setClipStart: (t: string) => void
  setClipEnd: (t: string) => void
  setSubtitles: (s: Subtitle[]) => void
  setTrackingMode: (m: string) => void
  setAspectRatio: (r: string) => void
  setExportFormat: (f: string) => void
  setExportPreset: (p: string) => void
  setRenderProgress: Dispatch<SetStateAction<number>>
  setRenderStatus: (s: string) => void
  addLog: (log: Log) => void
}

const EditorContext = createContext<EditorState | null>(null)

const defaultVideo: VideoInfo = { file: null, url: '', name: '', duration: 0 }

export function EditorProvider({ children }: { children: ReactNode }) {
  const [currentSection, setCurrentSection] = useState('import')
  const [video, setVideo] = useState<VideoInfo>(defaultVideo)
  const [clipStart, setClipStart] = useState('00:00:00')
  const [clipEnd, setClipEnd] = useState('00:00:00')
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [trackingMode, setTrackingMode] = useState('podcast')
  const [aspectRatio, setAspectRatio] = useState('9:16')
  const [exportFormat, setExportFormat] = useState('mp4')
  const [exportPreset, setExportPreset] = useState('tiktok')
  const [renderProgress, setRenderProgress] = useState(0)
  const [renderStatus, setRenderStatus] = useState('idle')
  const [logs, setLogs] = useState<Log[]>([
    { timestamp: '[BOOT]', message: 'ClipOS v0.1.0 initializing...', type: 'system' },
    { timestamp: '[BOOT]', message: 'Loading AI modules...', type: 'system' },
    { timestamp: '[OK]', message: 'Whisper engine ready', type: 'success' },
    { timestamp: '[OK]', message: 'YOLO detection loaded', type: 'success' },
    { timestamp: '[OK]', message: 'FFmpeg pipeline ready', type: 'success' },
    { timestamp: '[INFO]', message: 'Waiting for video input...', type: 'info' },
  ])

  const addLog = useCallback((log: Log) => {
    setLogs((prev) => [...prev, log])
  }, [])

  return (
    <EditorContext.Provider
      value={{
        currentSection, setSection: setCurrentSection,
        video, setVideo,
        clipStart, setClipStart,
        clipEnd, setClipEnd,
        subtitles, setSubtitles,
        trackingMode, setTrackingMode,
        aspectRatio, setAspectRatio,
        exportFormat, setExportFormat,
        exportPreset, setExportPreset,
        renderProgress, setRenderProgress,
        renderStatus, setRenderStatus,
        logs, addLog,
      }}
    >
      {children}
    </EditorContext.Provider>
  )
}

export function useEditor() {
  const ctx = useContext(EditorContext)
  if (!ctx) throw new Error('useEditor must be inside EditorProvider')
  return ctx
}
