import { Router, Request, Response } from "express";
import { Blog } from "../models/blogModel";
import authenticateToken from "../middlewares";
import mongoose from "mongoose";
import { body, param, validationResult } from "express-validator";
import xss from "xss";
import rateLimit from "express-rate-limit";

export const CommentRouter = Router();

const commentLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: "Too many comments from this IP, please try again later"
});

const validateCommentInput = [
  param('id').isMongoId().withMessage('Invalid blog ID format'),
  body('text').trim().isLength({ min: 1, max: 1000 }).escape()
    .withMessage('Comment must be between 1 and 1000 characters')
];

CommentRouter.post(
  "/:id", 
  authenticateToken, 
  commentLimiter,
  validateCommentInput,
  async (req: Request, res: Response): Promise<void> => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(400).json({ errors: errors.array() });
        return;
      }

      const blogId = req.params.id;
      const { text } = req.body;
      const user = (req as any).user;

      const blog = await Blog.findById(blogId);
      if (!blog) {
        res.status(404).json({ error: "Blog not found" });
        return;
      }

      const newComment = {
        _id: new mongoose.Types.ObjectId(),
        text: xss(text),
        author: user.username,
        userId: user.userId,
        date: new Date(),
      };

      blog.comments.push(newComment);
      await blog.save();

      res.status(201).json({ 
        message: "Comment added", 
        comment: newComment 
      });
    } catch (err) {
      console.error("❌ Error adding comment:", err);
      res.status(500).json({ error: "Failed to add comment" });
    }
  }
);

CommentRouter.get(
  "/:id",
  param('id').isMongoId().withMessage('Invalid blog ID format'),
  async (req: Request, res: Response): Promise<void> => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(400).json({ errors: errors.array() });
        return;
      }

      const blogId = req.params.id;
      
      const blog = await Blog.findById(blogId).select('comments').lean();
      
      if (!blog) {
        res.status(404).json({ error: "Blog not found" });
        return;
      }
      
      res.status(200).json({ comments: blog.comments || [] });
    } catch (err) {
      console.error("❌ Error fetching comments:", err);
      res.status(500).json({ error: "Failed to fetch comments" });
    }
  }
);


export default CommentRouter;