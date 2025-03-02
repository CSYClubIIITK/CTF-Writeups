import { useState, useMemo, useEffect } from "react";
import { Search, PlusCircle } from "lucide-react";
import BlogCard from "./BlogCard";
import DOMPurify from "isomorphic-dompurify";
import axios from "axios";
import CommentSection from "./BlogComments";
import AddBlog from "./AddBlog";
import { BlogCardType} from './types';

const BlogSection = () => {
  const [posts, setPosts] = useState<BlogCardType[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<"date" | "newest" | "popular">("newest");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddBlog, setShowAddBlog] = useState(false);

  useEffect(() => {
    const fetchPosts = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get<any>(`/api/v1/blog/getAll`, {
          headers: {
            "Authorization": `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.data.error) {
          setError(response.data.error);
          return;
        }
        
        // More robust handling of different possible API response structures
        let blogData: BlogCardType[] = [];
        
        if (Array.isArray(response.data)) {
          blogData = response.data;
        } else if (response.data.blogs && Array.isArray(response.data.blogs)) {
          blogData = response.data.blogs;
        } else if (response.data.data && Array.isArray(response.data.data)) {
          blogData = response.data.data;
        } else if (response.data.blog) {
          if (Array.isArray(response.data.blog)) {
            blogData = response.data.blog;
          } else {
            blogData = [response.data.blog];
          }
        } else if (typeof response.data === 'object') {
          // If it's some other shape, try to extract any array property that might contain the blogs
          const possibleArrayProps = Object.entries(response.data)
            .find(([_, value]) => Array.isArray(value));
          
          if (possibleArrayProps) {
            blogData = possibleArrayProps[1] as BlogCardType[];
          }
        }
  
        setPosts(blogData);
        
        if (blogData.length === 0) {
          console.warn("No blog posts found in the API response");
        }
      } catch (error: any) {
        console.error("Error fetching blog posts:", error);
        setError(`Failed to load blog posts: ${error.message || 'Please try again later.'}`);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchPosts();
  }, []);

  const handleBlogAdded = (newBlog: BlogCardType) => {
    setPosts(prevPosts => [newBlog, ...prevPosts]);
    setShowAddBlog(false);
  };

  const filteredPosts = useMemo(() => {
    return posts
      .filter((post) => post.visible !== false) // Handle case where visible might be undefined
      .filter(
        (post) =>
          post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          post.description?.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .sort((a, b) => {
        switch (sortBy) {
          case "newest":
            return new Date(b.date || b.createdAt || '').getTime() - 
                   new Date(a.date || a.createdAt || '').getTime();
          case "popular":
            return (b.likes || 0) - (a.likes || 0);
          case "date":
          default:
            return new Date(a.date || a.createdAt || '').getTime() - 
                   new Date(b.date || b.createdAt || '').getTime();
        }
      });
  }, [posts, searchTerm, sortBy]);

  if (isLoading) {
    return <div className="container mx-auto p-4 text-center">Loading blog posts...</div>;
  }

  if (error) {
    return <div className="container mx-auto p-4 text-center text-red-500">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-gray-100 p-4 rounded-lg">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-semibold text-gray-700">Blog Posts</h2>
          <span className="text-sm bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
            {posts.length}
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search posts..."
              className="w-full md:w-64 pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(DOMPurify.sanitize(e.target.value))}
            />
          </div>
          
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-500 bg-white text-gray-700"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "date" | "newest" | "popular")}
          >
            <option value="newest">Newest First</option>
            <option value="date">Oldest First</option>
            <option value="popular">Most Liked</option>
          </select>
          
          <button
            onClick={() => setShowAddBlog(!showAddBlog)}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors duration-200"
          >
            <PlusCircle size={16} />
            <span>New Post</span>
          </button>
        </div>
      </div>
      
      {/* Add Blog Form (Modal-like) */}
      {showAddBlog && (
        <div className="bg-gray-100 border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-medium text-gray-700 mb-4 border-b border-gray-200 pb-3">Create New Blog Post</h3>
          <AddBlog onBlogAdded={handleBlogAdded} />
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPosts.length > 0 ? (
          filteredPosts.map((post) => (
            <div key={post._id} className="space-y-4">
              <BlogCard
                _id={post._id}
                title={post.title}
                description={post.description}
                visible={post.visible}
                date={post.date || post.createdAt || new Date().toISOString()}
                readTime={post.readTime || "2 min"}
                likes={post.likes || 0}
                comments={post.comments || []}
                userId={post.userId}
                createdAt={post.createdAt}
                updatedAt={post.updatedAt}
              />
              <CommentSection postId={post._id} comments={post.comments || []} />
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12 text-gray-500">
            No posts found matching your search
          </div>
        )}
      </div>
      
      {posts.length === 0 && !isLoading && !error && (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-medium text-gray-700">No Blog Posts Available</h3>
          <p className="text-gray-500 mt-2">There are currently no blog posts to display.</p>
        </div>
      )}
    </div>
  );
};

export default BlogSection;