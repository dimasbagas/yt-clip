import { EditorProvider } from './context/VideoEditorContext.tsx'
import EditorPage from './pages/EditorPage.tsx'

export default function App() {
  return (
    <EditorProvider>
      <EditorPage />
    </EditorProvider>
  )
}
