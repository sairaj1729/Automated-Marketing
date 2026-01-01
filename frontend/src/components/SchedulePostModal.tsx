import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, Save, Globe } from "lucide-react";
import { toast } from "sonner";

interface ScheduledPost {
  id: string;
  content: string;
  scheduled_datetime: string;
  status: string;
  timezone?: string;
  error_message?: string;
}

interface SchedulePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onSchedule: (scheduledDateTime: string, postContent?: string, timezone?: string) => Promise<void>;
  isScheduling: boolean;
  existingPost?: ScheduledPost | null;
  onUpdate?: (postId: string, scheduledDateTime: string, postContent: string, timezone?: string) => Promise<void>;
  onDelete?: (postId: string) => Promise<void>;
  isUpdating?: boolean;
  isDeleting?: boolean;
}

export default function SchedulePostModal({ 
  isOpen, 
  onClose, 
  content,
  onSchedule,
  isScheduling,
  existingPost,
  onUpdate,
  onDelete,
  isUpdating = false,
  isDeleting = false
}: SchedulePostModalProps) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata"); // Default to India
  const [postContent, setPostContent] = useState(content);
  
  // Reset form when modal opens or existingPost changes
  useEffect(() => {
    if (isOpen) {
      if (existingPost) {
        setPostContent(existingPost.content);
        // Convert UTC time from backend to the original timezone for display
        const utcDate = new Date(existingPost.scheduled_datetime);
        const timezoneToUse = existingPost.timezone || 'Asia/Kolkata';
        // Format date and time in the original timezone
        setDate(utcDate.toLocaleDateString('sv-SE', { timeZone: timezoneToUse })); // 'sv-SE' gives YYYY-MM-DD format
        setTime(utcDate.toLocaleTimeString('sv-SE', { timeZone: timezoneToUse, hour12: false }).substring(0, 5)); // HH:MM format
        // For existing posts, use the post's timezone if available
        if (existingPost.timezone) {
          setTimezone(existingPost.timezone);
        }
      } else {
        setPostContent(content);
        // Set default date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        setDate(tomorrow.toISOString().split('T')[0]);
        // Set default time to 9:00 AM
        setTime("09:00");
        // Use user's saved timezone or default to India
        const savedTimezone = localStorage.getItem("userTimezone") || "Asia/Kolkata";
        setTimezone(savedTimezone);
      }
    }
  }, [isOpen, existingPost, content]);
  
  const handleAction = async () => {
    if (!date || !time) {
      toast.error("Please select both date and time");
      return;
    }
    
    // Create datetime string with selected timezone using proper timezone handling
    // We'll send the date/time and timezone separately to let the backend handle conversion
    const scheduledDateTime = `${date}T${time}`;
    
    if (existingPost && onUpdate) {
      await onUpdate(existingPost.id, scheduledDateTime, postContent, timezone);
    } else {
      await onSchedule(scheduledDateTime, postContent, timezone);
    }
  };
  
  const handleDelete = async () => {
    if (existingPost && onDelete) {
      if (window.confirm("Are you sure you want to delete this scheduled post?")) {
        await onDelete(existingPost.id);
      }
    }
  };
  
  const getTitle = () => {
    if (existingPost) {
      if (existingPost.status === 'failed') {
        return "Reschedule Failed Post";
      }
      return "Edit Scheduled Post";
    }
    return "Schedule Post";
  };
  
  const getActionButtonText = () => {
    if (existingPost) {
      if (existingPost.status === 'failed') {
        return "Reschedule Post";
      }
      return "Update Post";
    }
    return "Schedule Post";
  };
  
  const getActionButtonIcon = () => {
    if (existingPost) return <Save className="w-4 h-4 mr-2" />;
    return null;
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{getTitle()}</DialogTitle>
        </DialogHeader>
        
        {existingPost && existingPost.status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
            <p className="text-red-800 text-sm">
              <strong>Failed Post:</strong> This post failed to publish. Rescheduling it will reset its status to pending.
            </p>
          </div>
        )}
        
        <div className="space-y-6 py-4">
          {/* Content Preview */}
          <div>
            <Label>Post Content</Label>
            <Textarea
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              className="mt-2 min-h-[150px]"
            />
          </div>
          
          {/* Date Selection */}
          <div>
            <Label htmlFor="date">Date</Label>
            <div className="mt-2">
              <input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm pl-10 w-full"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Click to open calendar and select date</p>
          </div>
          
          {/* Time Selection */}
          <div>
            <Label htmlFor="time">Time</Label>
            <div className="mt-2">
              <input
                id="time"
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm pl-10 w-full"
                step="300"
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Select the time for your scheduled post (5-minute intervals)</p>
          </div>
          
          {/* Timezone Selection */}
          <div>
            <Label htmlFor="timezone">Timezone</Label>
            <div className="mt-2">
              <Select value={timezone} onValueChange={setTimezone}>
                <SelectTrigger className="w-full">
                  <Globe className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Asia/Kolkata">India (IST - UTC+5:30)</SelectItem>
                  <SelectItem value="America/New_York">New York (EST - UTC-5:00)</SelectItem>
                  <SelectItem value="America/Los_Angeles">Los Angeles (PST - UTC-8:00)</SelectItem>
                  <SelectItem value="Europe/London">London (GMT - UTC+0:00)</SelectItem>
                  <SelectItem value="Europe/Paris">Paris (CET - UTC+1:00)</SelectItem>
                  <SelectItem value="Asia/Tokyo">Tokyo (JST - UTC+9:00)</SelectItem>
                  <SelectItem value="Australia/Sydney">Sydney (AEDT - UTC+11:00)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Select your preferred timezone for scheduling</p>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-between gap-3 pt-4">
            {existingPost && onDelete && (
              <Button 
                variant="destructive" 
                onClick={handleDelete}
                disabled={isDeleting}
                className="flex-1"
              >
                {isDeleting ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete
                  </>
                )}
              </Button>
            )}
            <div className="flex gap-3 ml-auto">
              <Button variant="outline" onClick={onClose} disabled={isScheduling || isUpdating || isDeleting}>
                Cancel
              </Button>
              <Button 
                onClick={handleAction} 
                disabled={isScheduling || isUpdating || !date || !time}
                className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white"
              >
                {(isScheduling || isUpdating) ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                    {existingPost ? "Updating..." : "Scheduling..."}
                  </>
                ) : (
                  <>
                    {getActionButtonIcon()}
                    {getActionButtonText()}
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
