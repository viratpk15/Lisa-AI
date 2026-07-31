import { FileText, Plus, Database, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function FilesPage() {
  const files = [
    { id: "f1", name: "jarvis_constitution.pdf", size: "2.4 MB", type: "PDF Document", status: "indexed", chunks: "14 Chunks", date: "2 hours ago" },
    { id: "f2", name: "llm_routing_rules.json", size: "48 KB", type: "JSON Config", status: "indexed", chunks: "3 Chunks", date: "1 day ago" },
    { id: "f3", name: "agent_orchestrator.ts", size: "142 KB", type: "TypeScript File", status: "chunking", chunks: "Processing", date: "Just now" }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-linear-to-r from-foreground via-foreground/90 to-primary bg-clip-text text-transparent">Files & Knowledge</h1>
          <p className="text-muted-foreground mt-1">Manage documents, context attachments, and source code vector indexes.</p>
        </div>
        <Button size="sm" className="gap-2 cursor-pointer font-medium">
          <Plus className="h-4 w-4" />
          Add Document
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <Database className="h-4 w-4 text-primary" />
            <CardTitle className="text-sm font-semibold">Total Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">14 Files</div>
            <p className="text-xs text-muted-foreground mt-1">Indexed in global context.</p>
          </CardContent>
        </Card>
        <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <Search className="h-4 w-4 text-blue-500" />
            <CardTitle className="text-sm font-semibold">Vector Nodes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">842 Chunks</div>
            <p className="text-xs text-muted-foreground mt-1">Distributed across indices.</p>
          </CardContent>
        </Card>
        <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <FileText className="h-4 w-4 text-emerald-500" />
            <CardTitle className="text-sm font-semibold">Indexing Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98% Sync</div>
            <p className="text-xs text-muted-foreground mt-1">1 file active in pipeline.</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/60 bg-card/30 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-base font-semibold">Filesystem Knowledge Index</CardTitle>
          <CardDescription>Vector mapped files accessible by agents for context retrieval.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border border-border/50 rounded-xl overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="bg-secondary/40 border-b border-border/50 text-xs font-semibold text-muted-foreground uppercase font-mono">
                <tr>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">File Type</th>
                  <th className="px-6 py-3">Size</th>
                  <th className="px-6 py-3">Chunks</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 font-mono text-xs">
                {files.map((file) => (
                  <tr key={file.id} className="hover:bg-secondary/20 transition-colors">
                    <td className="px-6 py-4 flex items-center gap-2 font-medium text-foreground">
                      <FileText className="h-3.5 w-3.5 text-primary/80" />
                      {file.name}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{file.type}</td>
                    <td className="px-6 py-4 text-muted-foreground">{file.size}</td>
                    <td className="px-6 py-4">
                      <Badge variant="secondary" className="text-[10px] uppercase font-semibold">
                        {file.chunks}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`h-2 w-2 inline-block rounded-full mr-1.5 ${file.status === "indexed" ? "bg-emerald-500" : "bg-amber-500 animate-pulse"}`} />
                      <span className="capitalize">{file.status}</span>
                    </td>
                    <td className="px-6 py-4 text-right text-muted-foreground">{file.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
