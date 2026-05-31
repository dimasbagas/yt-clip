const BASE_URL = 'http://127.0.0.1:8899'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`)
  }
  return res.json()
}

function params(body: Record<string, unknown>): RequestInit {
  return {
    method: 'POST',
    body: JSON.stringify(body),
  }
}

export const api = {
  health: () => request<{ status: string; version: string }>('/api/health'),

  system: () => request<{ nvenc: boolean; models: Record<string, string> }>('/api/system'),

  upload: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE_URL}/api/upload`, { method: 'POST', body: form })
    if (!res.ok) throw new Error(`Upload failed: ${await res.text()}`)
    return res.json() as Promise<{
      path: string; filename: string; duration: number; width: number; height: number; fps: number
    }>
  },

  youtubeInfo: (url: string) =>
    request<{ title: string; duration: number; formats: Array<Record<string, unknown>> }>(
      '/api/youtube/info', params({ url })
    ),

  youtubeDownload: (url: string, quality = 'best') =>
    request<{ title: string; path: string; duration: number }>(
      '/api/youtube/download', params({ url, quality })
    ),

  trim: (videoPath: string, start: string, end: string) =>
    request<{ path: string }>('/api/clip/trim', params({ video_path: videoPath, start, end })),

  generateSubtitles: (videoPath: string, language?: string) =>
    request<{ segments: Array<Record<string, unknown>>; language: string; srt_path: string; vtt_path: string }>(
      '/api/subtitles/generate', params({ video_path: videoPath, language })
    ),

  render: (opts: {
    video_path: string; start: string; end: string; aspect_ratio?: string
    tracking_mode?: string; format?: string; burn_subtitles?: boolean
  }) => request<{ output_path: string; steps: string[] }>('/api/render', params(opts)),

  detectFaces: async (videoPath: string) => {
    const form = new FormData()
    form.append('video_path', videoPath)
    const res = await fetch(`${BASE_URL}/api/tracking/detect`, { method: 'POST', body: form })
    return res.json()
  },
}
