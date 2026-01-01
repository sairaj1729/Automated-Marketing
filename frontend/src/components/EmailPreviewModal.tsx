import { useState, useRef } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Send, Paperclip, X } from "lucide-react";
import { toast } from "sonner";

interface EmailPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onSend: (recipients: string[], subject: string, content: string, attachment?: File) => Promise<void>;
  isSending: boolean;
  userTimezone?: string; // Add user timezone prop
}

export default function EmailPreviewModal({ 
  isOpen, 
  onClose, 
  content,
  onSend,
  isSending,
  userTimezone = "Asia/Kolkata" // Default to India as per requirements
}: EmailPreviewModalProps) {
  const [recipients, setRecipients] = useState<string[]>([""]);
  const [subject, setSubject] = useState("LinkedIn Post Content");
  const [attachment, setAttachment] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleRecipientChange = (index: number, value: string) => {
    const newRecipients = [...recipients];
    newRecipients[index] = value;
    setRecipients(newRecipients);
  };

  const addRecipient = () => {
    setRecipients([...recipients, ""]);
  };

  const removeRecipient = (index: number) => {
    if (recipients.length > 1) {
      const newRecipients = recipients.filter((_, i) => i !== index);
      setRecipients(newRecipients);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachment(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const removeAttachment = () => {
    setAttachment(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSend = async () => {
    // Validate recipients
    const validRecipients = recipients.filter(email => email.trim() !== "");
    if (validRecipients.length === 0) {
      toast.error("Please enter at least one recipient");
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    for (const email of validRecipients) {
      if (!emailRegex.test(email)) {
        toast.error(`Invalid email format: ${email}`);
        return;
      }
    }

    if (!subject.trim()) {
      toast.error("Please enter a subject");
      return;
    }

    try {
      await onSend(validRecipients, subject, content, attachment || undefined);
      // Close modal on success
      onClose();
      // Reset form
      setRecipients([""]);
      setSubject("LinkedIn Post Content");
      setAttachment(null);
      setPreviewUrl(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Failed to send email:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Email Preview</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Recipients */}
          <div>
            <Label>Recipients</Label>
            {recipients.map((recipient, index) => (
              <div key={index} className="flex gap-2 mt-2">
                <Input
                  type="email"
                  placeholder="recipient@example.com"
                  value={recipient}
                  onChange={(e) => handleRecipientChange(index, e.target.value)}
                  className="flex-1"
                />
                {recipients.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => removeRecipient(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addRecipient}
              className="mt-2"
            >
              + Add Recipient
            </Button>
          </div>
          
          {/* Subject */}
          <div>
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="mt-2"
            />
          </div>
          
          {/* Attachment */}
          <div>
            <Label>Attachment (Optional)</Label>
            <div className="mt-2 flex items-center gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept="image/*,.pdf,.doc,.docx"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip className="h-4 w-4 mr-2" />
                Attach File
              </Button>
              {attachment && (
                <div className="flex items-center gap-2 bg-muted px-3 py-1 rounded-md">
                  <span className="text-sm truncate max-w-[150px]">{attachment.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={removeAttachment}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
            {previewUrl && attachment?.type.startsWith('image/') && (
              <div className="mt-2">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-h-32 rounded-md object-contain"
                />
              </div>
            )}
          </div>
          
          {/* Enhanced Email Preview */}
          <div className="border rounded-lg overflow-hidden bg-white">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-gray-900">{subject || 'No subject'}</h3>
                  <div className="text-sm text-gray-500 mt-1">
                    <span className="font-medium">To:</span> {recipients.filter(r => r.trim() !== '').join(', ') || 'No recipients'}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date().toLocaleString('en-IN', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: userTimezone })}
                </div>
              </div>
            </div>
            <div className="p-4">
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-gray-800">{content}</pre>
              </div>
              
              {/* Attachment Preview */}
              {attachment && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Paperclip className="h-4 w-4" />
                    <span>Attachment: {attachment.name}</span>
                  </div>
                  {previewUrl && attachment?.type.startsWith('image/') && (
                    <div className="mt-2 max-w-xs border rounded overflow-hidden">
                      <img 
                        src={previewUrl} 
                        alt="Attachment preview" 
                        className="w-full object-contain max-h-40"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              onClick={handleSend} 
              disabled={isSending}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSending ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Email
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}