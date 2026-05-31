import { useEffect, useState } from 'react'
import { api } from '../api/client.ts'

export function useBackend() {
  const [ready, setReady] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    let cancelled = false

    const check = () =>
      api.health()
        .then(() => {
          if (!cancelled) {
            setReady(true)
            setChecking(false)
          }
        })
        .catch(() => {
          if (!cancelled) {
            setReady(false)
            setTimeout(check, 1500)
          }
        })

    check()
    return () => { cancelled = true }
  }, [])

  return { ready, checking }
}
