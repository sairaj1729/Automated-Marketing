import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Calendar, Clock, Plus, Edit, Trash2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import SchedulePostModal from "@/components/SchedulePostModal";
import { useNavigate } from "react-router-dom";

// Helper function to convert UTC datetime from backend to original timezone for display
const formatDateTimeWithTimezone = (datetimeStr: string, timezone: string, format: 'date' | 'time' | 'datetime' = 'datetime') => {
  try {
    // The datetime from backend is stored in UTC, but comes without timezone indicator
    // We need to ensure it's treated as UTC, not as local time
    
    // Parse the datetime string as UTC by appending 'Z' to force UTC interpretation
    const utcDateTimeStr = datetimeStr.endsWith('Z') ? datetimeStr : `${datetimeStr}Z`;
    const utcDate = new Date(utcDateTimeStr);
    
    // Now convert from UTC to the target timezone
    const options: Intl.DateTimeFormatOptions = {
      timeZone: timezone,
    };
    
    if (format === 'date' || format === 'datetime') {
      options.year = 'numeric';
      options.month = '2-digit';
      options.day = '2-digit';
    }
    
    if (format === 'time' || format === 'datetime') {
      options.hour = '2-digit';
      options.minute = '2-digit';
      options.hour12 = false; // Use 24-hour format
    }
    
    return utcDate.toLocaleString('en-IN', options);
  } catch (error) {
    console.error('Error formatting datetime with timezone:', error);
    // Fallback: try to handle the datetime string as UTC
    try {
      const date = new Date(`${datetimeStr}Z`);
      const options: Intl.DateTimeFormatOptions = {
        timeZone: timezone,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      };
      return date.toLocaleString('en-IN', options);
    } catch (fallbackError) {
      // Last resort: show original value
      console.error('Fallback also failed:', fallbackError);
      return datetimeStr;
    }
  }
};

interface ScheduledPost {
  id: string;
  content: string;
  scheduled_datetime: string;
  status: string;
  timezone?: string;
  error_message?: string;
}

