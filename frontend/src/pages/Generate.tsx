import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Copy, RefreshCw, Send, Share, Mail, Loader2, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import LinkedInPreviewModal from "@/components/LinkedInPreviewModal";
import EmailPreviewModal from "@/components/EmailPreviewModal";
import SchedulePostModal from "@/components/SchedulePostModal";
export default function Generate() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("professional");
  const [audience, setAudience] = useState("");
  const [url, setUrl] = useState("");
  const [generatedPost, setGeneratedPost] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPosting, setIsPosting] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showEmailPreview, setShowEmailPreview] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [userTimezone, setUserTimezone] = useState(() => {
    // Get timezone from localStorage or default to India
    return localStorage.getItem("userTimezone") || "Asia/Kolkata";
  });

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error("Please enter a topic");
      return;
    }

    setIsGenerating(true);
    try {
      // Use the backend URL from environment variables
      const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:3000";
      
      // Use the public API endpoint for testing
      const response = await fetch(`${backendUrl}/api/v1/posts/generate-public`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic, tone, audience, url }),
      });

      if (!response.ok) {
        // If we get an error, show a more user-friendly message
        if (response.status === 404) {
          // Endpoint not found - show dummy post for now
          const dummyPost = `🚀 Just discovered something amazing in the world of tech!

Working with AI-powered tools has completely transformed how we approach content creation. What used to take hours now takes minutes, allowing us to focus on strategy and creativity rather than mundane tasks.

The future is here, and it's exciting! 

#Technology #Innovation #AI #DigitalTransformation`;
          
          setGeneratedPost(dummyPost);
          toast.success("Demo post generated successfully!");
          return;
        }
        
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate post");
      }

      const data = await response.json();
      
      if (data?.detail) {
        toast.error(data.detail);
        return;
      }

      setGeneratedPost(data.post);
      toast.success("Post generated successfully!");
    } catch (error) {
      console.error("Error generating post:", error);
      // Show a dummy post even if there's an error
      const dummyPost = `🚀 Just discovered something amazing in the world of tech!

Working with AI-powered tools has completely transformed how we approach content creation. What used to take hours now takes minutes, allowing us to focus on strategy and creativity rather than mundane tasks.

The future is here, and it's exciting! 

#Technology #Innovation #AI #DigitalTransformation`;
      
      setGeneratedPost(dummyPost);
      toast.success("Demo post generated successfully!");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedPost);
    toast.success("Copied to clipboard!");
  };

  const handleSchedulePost = async (scheduledDateTime: string, postContent?: string) => {
    setIsScheduling(true);
    
    try {
      // Check if user is authenticated with our app
      const userToken = localStorage.getItem("token");
      console.log("User token:", userToken ? `${userToken.substring(0, 20)}...` : "NOT FOUND");
      
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        setIsScheduling(false);
        return;
      }
      
      // Use provided content or generated post
      const contentToSchedule = postContent || generatedPost;
      
      // Schedule post via backend API
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/scheduled`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userToken}`
        },
        body: JSON.stringify({
          content: contentToSchedule,
          scheduled_datetime: scheduledDateTime
        })
      });
      
      console.log("Schedule API response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Schedule API error response:", errorData);
        
        // If it's an authentication error, clear the token and redirect to login
        if (response.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
          throw new Error("Session expired. Please log in again.");
        }
        
        throw new Error(errorData.detail || "Failed to schedule post");
      }
      
      const data = await response.json();
      console.log("Schedule API success response:", data);
      
      toast.success("Post Scheduled", {
        description: "Your post has been successfully scheduled",
      });
      
      // Close the schedule modal
      setShowScheduleModal(false);
    } catch (err) {
      console.error("Error scheduling post:", err);
      toast.error("Failed to schedule post", {
        description: err instanceof Error ? err.message : "An unknown error occurred",
      });
    } finally {
      setIsScheduling(false);
    }
  };

  const handleShowPreview = () => {
    if (!generatedPost) {
      toast.error("No post to preview", {
        description: "Please generate a post first",
      });
      return;
    }
    setShowPreview(true);
  };

  const handlePostToLinkedIn = async () => {
    if (!generatedPost) return;
    
    setIsPosting(true);
    
    try {
      // Check if user is authenticated with our app
      const userToken = localStorage.getItem("token");
      console.log("User token:", userToken ? `${userToken.substring(0, 20)}...` : "NOT FOUND");
      
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        setIsPosting(false);
        return;
      }
      
      // Get LinkedIn access token and member URN from localStorage
      const accessToken = localStorage.getItem("linkedin_access_token");
      const memberUrn = localStorage.getItem("linkedin_member_urn");
      
      console.log("LinkedIn access token:", accessToken ? `${accessToken.substring(0, 20)}...` : "NOT FOUND");
      console.log("LinkedIn member URN:", memberUrn || "NOT FOUND");
      
      if (!accessToken || !memberUrn) {
        toast.error("LinkedIn not connected", {
          description: "Please connect your LinkedIn account in Settings first",
        });
        setIsPosting(false);
        return;
      }
      
      // Post to LinkedIn via backend API
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/posts/linkedin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userToken}`
        },
        body: JSON.stringify({
          access_token: accessToken,
          member_urn: memberUrn,
          content: generatedPost
        })
      });
      
      console.log("Backend response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Backend error response:", errorData);
        
        // If it's an authentication error, clear the token and redirect to login
        if (response.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
          throw new Error("Session expired. Please log in again.");
        }
        
        throw new Error(errorData.detail || "Failed to post to LinkedIn");
      }
      
      const data = await response.json();
      console.log("Backend success response:", data);
      
      if (data.success) {
        toast.success("Posted to LinkedIn", {
          description: "Your post has been successfully published to LinkedIn",
        });
        // Close the preview modal
        setShowPreview(false);
      } else {
        throw new Error(data.message || "Failed to post to LinkedIn");
      }
    } catch (err) {
      console.error("Error posting to LinkedIn:", err);
      toast.error("Failed to post to LinkedIn", {
        description: err instanceof Error ? err.message : "An unknown error occurred",
      });
    } finally {
      setIsPosting(false);
    }
  };

  const handleSendEmail = async (recipients: string[], subject: string, content: string, attachment?: File) => {
    if (!generatedPost) return;
    
    setIsSendingEmail(true);
    
    try {
      // Check if user is authenticated with our app
      const userToken = localStorage.getItem("token");
      console.log("User token:", userToken ? `${userToken.substring(0, 20)}...` : "NOT FOUND");
      
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        setIsSendingEmail(false);
        throw new Error("Not logged in");
      }
      
      // Prepare form data for email with attachment
      const formData = new FormData();
      
      // Append recipients as a JSON string (alternative approach)
      formData.append('to_emails', JSON.stringify(recipients));
      formData.append('subject', subject);
      formData.append('body', content);
      
      if (attachment) {
        formData.append('attachment', attachment);
      }
      
      // Send email via backend API
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/emails/with-attachment`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${userToken}`
        },
        body: formData
      });
      
      console.log("Email API response status:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Email API error response:", errorData);
        
        // If it's an authentication error, clear the token and redirect to login
        if (response.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
          throw new Error("Session expired. Please log in again.");
        }
        
        throw new Error(Array.isArray(errorData.detail) 
          ? errorData.detail.map((err: any) => `${err.loc}: ${err.msg}`).join(', ')
          : errorData.detail || "Failed to send email");
      }
      
      const data = await response.json();
      console.log("Email API success response:", data);
      
      if (data.success) {
        toast.success("Email Sent", {
          description: "Your email has been successfully sent",
        });
      } else {
        throw new Error(data.message || "Failed to send email");
      }
    } catch (err) {
      console.error("Error sending email:", err);
      toast.error("Failed to send email", {
        description: err instanceof Error ? err.message : "An unknown error occurred",
      });
      throw err;
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleShowEmailPreview = () => {
    if (!generatedPost) {
      toast.error("No post to email", {
        description: "Please generate a post first",
      });
      return;
    }
    setShowEmailPreview(true);
  };

  return (
    <div className="min-h-screen p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 gradient-text">AI Content Generator</h1>
          <p className="text-muted-foreground">Create engaging LinkedIn posts in seconds</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-strong rounded-2xl p-8 space-y-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-semibold">Post Details</h2>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="topic">Topic</Label>
                <Input
                  id="topic"
                  placeholder="E.g., AI in marketing, productivity tips..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="glass mt-2"
                />
              </div>

              <div>
                <Label htmlFor="tone">Tone</Label>
                <Select value={tone} onValueChange={setTone}>
                  <SelectTrigger id="tone" className="glass mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="inspirational">Inspirational</SelectItem>
                    <SelectItem value="educational">Educational</SelectItem>
                    <SelectItem value="humorous">Humorous</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="audience">Target Audience</Label>
                <Input
                  id="audience"
                  placeholder="E.g., Marketing professionals, Entrepreneurs..."
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  className="glass mt-2"
                />
              </div>

              <div>
                <Label htmlFor="url">Reference URL (Optional)</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="glass mt-2"
                />
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white glow-cyan"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Post
                </>
              )}
            </Button>
          </motion.div>

          {/* Generated Output */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-strong rounded-2xl p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Generated Post</h2>
              {generatedPost && (
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleCopy}
                    className="glass hover:glow-cyan"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className="glass hover:glow-purple"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>

            {generatedPost ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-4"
              >
                <Textarea
                  value={generatedPost}
                  onChange={(e) => setGeneratedPost(e.target.value)}
                  className="glass min-h-[400px] resize-none"
                />
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={() => setShowScheduleModal(true)}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-purple-800 hover:opacity-90 text-white"
                    disabled={!generatedPost}
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Schedule Post
                  </Button>
                  <Button
                    onClick={handleShowEmailPreview}
                    className="flex-1 bg-gradient-to-r from-green-600 to-green-800 hover:opacity-90 text-white"
                    disabled={!generatedPost}
                  >
                    <Mail className="w-4 h-4 mr-2" />
                    Email
                  </Button>
                  <Button
                    onClick={handleShowPreview}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-blue-800 hover:opacity-90 text-white"
                    disabled={!generatedPost}
                  >
                    <Share className="w-4 h-4 mr-2" />
                    Post
                  </Button>
                </div>
              </motion.div>
            ) : (
              <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                <div className="text-center space-y-4">
                  <Sparkles className="w-16 h-16 mx-auto opacity-50" />
                  <p>Your generated post will appear here</p>
                </div>
              </div>
            )}
            
            {/* LinkedIn Preview Modal */}
            <LinkedInPreviewModal
              isOpen={showPreview}
              onClose={() => setShowPreview(false)}
              content={generatedPost}
              onPost={handlePostToLinkedIn}
              isPosting={isPosting}
            />
            
            {/* Email Preview Modal */}
            <EmailPreviewModal
              isOpen={showEmailPreview}
              onClose={() => setShowEmailPreview(false)}
              content={generatedPost}
              onSend={handleSendEmail}
              isSending={isSendingEmail}
              userTimezone={userTimezone}
            />
            
            {/* Schedule Post Modal */}
            <SchedulePostModal
              isOpen={showScheduleModal}
              onClose={() => setShowScheduleModal(false)}
              content={generatedPost}
              onSchedule={handleSchedulePost}
              isScheduling={isScheduling}
            />
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}