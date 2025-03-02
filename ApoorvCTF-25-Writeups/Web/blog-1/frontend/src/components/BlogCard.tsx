import React from "react";
import { Clock, Heart, MessageSquare } from "lucide-react";
import { BlogCardType } from "./types";

const BlogCard: React.FC<BlogCardType> = ({
  title,
  description,
  date,
  readTime,
  likes,
  comments = [],
}) => {
  // Format date for better display
  const formattedDate = date 
    ? new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "No date";

  // Safe HTML rendering with fallback
  const renderDescription = () => {
    try {
      return <div className="text-gray-600 overflow-y-auto max-h-24 text-sm" dangerouslySetInnerHTML={{ __html: description || "" }}/>;
    } catch (e) {
      return <div className="text-gray-600 overflow-y-auto max-h-24 text-sm">{description || ""}</div>;
    }
  };

  return (
    <div className="border rounded-lg shadow-sm hover:shadow-md transition-shadow h-64 flex flex-col">
      <div className="p-3 flex flex-col h-full">
        <h3 className="text-lg font-semibold mb-1 text-gray-800 line-clamp-1">{title || "Untitled"}</h3>
        <div className="flex items-center text-xs text-gray-500 mb-2">
          <span>{formattedDate}</span>
          <div className="flex items-center ml-2">
            <Clock className="w-3 h-3 mr-1" />
            <span>{readTime || "2m"}</span>
          </div>
        </div>
        {renderDescription()}
        <div className="flex items-center pt-2 border-t mt-auto">
          <div className="flex items-center text-gray-500 text-xs">
            <Heart className="w-3 h-3 mr-1" />
            <span>{likes || 0}</span>
          </div>
          <div className="flex items-center text-gray-500 text-xs ml-3">1
            <MessageSquare className="w-3 h-3 mr-1" />
            <span>{comments?.length || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogCard;