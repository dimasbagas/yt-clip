import TerminalHeader from '../components/TerminalHeader.tsx'
import Sidebar from '../components/Sidebar.tsx'
import ImportPanel from '../components/ImportPanel.tsx'
import VideoCanvas from '../components/VideoCanvas.tsx'
import ClipEditor from '../components/ClipEditor.tsx'
import SubtitlePanel from '../components/SubtitlePanel.tsx'
import TrackingPanel from '../components/TrackingPanel.tsx'
import CropPanel from '../components/CropPanel.tsx'
import ExportPanel from '../components/ExportPanel.tsx'
import TerminalOutput from '../terminal/TerminalOutput.tsx'
import Timeline from '../timeline/Timeline.tsx'
import { useEditor } from '../context/VideoEditorContext.tsx'

export default function EditorPage() {
  const { currentSection, video } = useEditor()
  const hasVideo = video.file || video.url

  const renderPanel = () => {
    switch (currentSection) {
      case 'import': return <ImportPanel />
      case 'clip': return hasVideo ? <ClipEditor /> : <ImportPanel />
      case 'subtitles': return hasVideo ? <SubtitlePanel /> : <ImportPanel />
      case 'tracking': return hasVideo ? <TrackingPanel /> : <ImportPanel />
      case 'crop': return hasVideo ? <CropPanel /> : <ImportPanel />
      case 'render': return hasVideo ? <ExportPanel /> : <ImportPanel />
      default: return <ImportPanel />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-terminal-bg text-terminal-text">
      <TerminalHeader />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />

        <main className="flex-1 flex flex-col">
          {currentSection === 'clip' && hasVideo ? (
            <div className="flex-1 flex">
              <VideoCanvas />
              <ClipEditor />
            </div>
          ) : (
            renderPanel()
          )}

          <Timeline />
        </main>
      </div>

      <TerminalOutput />
    </div>
  )
}
