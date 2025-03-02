import { Router, Request, Response } from "express";
import { Blog } from "../models/blogModel";
import authenticateToken from "../middlewares";
import User from "../models/userModel";
import { body, validationResult } from "express-validator";
import xss from "xss";
import CommentRouter from "./comments";

export const BlogRouter = Router();

BlogRouter.use('/api/comment',authenticateToken,CommentRouter);

const validateBlogInput = [
  body('title').trim().isLength({ min: 3, max: 100 }).escape()
    .withMessage('Title must be between 3 and 100 characters'),
  body('description').trim().isLength({ min: 10, max: 5000 })
    .withMessage('Description must be between 10 and 5000 characters'),
  body('visible').optional().isBoolean()
    .withMessage('Visible must be a boolean value')
];

BlogRouter.get("/getAll", async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user.userId;
    const blogs = await Blog.find({ visible: true,userId })
      .select("title description date readTime likes comments userId")
      .populate("userId", "username email")
      .lean();
    
    if (!blogs.length) {
      res.status(200).json({ blogs: [] });
      return;
    }
    
    res.status(200).json(blogs);
  } catch (err) {
    res.status(500).json({ error: "An error occurred while fetching blogs" });
  }
});

BlogRouter.post(
  "/addBlog",
  authenticateToken,
  validateBlogInput,
  async (req: Request, res: Response): Promise<void> => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(400).json({ errors: errors.array() });
        return;
      }
      const { title, description, visible } = req.body;
      const userId = (req as any).user.userId;

      const user = await User.findById(userId).select("_id").lean();
      if (!user) {
        res.status(404).json({ message: "User not found" });
        return;
      }

      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      const userBlogToday = await Blog.findOne({
        userId,
        date: { $gte: today, $lt: tomorrow },
      }).lean();

      await new Promise((resolve) => setTimeout(resolve, 3000));

      const userBlogAfterDelay = await Blog.findOne({
        userId,
        date: { $gte: today, $lt: tomorrow },
      });

      if (userBlogToday || userBlogAfterDelay) {
        res.status(400).json({ message: "Only one blog per day is allowed!" });
        return;
      }

      // **4️⃣ Now insert the blog**
      const newBlog = new Blog({
        title: xss(title),
        description: xss(description),
        visible: visible ?? true,
        date: new Date(),
        readTime: Math.ceil(description.split(" ").length / 200),
        likes: 0,
        comments: [],
        userId: userId,
      });

      await newBlog.save();

      res.status(201).json({
        message: "Blog added successfully",
        blog: {
          id: newBlog._id,
          title: newBlog.title,
          date: newBlog.date,
          readTime: newBlog.readTime,
        },
      });
    } catch (err) {
      if (!res.headersSent) {
        res.status(500).json({ error: "An error occurred while creating the blog" });
      }
    }
  }
);


BlogRouter.get(
  "/userDailyCount", 
  authenticateToken, 
  async (req: Request, res: Response): Promise<void> => {
    try {
      const userId = (req as any).user.userId;
      
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const count = await Blog.countDocuments({
        userId,
        date: { $gte: today, $lt: tomorrow }
      });
      
      res.status(200).json({ count });
    } catch (err) {
      res.status(500).json({ error: "An error occurred" });
    }
  }
);