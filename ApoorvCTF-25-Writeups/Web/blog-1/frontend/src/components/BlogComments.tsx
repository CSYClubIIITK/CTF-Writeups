import { useState } from "react";
import axios from "axios";
import DOMPurify from "isomorphic-dompurify";
import { Comment } from "./types";

interface CommentSectionProps {
  postId: string;
  comments: Comment[];
}

const CommentSection: React.FC<CommentSectionProps> = ({ postId, comments }) => {
  const [newComment, setNewComment] = useState("");
  const [localComments, setLocalComments] = useState<Comment[]>(comments);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAllComments, setShowAllComments] = useState(false);
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) return;
    setIsSubmitting(true);
    
    try {
      const response = await axios.post(`/api/v1/blog/comment/${postId}`,{ text: DOMPurify.sanitize(newComment),},{
        headers: {
          "Authorization": `Bearer ${localStorage.getItem('token')}`}
        },
      );
      
      if (response.data.error) {
        setError(response.data.error);
        return;
      }
      
      const updatedComments = response.data.blog?.comments || 
        (response.data.comment ? [...localComments, response.data.comment] : localComments);
      
      setLocalComments(updatedComments);
      setNewComment("");
    } catch (error) {
      setError("Failed to post comment");
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const displayedComments = showAllComments ? localComments : localComments.slice(0, 2);
  
  return (
    <div className="pt-2 border-t">
      <h4 className="text-base font-medium mb-2">Comments ({localComments.length})</h4>
      
      {displayedComments.map((comment) => (
        <div key={comment._id} className="mb-2 bg-gray-50 p-2 rounded">
          <div className="flex justify-between mb-1">
            <span className="font-medium text-sm">{comment.author}</span>
            <span className="text-xs text-gray-500">{formatDate(comment.date)}</span>
          </div>
          <p className="text-sm">{comment.text}</p>
        </div>
      ))}
      
      {localComments.length > 2 && (
        <button
          onClick={() => setShowAllComments(!showAllComments)}
          className="text-sm text-blue-600 hover:underline mb-2"
        >
          {showAllComments ? "Show less" : `Show all ${localComments.length} comments`}
        </button>
      )}
      
      <div className="mt-2">
        <textarea
          placeholder="Add a comment..."
          className="w-full p-2 border rounded text-sm focus:ring-1 focus:ring-blue-500"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          rows={2}
        />
        
        {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
        
        <button
          onClick={handleSubmitComment}
          disabled={isSubmitting || !newComment.trim()}
          className="mt-2 px-3 py-1 rounded-sm bg-stone-800 text-white text-sm hover:bg-gray-700 disabled:bg-gray-400"
        >
          {isSubmitting ? "Posting..." : "Submit"}
        </button>
      </div>
    </div>
  );
};

export default CommentSection;