import { useState, useRef, type ChangeEvent, type DragEvent } from 'react'
import { Upload, Link } from 'lucide-react'
import { useEditor } from '../context/VideoEditorContext.tsx'
import { api } from '../api/client.ts'

export default function ImportPanel() {
  const { setVideo, setSection, addLog } = useEditor()
  const [url, setUrl] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    if (!file.type.startsWith('video/')) return

    setLoading(true)
    addLog({ timestamp: '[INFO]', message: `Uploading: ${file.name}`, type: 'info' })

    try {
      const result = await api.upload(file)
      setVideo({
        file,
        url: URL.createObjectURL(file),
        name: file.name,
        duration: result.duration,
      })
      addLog({ timestamp: '[OK]', message: `Imported: ${file.name} (${result.duration}s)`, type: 'success' })
      setSection('clip')
    } catch (e) {
      addLog({ timestamp: '[ERROR]', message: `Upload failed: ${e}`, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleInput = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }

  const handleUrlImport = async () => {
    if (!url.trim()) return
    setLoading(true)
    addLog({ timestamp: '[INFO]', message: `Fetching: ${url}`, type: 'info' })

    try {
      const info = await api.youtubeInfo(url)
      addLog({ timestamp: '[OK]', message: `Found: ${info.title} (${info.duration}s)`, type: 'success' })

      const dl = await api.youtubeDownload(url)
      setVideo({ file: null, url: dl.path, name: dl.title, duration: dl.duration })
      addLog({ timestamp: '[OK]', message: 'Download complete, ready to process', type: 'success' })
      setSection('clip')
    } catch (e) {
      addLog({ timestamp: '[ERROR]', message: `YouTube import failed: ${e}`, type: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center">
          <h2 className="text-neon text-lg font-semibold mb-1">$ import video</h2>
          <p className="text-terminal-dim text-xs">Load a video file or paste a YouTube URL</p>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !loading && inputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-neon bg-neon/5'
              : 'border-terminal-border hover:border-terminal-dim'
          } ${loading ? 'opacity-50 pointer-events-none' : ''}`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="video/mp4,video/mov,video/mkv,video/avi"
            className="hidden"
            onChange={handleInput}
          />
          <Upload className="w-8 h-8 text-terminal-dim mx-auto mb-3" />
          <p className="text-terminal-text text-sm mb-1">
            {loading ? 'Processing...' : dragOver ? 'Drop video here' : 'Drag & drop video'}
          </p>
          <p className="text-terminal-dim text-xs">or click to browse</p>
          <div className="flex gap-2 justify-center mt-3 text-[10px] text-terminal-dim">
            <span className="px-2 py-0.5 border border-terminal-border rounded">mp4</span>
            <span className="px-2 py-0.5 border border-terminal-border rounded">mov</span>
            <span className="px-2 py-0.5 border border-terminal-border rounded">mkv</span>
            <span className="px-2 py-0.5 border border-terminal-border rounded">avi</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-terminal-border" />
          <span className="text-terminal-dim text-xs">OR</span>
          <div className="flex-1 h-px bg-terminal-border" />
        </div>

        <div className="space-y-2">
          <label className="text-xs text-terminal-dim flex items-center gap-1.5">
            <Link className="w-3 h-3" />
            YouTube URL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              disabled={loading}
              className="flex-1 bg-black border border-terminal-border rounded px-3 py-2 text-sm text-terminal-text placeholder:text-terminal-dim/40 outline-none focus:border-neon/50 transition-colors disabled:opacity-50"
            />
            <button
              onClick={handleUrlImport}
              disabled={!url.trim() || loading}
              className="px-4 py-2 bg-neon/10 border border-neon/30 text-neon text-sm rounded hover:bg-neon/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              $ fetch
            </button>
          </div>
          <p className="text-[10px] text-terminal-dim/60">Supports public videos & playlists</p>
        </div>
      </div>
    </div>
  )
}
