import { useState } from "react";
import { Loader, X } from "lucide-react";
import axios from "axios";
import DOMPurify from "isomorphic-dompurify";
import { BlogCardType } from './types';

const AddBlog = ({ onBlogAdded }: { onBlogAdded: (blog: BlogCardType) => void }) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [visible, setVisible] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = () => {
    setTitle("");
    setVisible(true);
    setDescription("");
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    // Validate inputs
    if (!title.trim() || !description.trim()) {
      setError("All fields are required");
      setIsSubmitting(false);
      return;
    }

    try {
      const blogData = {
        title: DOMPurify.sanitize(title),
        description: DOMPurify.sanitize(description),
        visible: visible,
        date: new Date().toISOString(),
      };

      const response = await axios.post<{ blog: BlogCardType }>(
       `/api/v1/blog/addBlog`,
        blogData,
        {
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      
      if (response.data && response.data.blog) {
        onBlogAdded(response.data.blog);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error: any) {
      console.error("Error creating blog post:", error);
      setError(error.response?.data?.message || error.message || "Failed to create blog post");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      {error && (
        <div className="mb-4 p-3 bg-gray-200 text-gray-700 border-l-4 border-red-500 rounded flex items-center gap-2">
          <X size={16} className="text-red-500" /> 
          <span>{error}</span>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-600 mb-1">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500"
            placeholder="Enter blog title"
            disabled={isSubmitting}
          />
        </div>
        
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-600 mb-1">
            Short Description
          </label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500"
            placeholder="Brief summary of your blog post"
            disabled={isSubmitting}
          />
        </div>
        
        <div>
          <div className="flex items-center gap-2">
            <input
              id="visible"
              type="checkbox"
              checked={visible}
              onChange={(e) => setVisible(e.target.checked)}
              className="h-4 w-4 text-gray-600 focus:ring-gray-500 border-gray-300 rounded"
              disabled={isSubmitting}
            />
            <label htmlFor="visible" className="text-sm font-medium text-gray-600">
              Make blog post visible
            </label>
          </div>
          <p className="text-xs text-gray-500 mt-1 ml-6">
            Uncheck to save as draft and publish later
          </p>
        </div>
        
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={resetForm}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50"
            disabled={isSubmitting}
          >
            Reset
          </button>
          <button
            type="submit"
            className="px-5 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-400 flex items-center gap-2"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader size={16} className="animate-spin" /> Publishing...
              </>
            ) : (
              "Publish Post"
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddBlog;