import { useState, useEffect, useMemo, useCallback } from "react"

export interface VirtualItem {
  index: number
  start: number
  size: number
}

export interface UseVirtualizerOptions {
  count: number
  getScrollElement: () => HTMLElement | null
  estimateSize?: (index: number) => number
  overscan?: number
  enabled?: boolean
}

/**
 * Custom zero-dependency Virtualizer hook.
 * Matches @tanstack/react-virtual API, providing smooth threshold-based virtualized rendering
 * without external npm module installation dependencies.
 */
export function useVirtualizer(options: UseVirtualizerOptions) {
  const {
    count,
    getScrollElement,
    estimateSize = () => 120,
    overscan = 5,
    enabled = true,
  } = options

  const [scrollTop, setScrollTop] = useState(0)
  const [clientHeight, setClientHeight] = useState(800)

  useEffect(() => {
    if (!enabled) return
    const el = getScrollElement()
    if (!el) return

    const handleScroll = () => {
      setScrollTop(el.scrollTop)
      setClientHeight(el.clientHeight || 800)
    }

    handleScroll()
    el.addEventListener("scroll", handleScroll, { passive: true })
    return () => el.removeEventListener("scroll", handleScroll)
  }, [getScrollElement, enabled])

  const itemHeight = estimateSize(0)

  const virtualItems = useMemo(() => {
    if (!enabled || count <= 0) {
      return Array.from({ length: count }, (_, i) => ({
        index: i,
        start: i * itemHeight,
        size: itemHeight,
      }))
    }

    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
    const endIndex = Math.min(count - 1, Math.ceil((scrollTop + clientHeight) / itemHeight) + overscan)

    const items: VirtualItem[] = []
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        start: i * itemHeight,
        size: itemHeight,
      })
    }
    return items
  }, [count, scrollTop, clientHeight, itemHeight, overscan, enabled])

  const getTotalSize = useCallback(() => count * itemHeight, [count, itemHeight])
  const measureElement = useCallback((_el: HTMLElement | null) => {}, [])

  return {
    getVirtualItems: () => virtualItems,
    getTotalSize,
    measureElement,
  }
}
