import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useEffect, useState } from "react";

interface LinkedInPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onPost: () => void;
  isPosting: boolean;
}

interface LinkedInProfile {
  name: string;
  headline: string | null;
  profile_picture_url: string | null;
}

export default function LinkedInPreviewModal({
  isOpen,
  onClose,
  content,
  onPost,
  isPosting
}: LinkedInPreviewModalProps) {
  const [profile, setProfile] = useState<LinkedInProfile | null>(null);
  
  // Get user info from localStorage (fallback values)
  const fallbackName = localStorage.getItem("linkedin_user_name") || "Your Name";
  const fallbackAvatar = localStorage.getItem("linkedin_user_avatar") || "";
  const fallbackHeadline = localStorage.getItem("linkedin_user_headline") || "Professional";
  
  // Use profile data or fallback values
  const userName = profile?.name || fallbackName;
  const userAvatar = profile?.profile_picture_url || fallbackAvatar;
  const userHeadline = profile?.headline || fallbackHeadline;
  
  useEffect(() => {
    const fetchLinkedInProfile = async () => {
      try {
        const accessToken = localStorage.getItem("linkedin_access_token");
        if (!accessToken) return;
        
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/linkedin/profile`, {
          headers: {
            "Authorization": `Bearer ${accessToken}`
          }
        });
        
        if (response.ok) {
          const profileData = await response.json();
          setProfile(profileData);
        }
      } catch (error) {
        console.error("Failed to fetch LinkedIn profile:", error);
        // Use fallback values
      }
    };
    
    if (isOpen) {
      fetchLinkedInProfile();
    }
  }, [isOpen]);

  // Extract actual post content from AI response
  const extractPostContent = (rawContent: string): string => {
    // Look for content between separators
    if (rawContent.includes('---')) {
      const parts = rawContent.split('---');
      if (parts.length > 1) {
        return parts[parts.length - 1].trim();
      }
    }
    
    // Remove common introductory phrases
    const lines = rawContent.split('\n');
    const startIndex = lines.findIndex(line => 
      !line.toLowerCase().includes('here') && 
      !line.toLowerCase().includes('below') && 
      !line.toLowerCase().includes('post') && 
      !line.toLowerCase().includes('linkedin')
    );
    
    return lines.slice(Math.max(0, startIndex)).join('\n').trim();
  };
  
  // Extract and format the actual post content
  const actualPostContent = extractPostContent(content);
  
  // Format the content to handle line breaks
  const formattedContent = actualPostContent.split('\n').map((line, index) => (
    <span key={index}>
      {line}
      <br />
    </span>
  ));

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto p-0 bg-gray-100">
        {/* LinkedIn-style compose header */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-300 p-4 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded flex items-center justify-center bg-blue-600 text-white mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Create a post</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-4">
          {/* LinkedIn post preview */}
          <div className="bg-white rounded-lg border border-gray-300 shadow-sm">
            {/* Post header */}
            <div className="p-4 flex items-start gap-3">
              <Avatar className="w-12 h-12">
                <AvatarImage src={userAvatar} />
                <AvatarFallback className="bg-gray-200 text-gray-700 font-semibold">
                  {userName.charAt(0)}
                </AvatarFallback>
              </Avatar>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1">
                  <h3 className="font-semibold text-gray-900">{userName}</h3>
                  <span className="text-gray-500">•</span>
                  <span className="text-gray-500 text-sm">{userHeadline}</span>
                </div>
                <div className="flex items-center mt-1">
                  <div className="flex items-center text-xs text-gray-500">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <span>Anyone</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Post content */}
            <div className="px-4 pb-4">
              <div className="whitespace-pre-wrap text-gray-800 text-base leading-relaxed">
                {formattedContent}
              </div>
            </div>
            
            {/* Divider */}
            <div className="border-t border-gray-200 mx-4"></div>
            
            {/* Engagement preview */}
            <div className="p-4 flex items-center justify-between text-gray-500">
              <div className="flex items-center text-xs font-medium">
                <span>👍</span>
                <span className="ml-1">Like</span>
              </div>
              <div className="flex items-center text-xs font-medium">
                <span>💬</span>
                <span className="ml-1">Comment</span>
              </div>
              <div className="flex items-center text-xs font-medium">
                <span>🔄</span>
                <span className="ml-1">Repost</span>
              </div>
              <div className="flex items-center text-xs font-medium">
                <span>📤</span>
                <span className="ml-1">Send</span>
              </div>
            </div>
          </div>
          
          {/* Action buttons */}
          <div className="mt-4 flex justify-end gap-3">
            <Button 
              variant="outline" 
              onClick={onClose}
              className="px-4 py-2"
            >
              Cancel
            </Button>
            <Button 
              onClick={onPost} 
              disabled={isPosting}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isPosting ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                  Posting...
                </>
              ) : (
                "Post"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}