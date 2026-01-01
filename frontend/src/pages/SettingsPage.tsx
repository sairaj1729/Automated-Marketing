import { motion } from "framer-motion";
import { Settings, Key, User, Bell, Clock } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useEffect, useState } from "react";

export default function SettingsPage() {
  const [linkedinConnected, setLinkedinConnected] = useState(false);
  const [connectionExpiry, setConnectionExpiry] = useState<number | null>(null);

  useEffect(() => {
    // Check if LinkedIn is already connected
    const checkConnectionStatus = () => {
      const accessToken = localStorage.getItem("linkedin_access_token");
      const memberUrn = localStorage.getItem("linkedin_member_urn");
      const expiryTime = localStorage.getItem("linkedin_expiry_time");
      
      if (accessToken && memberUrn) {
        setLinkedinConnected(true);
        if (expiryTime) {
          setConnectionExpiry(parseInt(expiryTime, 10));
        }
      } else {
        setLinkedinConnected(false);
        setConnectionExpiry(null);
      }
    };
    
    checkConnectionStatus();
    

    
    // Set up interval to check connection status periodically
    const interval = setInterval(checkConnectionStatus, 60000); // Check every minute
    
    return () => clearInterval(interval);
  }, []);

  const getConnectionExpiryText = () => {
    if (!connectionExpiry) return "";
    
    const now = Date.now();
    const expiry = connectionExpiry;
    const timeLeft = expiry - now;
    
    if (timeLeft <= 0) {
      return "Expired";
    }
    
    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) {
      return `Expires in ${days}d ${hours}h`;
    } else if (hours > 0) {
      return `Expires in ${hours}h ${minutes}m`;
    } else {
      return `Expires in ${minutes} minutes`;
    }
  };

  const handleConnectLinkedIn = () => {
    // Redirect to LinkedIn OAuth using backend endpoint
    const redirectUri = encodeURIComponent(import.meta.env.VITE_LINKEDIN_REDIRECT_URI || "http://localhost:8080/callback");
    const scope = encodeURIComponent("openid profile email w_member_social");
    
    // Use backend endpoint that has the client ID configured
    const baseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BACKEND_URL || "http://localhost:3000";
    window.location.href = `${baseUrl}/api/v1/linkedin/auth?redirect_uri=${redirectUri}&scope=${scope}`;
  };

  const handleDisconnectLinkedIn = () => {
    localStorage.removeItem("linkedin_access_token");
    localStorage.removeItem("linkedin_member_urn");
    localStorage.removeItem("linkedin_expiry_time");
    localStorage.removeItem("linkedin_refresh_token");
    setLinkedinConnected(false);
    setConnectionExpiry(null);
  };



  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 gradient-text">Settings</h1>
          <p className="text-muted-foreground">Manage your account and preferences</p>
        </div>

        <div className="space-y-6">
          {/* LinkedIn Connection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="glass-strong p-8">
              <div className="flex items-center gap-2 mb-6">
                <User className="w-6 h-6 text-primary" />
                <h2 className="text-2xl font-semibold">LinkedIn Connection</h2>
              </div>

              <div className="space-y-4">
                <div className="glass p-4 rounded-lg flex items-center justify-between">
                  <div>
                    <p className="font-semibold">LinkedIn Account</p>
                    <p className="text-sm text-muted-foreground">
                      {linkedinConnected ? "Connected" : "Not connected"}
                    </p>
                    {linkedinConnected && connectionExpiry && (
                      <div className="flex items-center mt-1">
                        <Clock className="w-4 h-4 mr-1 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {getConnectionExpiryText()}
                        </span>
                      </div>
                    )}
                  </div>
                  {linkedinConnected ? (
                    <Button 
                      variant="destructive" 
                      onClick={handleDisconnectLinkedIn}
                    >
                      Disconnect
                    </Button>
                  ) : (
                    <Button 
                      className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white"
                      onClick={handleConnectLinkedIn}
                    >
                      Connect LinkedIn
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>


          {/* Notifications */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="glass-strong p-8">
              <div className="flex items-center gap-2 mb-6">
                <Bell className="w-6 h-6 text-primary" />
                <h2 className="text-2xl font-semibold">Notifications</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between glass p-4 rounded-lg">
                  <div>
                    <p className="font-semibold">Post Reminders</p>
                    <p className="text-sm text-muted-foreground">Get notified before scheduled posts</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between glass p-4 rounded-lg">
                  <div>
                    <p className="font-semibold">Engagement Alerts</p>
                    <p className="text-sm text-muted-foreground">Notifications for high-performing posts</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between glass p-4 rounded-lg">
                  <div>
                    <p className="font-semibold">Weekly Reports</p>
                    <p className="text-sm text-muted-foreground">Receive weekly performance summaries</p>
                  </div>
                  <Switch />
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}


