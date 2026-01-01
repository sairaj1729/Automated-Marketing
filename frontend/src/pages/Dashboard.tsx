import { motion } from "framer-motion";
import { Sparkles, TrendingUp, Clock, Calendar } from "lucide-react";
import { Card } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";

const features = [
  {
    icon: Sparkles,
    title: "AI Content Generator",
    description: "Create engaging LinkedIn posts with AI in seconds",
    gradient: "from-primary to-secondary",
    path: "/generate",
  },
  {
    icon: Clock,
    title: "Best Time Predictor",
    description: "Find optimal posting times for maximum engagement",
    gradient: "from-secondary to-accent",
    path: "/analytics",
  },
  {
    icon: TrendingUp,
    title: "Analytics Dashboard",
    description: "Track performance and engagement metrics",
    gradient: "from-accent to-primary",
    path: "/analytics",
  },
  {
    icon: Calendar,
    title: "Post Scheduler",
    description: "Schedule your content for optimal reach",
    gradient: "from-primary via-secondary to-accent",
    path: "/schedule",
  },
];

const stats = [
  { label: "Posts Generated", value: "0", change: "+0%" },
  { label: "Engagement Rate", value: "0%", change: "+0%" },
  { label: "Scheduled Posts", value: "0", change: "+0" },
  { label: "Total Reach", value: "0", change: "+0%" },
];

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold mb-2 gradient-text">LinkedIn AutoMarketer AI</h1>
          <p className="text-muted-foreground text-lg">Automate your LinkedIn marketing with AI-powered tools</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="glass p-6 hover:glow-cyan transition-all duration-300">
                <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                <p className="text-3xl font-bold mb-1">{stat.value}</p>
                <p className="text-xs text-primary">{stat.change}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              whileHover={{ scale: 1.02, y: -5 }}
              onClick={() => navigate(feature.path)}
              className="cursor-pointer"
            >
              <Card className="glass-strong p-8 h-full hover:glow-purple transition-all duration-300">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Best Time Widget */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8"
        >
          <Card className="glass-strong p-8">
            <h2 className="text-2xl font-semibold mb-6">Best Times to Post This Week</h2>
            <div className="grid grid-cols-7 gap-4">
              {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, index) => (
                <div key={day} className="text-center">
                  <p className="text-sm text-muted-foreground mb-2">{day}</p>
                  <div className="glass rounded-lg p-3 hover:glow-cyan transition-all duration-300">
                    <p className="text-xs text-primary font-semibold">
                      {index < 5 ? "9:00 AM" : "11:00 AM"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </motion.div>
    </div>
  );
}
