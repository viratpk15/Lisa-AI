import { useMemo } from "react"
import { useNavigate } from "react-router"
import { motion } from "framer-motion"
import { useAuthStore } from "@/services/store/authStore"
import { useConversationsQuery } from "@/services/queries/chat"
import { useEmailDigest } from "@/features/Email/queries"
import {
  Bot,
  Mail,
  FolderOpen,
  Settings,
  ArrowRight,
  MessageSquare,
  AlertCircle,
  FileText,
  Clock,
  Sparkles,
  CheckCircle2,
  Plane,
  Briefcase
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function HomePage() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)

  // Derive time-based greeting and real user name
  const { greeting, firstName } = useMemo(() => {
    const hour = new Date().getHours()
    const timeGreeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"

    let name = "there"
    if (user?.email) {
      const emailPrefix = user.email.split("@")[0]
      // Clean up common formats like john.doe or john_doe
      const rawName = emailPrefix.split(/[._-]/)[0]
      if (rawName) {
        name = rawName.charAt(0).toUpperCase() + rawName.slice(1)
      }
    }
    return { greeting: timeGreeting, firstName: name }
  }, [user])

  // Real Email Digest Query
  const { data: digest, isError: isDigestError, isLoading: isDigestLoading } = useEmailDigest("today")

  // Real Conversations Query
  const { data: conversations = [], isLoading: isConvLoading } = useConversationsQuery()
  const recentConversations = useMemo(() => conversations.slice(0, 3), [conversations])

  const urgentItems = digest?.top_urgent || []
  const urgentCount = urgentItems.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="max-w-4xl mx-auto space-y-8 py-2"
    >
      {/* 1. Header Greeting */}
      <div className="space-y-1.5">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {greeting}, {firstName}
        </h1>
        <p className="text-sm text-muted-foreground">
          Here is your personal overview and items requiring attention.
        </p>
      </div>

      {/* 2. Quick Actions */}
      <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
        <button
          onClick={() => navigate("/assistant")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <Bot className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Ask Lisa</span>
          <span className="text-xs text-muted-foreground mt-0.5">Start conversation</span>
        </button>

        <button
          onClick={() => navigate("/email")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <Mail className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Open Email</span>
          <span className="text-xs text-muted-foreground mt-0.5">Inbox & digest</span>
        </button>

        <button
          onClick={() => navigate("/files")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <FolderOpen className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Upload File</span>
          <span className="text-xs text-muted-foreground mt-0.5">Knowledge store</span>
        </button>

        <button
          onClick={() => navigate("/travel")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <Plane className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Travel</span>
          <span className="text-xs text-muted-foreground mt-0.5">Trip planner</span>
        </button>

        <button
          onClick={() => navigate("/jobs")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <Briefcase className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Jobs</span>
          <span className="text-xs text-muted-foreground mt-0.5">Find opportunities</span>
        </button>

        <button
          onClick={() => navigate("/settings")}
          className="flex flex-col items-start p-4 rounded-xl border border-border/60 bg-card/60 hover:bg-secondary/50 hover:border-border transition-all text-left group cursor-pointer outline-none shadow-xs"
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mb-3 group-hover:scale-105 transition-transform">
            <Settings className="h-5 w-5" />
          </div>
          <span className="text-sm font-semibold text-foreground">Settings</span>
          <span className="text-xs text-muted-foreground mt-0.5">Preferences & power</span>
        </button>
      </div>

      {/* 3. Needs Your Attention (Email Digest) */}
      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <CardTitle className="text-base font-semibold">Needs Your Attention</CardTitle>
              {urgentCount > 0 && (
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                  {urgentCount} urgent
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">Urgent emails and priority action items detected by Lisa.</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/email")}
            className="text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1"
          >
            <span>View all</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </CardHeader>
        <CardContent>
          {isDigestLoading ? (
            <div className="py-8 text-center text-xs text-muted-foreground">
              Checking recent email intelligence...
            </div>
          ) : isDigestError ? (
            <div className="p-5 rounded-xl bg-secondary/30 border border-border/50 text-center space-y-3">
              <div className="p-2.5 rounded-full bg-secondary w-fit mx-auto text-muted-foreground">
                <AlertCircle className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-foreground">Connect Gmail to see important emails</p>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                  Connect your Google account in Email Agent to automatically summarize important emails, track action items, and detect deadlines.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => navigate("/email")}
                className="cursor-pointer gap-1.5 text-xs font-medium"
              >
                <Mail className="h-3.5 w-3.5" />
                Connect Gmail
              </Button>
            </div>
          ) : urgentItems.length > 0 ? (
            <div className="divide-y divide-border/40">
              {urgentItems.map((item) => (
                <div
                  key={item.email_id}
                  onClick={() => navigate(`/email?selected=${item.email_id}`)}
                  className="py-3 flex items-start justify-between gap-4 hover:bg-secondary/30 px-2 rounded-lg transition-colors cursor-pointer"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-foreground truncate">{item.subject}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-secondary text-muted-foreground border border-border/40 uppercase">
                        {item.category}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-1">{item.one_line_summary || item.sender}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[11px] font-mono font-bold text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                      Score {item.priority_score}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-muted-foreground space-y-2">
              <CheckCircle2 className="h-6 w-6 text-emerald-500/80 mx-auto" />
              <p className="text-xs font-medium text-foreground">All caught up</p>
              <p className="text-xs text-muted-foreground">No urgent emails requiring your attention right now.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 4. Recent Conversations */}
      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-semibold">Recent Conversations</CardTitle>
            <p className="text-xs text-muted-foreground">Pick up where you left off with Lisa.</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/assistant")}
            className="text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1"
          >
            <span>Open Assistant</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </CardHeader>
        <CardContent>
          {isConvLoading ? (
            <div className="py-8 text-center text-xs text-muted-foreground">
              Loading conversations...
            </div>
          ) : recentConversations.length > 0 ? (
            <div className="space-y-2">
              {recentConversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => navigate("/assistant")}
                  className="p-3 rounded-lg border border-border/40 bg-secondary/20 hover:bg-secondary/50 transition-colors flex items-center justify-between cursor-pointer"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-md bg-primary/10 text-primary shrink-0">
                      <MessageSquare className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-foreground truncate">{conv.title || "Untitled Conversation"}</p>
                      <p className="text-[11px] text-muted-foreground flex items-center gap-1 mt-0.5 font-mono">
                        <Clock className="h-3 w-3" />
                        {conv.time || "Recent"}
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center space-y-3">
              <div className="p-2.5 rounded-full bg-secondary w-fit mx-auto text-muted-foreground">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-medium text-foreground">Start a conversation with Lisa</p>
                <p className="text-xs text-muted-foreground">Ask questions, analyze documents, or delegate tasks.</p>
              </div>
              <Button
                size="sm"
                onClick={() => navigate("/assistant")}
                className="cursor-pointer gap-1.5 text-xs font-medium"
              >
                <Bot className="h-3.5 w-3.5" />
                New Conversation
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 5. Recent Files */}
      <Card className="border-border/70 bg-card/50 shadow-xs">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-semibold">Recent Files</CardTitle>
            <p className="text-xs text-muted-foreground">Documents and knowledge indexed for Lisa.</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/files")}
            className="text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1"
          >
            <span>View Files</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="py-8 text-center space-y-3">
            <div className="p-2.5 rounded-full bg-secondary w-fit mx-auto text-muted-foreground">
              <FileText className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-foreground">No files yet</p>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                Upload PDFs, notes, or data files in the Files section so Lisa can reference them in your conversations.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/files")}
              className="cursor-pointer gap-1.5 text-xs font-medium"
            >
              <FolderOpen className="h-3.5 w-3.5" />
              Go to Files
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
