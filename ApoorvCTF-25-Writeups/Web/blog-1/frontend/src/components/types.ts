// Updated frontend interfaces to match backend models

export interface Comment {
    _id: string;               // MongoDB ObjectId as string
    text: string;              // Comment content
    author: string;            // Author name
    userId: string;            // User ID who created the comment
    date: string;              // Date as string for frontend display
}

export interface BlogCardType {
    _id: string;               // Changed from *id to _id to match MongoDB
    title: string;             // Blog title
    description: string;       // Blog content
    visible: boolean;          // Visibility flag
    date: string;              // Date as string for frontend display
    readTime: string;          // Estimated read time
    likes: number;             // Number of likes
    comments: Comment[];       // Array of comments
    userId: string;            // User ID who created the blog
    createdAt?: string;        // Optional timestamp from mongoose
    updatedAt?: string;        // Optional timestamp from mongoose
}

// Interface for creating a new blog (omitting auto-generated fields)
export interface CreateBlogInput {
    title: string;
    description: string;
    visible?: boolean;         // Optional as it has a default value in the backend
}

// Interface for API responses
export interface BlogResponse {
    message: string;
    blog?: BlogCardType;
    error?: string;
}