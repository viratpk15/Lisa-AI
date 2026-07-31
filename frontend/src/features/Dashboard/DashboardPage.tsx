import { motion } from "framer-motion"
import { dashboardGridVariants } from "@/lib/motion"
import {
  Hero,
  QuickActions,
  ContinueWorking,
  Projects,
  Conversations,
  Agents,
  SystemHealth,
  Timeline,
  Notifications,
  Insights
} from "./widgets"

export default function DashboardPage() {
  return (
    <motion.div
      variants={dashboardGridVariants}
      initial="initial"
      animate="animate"
      className="space-y-8"
    >
      {/* 1. Welcome Hero Widget */}
      <Hero />

      {/* 2. Responsive Grid Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Columns (2/3 width on desktop) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Actions Card Grid */}
          <QuickActions />

          {/* Recent Workspace Cards */}
          <ContinueWorking />

          {/* Active Projects Cards */}
          <Projects />

          {/* Active Agents list */}
          <Agents />

          {/* Recent Conversations */}
          <Conversations />
        </div>

        {/* Right Column (1/3 width on desktop) */}
        <div className="space-y-8">
          {/* Real-time System Telemetry */}
          <SystemHealth />

          {/* Stackable notifications */}
          <Notifications />

          {/* OS Timeline events logs */}
          <Timeline />

          {/* Knowledge Insights */}
          <Insights />
        </div>

      </div>
    </motion.div>
  )
}