export default function Schedule() {
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [editingPost, setEditingPost] = useState<ScheduledPost | null>(null);
  const [userTimezone, setUserTimezone] = useState(() => {
    // Get timezone from localStorage or default to India
    return localStorage.getItem("userTimezone") || "Asia/Kolkata";
  });
  const navigate = useNavigate();
  
  // Fetch scheduled posts
  useEffect(() => {
    // Check if user is authenticated
    const userToken = localStorage.getItem("token");
    if (!userToken) {
      toast.error("Authentication required", {
        description: "Please log in to access the scheduler",
      });
      navigate("/login");
      return;
    }
    
    fetchScheduledPosts();
  }, [navigate]);
  
  const fetchScheduledPosts = async () => {
    try {
      const userToken = localStorage.getItem("token");
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        navigate("/login");
        return;
      }
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/scheduled`, {
        headers: {
          "Authorization": `Bearer ${userToken}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Session expired", {
            description: "Please log in again",
          });
          navigate("/login");
          return;
        }
        throw new Error(`Failed to fetch scheduled posts: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setScheduledPosts(data);
    } catch (error) {
      console.error("Error fetching scheduled posts:", error);
      toast.error("Failed to load scheduled posts", {
        description: error instanceof Error ? error.message : "Unknown error occurred"
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleScheduleNewPost = () => {
    setEditingPost(null);
    setShowScheduleModal(true);
  };
  
  const handleEditPost = (post: ScheduledPost) => {
    setEditingPost(post);
    setShowScheduleModal(true);
  };
  
  const handleDeletePost = async (postId: string) => {
    try {
      const userToken = localStorage.getItem("token");
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        navigate("/login");
        return;
      }
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/scheduled/${postId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${userToken}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Session expired", {
            description: "Please log in again",
          });
          navigate("/login");
          return;
        }
        throw new Error(`Failed to delete scheduled post: ${response.status} ${response.statusText}`);
      }
      
      toast.success("Post deleted successfully");
      fetchScheduledPosts(); // Refresh the list
    } catch (error) {
      console.error("Error deleting scheduled post:", error);
      toast.error("Failed to delete scheduled post", {
        description: error instanceof Error ? error.message : "Unknown error occurred"
      });
    }
  };
  
  const handleSchedulePost = async (scheduledDateTime: string, postContent?: string, timezone?: string) => {
    try {
      const userToken = localStorage.getItem("token");
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        navigate("/login");
        return;
      }
      
      // Save user timezone preference
      if (timezone) {
        localStorage.setItem("userTimezone", timezone);
        setUserTimezone(timezone);
      }
      
      const content = postContent || "";
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/scheduled?timezone=${encodeURIComponent(timezone || 'Asia/Kolkata')}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userToken}`
        },
        body: JSON.stringify({
          content,
          scheduled_datetime: scheduledDateTime,
          timezone: timezone || 'Asia/Kolkata'
        })
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Session expired", {
            description: "Please log in again",
          });
          navigate("/login");
          return;
        }
        throw new Error(`Failed to schedule post: ${response.status} ${response.statusText}`);
      }
      
      toast.success("Post scheduled successfully");
      setShowScheduleModal(false);
      fetchScheduledPosts(); // Refresh the list
    } catch (error) {
      console.error("Error scheduling post:", error);
      toast.error("Failed to schedule post", {
        description: error instanceof Error ? error.message : "Unknown error occurred"
      });
    }
  };
  
  const handleUpdatePost = async (postId: string, scheduledDateTime: string, postContent: string, timezone?: string) => {
    try {
      const userToken = localStorage.getItem("token");
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        navigate("/login");
        return;
      }
      
      // Check if this is a failed post being updated
      const isFailedPost = editingPost?.status === 'failed';
      
      // Save user timezone preference
      if (timezone) {
        localStorage.setItem("userTimezone", timezone);
        setUserTimezone(timezone);
      }
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/scheduled/${postId}?timezone=${encodeURIComponent(timezone || 'Asia/Kolkata')}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userToken}`
        },
        body: JSON.stringify({
          content: postContent,
          scheduled_datetime: scheduledDateTime,
          timezone: timezone || 'Asia/Kolkata'
        })
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Session expired", {
            description: "Please log in again",
          });
          navigate("/login");
          return;
        }
        throw new Error(`Failed to update scheduled post: ${response.status} ${response.statusText}`);
      }
      
      // Show appropriate success message
      if (isFailedPost) {
        toast.success("Failed post rescheduled successfully", {
          description: "The post status has been updated to pending"
        });
      } else {
        toast.success("Post updated successfully");
      }
      
      setShowScheduleModal(false);
      fetchScheduledPosts(); // Refresh the list
    } catch (error) {
      console.error("Error updating scheduled post:", error);
      toast.error("Failed to update scheduled post", {
        description: error instanceof Error ? error.message : "Unknown error occurred"
      });
    }
  };
  
  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2 gradient-text">Post Scheduler</h1>
            <p className="text-muted-foreground">Manage and schedule your LinkedIn posts</p>
          </div>
          <Button 
            className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white glow-cyan"
            onClick={handleScheduleNewPost}
          >
            <Plus className="w-4 h-4 mr-2" />
            Schedule New Post
          </Button>
        </div>

        {/* Calendar View */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Calendar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2"
          >
            <Card className="glass-strong p-8">
              <div className="flex items-center gap-2 mb-6">
                <Calendar className="w-6 h-6 text-primary" />
                <h2 className="text-2xl font-semibold">December 2025</h2>
              </div>

              {/* Simple calendar grid */}
              <div className="grid grid-cols-7 gap-2">
                {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                  <div key={day} className="text-center text-sm text-muted-foreground font-semibold p-2">
                    {day}
                  </div>
                ))}
                {Array.from({ length: 35 }, (_, i) => {
                  const day = i - 2;
                  const isCurrentMonth = day > 0 && day <= 31;
                  
                  // Check if any scheduled posts exist for this day
                  const hasPost = isCurrentMonth && scheduledPosts.some(post => {
                    // Convert UTC time from backend to the original timezone for display
                    const utcDate = new Date(post.scheduled_datetime);
                    const timezoneToUse = post.timezone || userTimezone;
                    const localizedPostDate = new Date(utcDate.toLocaleString("en-US", { timeZone: timezoneToUse }));
                    return localizedPostDate.getDate() === day && 
                           localizedPostDate.getMonth() === 11 && // December (0-indexed)
                           localizedPostDate.getFullYear() === 2025;
                  });

                  return (
                    <motion.div
                      key={i}
                      whileHover={isCurrentMonth ? { scale: 1.05 } : {}}
                      className={`
                        aspect-square rounded-lg flex items-center justify-center text-sm
                        ${isCurrentMonth ? "glass cursor-pointer hover:glow-cyan" : "text-muted-foreground/30"}
                        ${hasPost ? "bg-primary/20 border-2 border-primary glow-cyan" : ""}
                      `}
                    >
                      {isCurrentMonth ? day : ""}
                      {hasPost && (
                        <div className="absolute bottom-1 w-1 h-1 rounded-full bg-primary"></div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </Card>
          </motion.div>

          {/* Scheduled Posts List */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-4"
          >
            <Card className="glass-strong p-6">
              <div className="flex items-center gap-2 mb-6">
                <Clock className="w-6 h-6 text-primary" />
                <h2 className="text-xl font-semibold">Upcoming Posts</h2>
              </div>

              {loading ? (
                <div className="text-center py-12 text-muted-foreground">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                  <p>Loading scheduled posts...</p>
                </div>
              ) : scheduledPosts.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Calendar className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No scheduled posts yet</p>
                  <Button 
                    className="mt-4 bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white"
                    onClick={handleScheduleNewPost}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Schedule Your First Post
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {scheduledPosts.map((post) => (
                    <motion.div
                      key={post.id}
                      whileHover={{ scale: 1.02 }}
                      className="glass p-4 rounded-lg space-y-2"
                    >
                      <p className="text-sm line-clamp-2">{post.content}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDateTimeWithTimezone(post.scheduled_datetime, post.timezone || userTimezone, 'date')}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDateTimeWithTimezone(post.scheduled_datetime, post.timezone || userTimezone, 'time')}
                          <span className="ml-1 text-[10px] bg-muted px-1 rounded">
                            {post.timezone === 'Asia/Kolkata' ? 'IST' : 
                             post.timezone === 'America/New_York' ? 'EST/EDT' : 
                             post.timezone === 'America/Los_Angeles' ? 'PST/PDT' : 
                             post.timezone === 'Europe/London' ? 'GMT/BST' : 
                             post.timezone === 'Europe/Paris' ? 'CET/CEST' : 
                             post.timezone === 'Asia/Tokyo' ? 'JST' : 
                             post.timezone === 'Australia/Sydney' ? 'AEDT/AEST' : 
                             'TZ' }
                          </span>
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${post.status === 'published' ? 'bg-green-100 text-green-800' : post.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {post.status.charAt(0).toUpperCase() + post.status.slice(1)}
                        </span>
                      </div>
                      {post.status === 'failed' && post.error_message && (
                        <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                          Error: {post.error_message}
                        </div>
                      )}
                      <div className="flex gap-2 pt-2">
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          className="flex-1 glass"
                          onClick={() => handleEditPost(post)}
                        >
                          <Edit className="w-3 h-3 mr-1" />
                          Edit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost" 
                          className="flex-1 glass text-destructive"
                          onClick={() => handleDeletePost(post.id)}
                        >
                          <Trash2 className="w-3 h-3 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </Card>
          </motion.div>
        </div>
        
        {/* Schedule Post Modal */}
        <SchedulePostModal
          isOpen={showScheduleModal}
          onClose={() => {
            setShowScheduleModal(false);
            setEditingPost(null);
          }}
          content=""
          onSchedule={handleSchedulePost}
          isScheduling={false}
          existingPost={editingPost}
          onUpdate={handleUpdatePost}
          onDelete={handleDeletePost}
          isUpdating={false}
          isDeleting={false}
        />
      </motion.div>
    </div>
  );
}
