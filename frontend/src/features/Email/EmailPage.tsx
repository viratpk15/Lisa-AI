// frontend/src/features/Email/EmailPage.tsx
import React, { useState, useEffect } from "react"
import { useSearchParams } from "react-router"
import { Mail, PieChart, AlertCircle, RefreshCw, ArrowLeft } from "lucide-react"
import { InboxList } from "./InboxList"
import { EmailDetail } from "./EmailDetail"
import { DigestView } from "./DigestView"
import {
  useEmailList,
  useEmailDetail,
  useSyncEmail,
  useClassifyEmail,
  useSummarizeEmail,
  useExtractActionsEmail,
  useGoogleAuthStatus,
} from "./queries"
import { fetchGoogleAuthUrlApi } from "./api"
import { useInspectorStore } from "@/features/Workspace/inspectorStore"
import { Button } from "@/components/ui/button"

export const EmailPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get("tab") === "digest" ? "digest" : "detail"
  const [activeTab, setActiveTab] = useState<"detail" | "digest">(initialTab)
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [syncErrorMessage, setSyncErrorMessage] = useState<string | null>(null)
  const [isConnectingGmail, setIsConnectingGmail] = useState(false)
  const [showMobileDetail, setShowMobileDetail] = useState(false)
  const [windowWidth, setWindowWidth] = useState(typeof window !== "undefined" ? window.innerWidth : 1200)

  // Query Google OAuth status directly on Mail page
  const { data: googleStatus } = useGoogleAuthStatus()
  const isConnected = googleStatus?.connected === true

  const handleConnectGmail = async () => {
    try {
      setIsConnectingGmail(true)
      const res = await fetchGoogleAuthUrlApi()
      const targetUrl = res?.url || res?.authorization_url
      if (targetUrl) {
        window.location.href = targetUrl
      } else {
        console.error("No authorization URL received from backend:", res)
        setIsConnectingGmail(false)
      }
    } catch (err) {
      console.error("Failed to initiate Gmail OAuth:", err)
      setIsConnectingGmail(false)
    }
  }

  // Track window resizing for mobile layout switching
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  const isMobile = windowWidth < 768

  // Sync tab with URL search params
  useEffect(() => {
    const tabParam = searchParams.get("tab")
    if (tabParam === "digest" && activeTab !== "digest") {
      setActiveTab("digest")
    } else if (!tabParam && activeTab === "digest") {
      setActiveTab("detail")
    }
  }, [searchParams, activeTab])

  // Sync selected email from URL param (e.g. from Home page attention items)
  useEffect(() => {
    const selectedParam = searchParams.get("selected")
    if (selectedParam) {
      const parsedId = parseInt(selectedParam, 10)
      if (!isNaN(parsedId)) {
        setSelectedEmailId(parsedId)
        setShowMobileDetail(true)
      }
    }
  }, [searchParams])

  const handleTabChange = (tab: "detail" | "digest") => {
    setActiveTab(tab)
    if (tab === "digest") {
      setSearchParams({ tab: "digest" })
    } else {
      setSearchParams({})
    }
  }

  // ---------------------------------------------------------------------------
  // Queries & Mutations
  // ---------------------------------------------------------------------------

  const {
    data: listData,
    isLoading: isListLoading,
  } = useEmailList(selectedCategory ? { category: selectedCategory } : undefined)

  const emails = React.useMemo(() => listData?.emails ?? [], [listData?.emails])

  // Auto-select first email if none selected on desktop
  useEffect(() => {
    if (!selectedEmailId && emails.length > 0 && !isMobile) {
      setSelectedEmailId(emails[0].id)
    }
  }, [emails, selectedEmailId, isMobile])

  const { data: detailData, isLoading: isDetailLoading } = useEmailDetail(selectedEmailId)

  // Sync active email context with Inspector Panel
  useEffect(() => {
    if (detailData) {
      const analysis = detailData.analysis
      const actionItems = analysis?.action_items?.tasks || []
      const isUrgent = analysis?.category === "URGENT" || (analysis?.priority_score ?? 0) >= 80
      const actionRequired = Boolean(
        analysis?.action_items?.sender_action_required ||
        (analysis?.action_items?.tasks && analysis.action_items.tasks.length > 0)
      )

      useInspectorStore.getState().setEmailContext({
        id: detailData.id,
        subject: detailData.subject,
        sender: detailData.sender,
        received_at: detailData.received_at,
        category: analysis?.category || null,
        priority_score: analysis?.priority_score || null,
        is_urgent: isUrgent,
        action_required: actionRequired,
        action_items: actionItems,
        deadline: analysis?.deadline || null,
        summary_text: analysis?.summary_text || null,
        verification: detailData.verification || null,
      })
    } else {
      useInspectorStore.getState().setEmailContext(null)
    }
  }, [detailData])

  const syncMutation = useSyncEmail()
  const classifyMutation = useClassifyEmail()
  const summarizeMutation = useSummarizeEmail()
  const extractActionsMutation = useExtractActionsEmail()

  const handleSync = async () => {
    if (!isConnected) {
      handleConnectGmail()
      return
    }
    setSyncErrorMessage(null)
    syncMutation.mutate(undefined, {
      onError: (err) => {
        setSyncErrorMessage(err.message || "Failed to synchronize Gmail. Click 'Connect Gmail' to re-authorize.")
      },
    })
  }

  const handleClassify = () => {
    if (selectedEmailId) {
      classifyMutation.mutate(selectedEmailId)
    }
  }

  const handleSummarize = () => {
    if (selectedEmailId) {
      summarizeMutation.mutate(selectedEmailId)
    }
  }

  const handleExtractActions = () => {
    if (selectedEmailId) {
      extractActionsMutation.mutate(selectedEmailId)
    }
  }

  const handleSelectFromDigest = (id: number) => {
    setSelectedEmailId(id)
    setShowMobileDetail(true)
    handleTabChange("detail")
  }

  const handleSelectEmail = (id: number) => {
    setSelectedEmailId(id)
    if (isMobile) {
      setShowMobileDetail(true)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] w-full overflow-hidden bg-background">
      {/* Top Banner if sync error */}
      {syncErrorMessage && (
        <div className="bg-rose-500/10 border-b border-rose-500/30 px-4 py-2 flex items-center justify-between text-xs text-rose-400 shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="truncate">{syncErrorMessage}</span>
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-2">
            {!isConnected && (
              <Button
                size="sm"
                onClick={handleConnectGmail}
                disabled={isConnectingGmail}
                className="h-6 px-2.5 text-[11px] gap-1 bg-rose-600 hover:bg-rose-500 text-white font-medium cursor-pointer"
              >
                <Mail className="w-3 h-3" /> Connect Gmail
              </Button>
            )}
            <button
              onClick={handleSync}
              className="font-medium underline hover:text-rose-300 cursor-pointer flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" /> Retry
            </button>
          </div>
        </div>
      )}

      {/* 2-Pane Main Viewport with Mobile Single-Pane Support */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Inbox List (Visible on desktop or when mobile detail is not open) */}
        <div
          className={`${
            isMobile && showMobileDetail ? "hidden" : "flex"
          } w-full md:w-96 md:border-r border-border/70 shrink-0 flex-col h-full overflow-hidden`}
        >
          <InboxList
            emails={emails}
            selectedId={selectedEmailId}
            onSelect={handleSelectEmail}
            isLoading={isListLoading}
            isSyncing={syncMutation.isPending}
            onSync={handleSync}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            isConnected={isConnected}
            connectedEmail={googleStatus?.email_address}
            isConnectingGmail={isConnectingGmail}
            onConnectGmail={handleConnectGmail}
          />
        </div>

        {/* Right Pane: Tabs Header + Active View (Detail | Daily Digest) */}
        <div
          className={`${
            isMobile && !showMobileDetail ? "hidden" : "flex"
          } flex-1 flex-col h-full overflow-hidden`}
        >
          {/* Navigation Bar / Tabs */}
          <div className="h-11 px-4 border-b border-border/60 bg-card/30 flex items-center justify-between shrink-0 gap-2">
            <div className="flex items-center gap-2 font-mono text-xs">
              {/* Mobile Back Button to return to Inbox */}
              {isMobile && showMobileDetail && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowMobileDetail(false)}
                  className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground cursor-pointer gap-1 mr-1"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Inbox</span>
                </Button>
              )}

              <button
                onClick={() => handleTabChange("detail")}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors cursor-pointer ${
                  activeTab === "detail"
                    ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Email Detail</span>
              </button>
              <button
                onClick={() => handleTabChange("digest")}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-colors cursor-pointer ${
                  activeTab === "digest"
                    ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                <PieChart className="w-3.5 h-3.5" />
                <span>Daily Digest</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              {isConnected ? (
                <span className="text-[11px] text-emerald-400/90 font-mono hidden sm:inline-flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  {googleStatus?.email_address ? `Connected: ${googleStatus.email_address}` : "Gmail Connected"}
                </span>
              ) : (
                <Button
                  onClick={handleConnectGmail}
                  disabled={isConnectingGmail}
                  variant="outline"
                  size="sm"
                  className="h-6 px-2 text-[11px] gap-1 text-rose-400 border-rose-500/30 hover:bg-rose-500/10 cursor-pointer hidden sm:inline-flex"
                >
                  <Mail className="w-3 h-3 text-rose-400" />
                  <span>Connect Gmail</span>
                </Button>
              )}
              <span className="text-[11px] text-muted-foreground font-mono hidden md:inline">
                Lisa Email Intelligence
              </span>
            </div>
          </div>

          {/* Tab Content Viewport */}
          <div className="flex-1 overflow-hidden">
            {activeTab === "detail" ? (
              <EmailDetail
                email={detailData ?? null}
                isLoading={isDetailLoading}
                onClassify={handleClassify}
                isClassifying={classifyMutation.isPending}
                onSummarize={handleSummarize}
                isSummarizing={summarizeMutation.isPending}
                onExtractActions={handleExtractActions}
                isExtractingActions={extractActionsMutation.isPending}
              />
            ) : (
              <DigestView onSelectEmail={handleSelectFromDigest} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmailPage
