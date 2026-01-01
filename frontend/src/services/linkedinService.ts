// LinkedIn service for handling LinkedIn API interactions

class LinkedInService {
  private baseUrl = "https://api.linkedin.com/v2";

  /**
   * Post content to LinkedIn
   */
  async postContent(
    accessToken: string,
    memberUrn: string,
    content: string,
    imageUrl?: string
  ): Promise<{ success: boolean; message: string; linkedinPostId?: string }> {
    try {
      // Prepare the post payload
      const payload = {
        author: memberUrn,
        lifecycleState: "PUBLISHED",
        specificContent: {
          "com.linkedin.ugc.ShareContent": {
            shareCommentary: { text: content },
            shareMediaCategory: imageUrl ? "IMAGE" : "NONE"
          }
        },
        visibility: {
          "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
      };

      // Add image if provided
      if (imageUrl) {
        (payload.specificContent as any)["com.linkedin.ugc.ShareContent"].media = [
          {
            status: "READY",
            description: { text: "Image for post" },
            media: imageUrl,
            title: { text: "Image" }
          }
        ];
      }

      // Make the API request
      const response = await fetch(`${this.baseUrl}/ugcPosts`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${accessToken}`,
          "X-Restli-Protocol-Version": "2.0.0",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      // Check if the request was successful
      if (response.ok) {
        const responseData = await response.json();
        const linkedinPostId = responseData.id || "";

        return {
          success: true,
          message: "Post published to LinkedIn successfully",
          linkedinPostId
        };
      } else {
        const errorText = await response.text();
        return {
          success: false,
          message: `Failed to post to LinkedIn. Status: ${response.status} - ${errorText}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error posting to LinkedIn: ${error instanceof Error ? error.message : "Unknown error"}`
      };
    }
  }

  /**
   * Get engagement metrics for a LinkedIn post
   */
  async getPostEngagement(
    accessToken: string,
    postUrn: string
  ): Promise<{ success: boolean; message?: string; metrics?: any }> {
    try {
      // Ensure we have a proper URN format
      if (!postUrn.startsWith("urn:li:share:")) {
        postUrn = `urn:li:share:${postUrn}`;
      }

      // Extract just the ID part for the API call
      const postId = postUrn.replace("urn:li:share:", "");
      
      // URL encode the post ID to handle special characters
      const encodedPostId = encodeURIComponent(postId);

      // Use the correct endpoint for social actions
      const url = `${this.baseUrl}/socialActions/${encodedPostId}`;

      const response = await fetch(url, {
        headers: {
          "Authorization": `Bearer ${accessToken}`,
          "X-Restli-Protocol-Version": "2.0.0"
        }
      });

      // Check if the request was successful
      if (response.ok) {
        const responseData = await response.json();

        // Parse engagement metrics from response
        const metrics = {
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          impressions: 0,
          engagementRate: 0.0
        };

        // Extract likes count if available
        if (responseData.likesSummary) {
          metrics.likes = responseData.likesSummary.aggregatedTotalLikes || 0;
        }

        // Extract comments count if available
        if (responseData.commentsSummary) {
          metrics.comments = responseData.commentsSummary.aggregatedTotalComments || 0;
        }

        return {
          success: true,
          metrics
        };
      } else if (response.status === 404) {
        // Post not found, return zeros
        return {
          success: true,
          metrics: {
            views: 0,
            likes: 0,
            comments: 0,
            shares: 0,
            impressions: 0,
            engagementRate: 0.0
          }
        };
      } else {
        const errorText = await response.text();
        return {
          success: false,
          message: `Failed to fetch engagement metrics. Status: ${response.status} - ${errorText}`,
          metrics: {
            views: 0,
            likes: 0,
            comments: 0,
            shares: 0,
            impressions: 0,
            engagementRate: 0.0
          }
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error fetching engagement metrics: ${error instanceof Error ? error.message : "Unknown error"}`,
        metrics: {
          views: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          impressions: 0,
          engagementRate: 0.0
        }
      };
    }
  }
}

// Export singleton instance
export const linkedinService = new LinkedInService();