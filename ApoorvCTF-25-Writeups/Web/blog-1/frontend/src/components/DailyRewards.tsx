import  { useState, useEffect } from 'react';
import { BookOpen } from 'lucide-react';
import axios from 'axios';

const RewardsPage = () => {
  const [blogData, setBlogData] = useState({
    blogCount: 0,
    requiredBlogs: 5,
    message: ''
  });
  const [loading, setLoading] = useState(true);
  const [error] = useState(null);

  // Fetch blog count from API
  useEffect(() => {
    const fetchBlogData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/v2/gift`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        setBlogData({
          blogCount: response.data.blogCount || 0,
          requiredBlogs: 5,
          message: response.data.message || ''
        });
      } catch (err) {
        console.error('Error fetching blog data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBlogData();
  }, []);

  if (loading) {
    return <div className="text-center py-6">Loading...</div>;
  }

  if (error) {
    return <div className="text-center py-6 text-red-600">{error}</div>;
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg">
      <div className="flex items-center justify-center gap-3 mb-4">
        <BookOpen className="w-6 h-6 text-stone-950" />
        <h2 className="text-xl font-bold">Blog Rewards</h2>
      </div>
      
      <div className="text-center mb-4">
        <p className="text-lg font-semibold">
          {blogData.blogCount >= blogData.requiredBlogs 
            ? "You can claim your reward!" 
            : `Write ${blogData.requiredBlogs - blogData.blogCount} more post${blogData.requiredBlogs - blogData.blogCount !== 1 ? 's' : ''} to claim your reward`}
        </p>
      </div>
      
      <div className="mb-4 bg-gray-200 rounded-full h-4 overflow-hidden">
        <div 
          className="h-full bg-gray-900 transition-all duration-500"
          style={{ width: `${Math.min(100, (blogData.blogCount / blogData.requiredBlogs) * 100)}%` }}
        ></div>
      </div>
      
      <div className="flex justify-between text-sm text-gray-600 mb-6">
        <span>0/{blogData.requiredBlogs}</span>
        <span>{blogData.blogCount}/{blogData.requiredBlogs}</span>
      </div>
      
      {blogData.message && (
        <div className="p-1 rounded-lg text-center">
          {blogData.message}
        </div>
      )}
      
    </div>
  );
};

export default RewardsPage;