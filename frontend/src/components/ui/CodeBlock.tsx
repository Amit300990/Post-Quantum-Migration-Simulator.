import { useState } from 'react'
import { Check, Copy, Download } from 'lucide-react'
import { copyToClipboard, downloadText } from '../../lib/utils'

interface CodeBlockProps {
  code: string
  language?: string
  filename?: string
  maxHeight?: string
  downloadable?: boolean
}

export function CodeBlock({ code, language = 'json', filename, maxHeight = '320px', downloadable = false }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await copyToClipboard(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const ext = language === 'json' ? '.json' : '.txt'
    downloadText(code, (filename ?? 'download') + ext)
  }

  return (
    <div className="relative rounded-lg overflow-hidden border border-surface-600 bg-surface-950">
      <div className="flex items-center justify-between px-4 py-2 bg-surface-800 border-b border-surface-600">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/60" />
          </div>
          {filename && <span className="text-xs text-slate-500 ml-2 font-mono">{filename}</span>}
          {!filename && <span className="text-xs text-slate-500 ml-2">{language}</span>}
        </div>
        <div className="flex items-center gap-1">
          {downloadable && (
            <button
              onClick={handleDownload}
              className="p-1.5 rounded text-slate-500 hover:text-slate-300 hover:bg-surface-700 transition-colors"
              title="Download"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={handleCopy}
            className="p-1.5 rounded text-slate-500 hover:text-slate-300 hover:bg-surface-700 transition-colors"
            title="Copy"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>
      <div
        className="overflow-auto p-4"
        style={{ maxHeight }}
      >
        <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap break-all leading-relaxed">
          {code}
        </pre>
      </div>
    </div>
  )
}
