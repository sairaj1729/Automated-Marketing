import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

export default function LinkedInCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const handleLinkedInCallback = async () => {
      // Check if user is authenticated with our app
      const userToken = localStorage.getItem("token");
      if (!userToken) {
        toast.error("Not logged in", {
          description: "Please log in to the application first",
        });
        navigate("/login");
        return;
      }

      const code = searchParams.get("code");
      const error = searchParams.get("error");

      if (error) {
        toast.error("LinkedIn connection failed", {
          description: error,
        });
        navigate("/settings");
        return;
      }

      if (!code) {
        toast.error("Invalid LinkedIn callback", {
          description: "No authorization code received",
        });
        navigate("/settings");
        return;
      }

      try {
        // Get user authentication token
        const userToken = localStorage.getItem("token");
        
        // Exchange code for access token
        const backendUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BACKEND_URL || "http://localhost:3000";
        const response = await fetch(`${backendUrl}/api/v1/linkedin/callback`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${userToken}`,
          },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          throw new Error("Failed to exchange code for token");
        }

        const data = await response.json();
        
        // Store the access token, refresh token, member URN, and profile data in localStorage
        localStorage.setItem("linkedin_access_token", data.access_token);
        localStorage.setItem("linkedin_member_urn", data.member_urn);
        
        // Store refresh token if provided
        if (data.refresh_token) {
          localStorage.setItem("linkedin_refresh_token", data.refresh_token);
        }
        
        // Store expiration time if provided
        if (data.expires_in) {
          const expiryTime = Date.now() + (data.expires_in * 1000);
          localStorage.setItem("linkedin_expiry_time", expiryTime.toString());
        }
        
        // Store profile information if available
        if (data.profile) {
          localStorage.setItem("linkedin_user_name", data.profile.name || "LinkedIn User");
          localStorage.setItem("linkedin_user_headline", data.profile.headline || "Professional");
          if (data.profile.picture) {
            localStorage.setItem("linkedin_user_avatar", data.profile.picture);
          }
        }
        
        toast.success("LinkedIn connected successfully", {
          description: "You can now post to LinkedIn",
        });
        
        // Redirect to settings page
        navigate("/settings");
      } catch (err) {
        console.error("LinkedIn callback error:", err);
        toast.error("LinkedIn connection failed", {
          description: "Failed to connect your LinkedIn account",
        });
        navigate("/settings");
      }
    };

    handleLinkedInCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold mb-2">Connecting LinkedIn...</h2>
        <p className="text-muted-foreground">Please wait while we connect your LinkedIn account</p>
        <Button 
          onClick={() => navigate("/settings")} 
          variant="outline" 
          className="mt-4"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}