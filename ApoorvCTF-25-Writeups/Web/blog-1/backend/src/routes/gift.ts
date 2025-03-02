import { Router, Request, Response } from "express";
import { Blog } from "../models/blogModel";
import authenticateToken from "../middlewares"; 

export const GiftRouter = Router();


GiftRouter.get('/', authenticateToken, async (req: Request, res: Response): Promise<void> => {
    try {
        const userId = (req as any).user.userId;
        
        if (!userId) {
            res.status(401).json({ message: "Unauthorized" });
            return;
        }
        
        const blogCount = await Blog.countDocuments({ userId });
        
        const requiredBlogs = 5;
        if (blogCount >= requiredBlogs) {
            res.status(200).json({ 
                message: "Congratulations! You received a special gift : https://youtu.be/WePNs-G7puA?si=DOUFW9vAgUKdClxX",
                blogCount
            });
        }
        else {
            const remaining = requiredBlogs - blogCount;
            res.status(200).json({ message: `Keep going! Write ${remaining} more blog${remaining !== 1 ? 's' : ''} to get a gift.`,blogCount: blogCount});
        }
    } 
    catch (error) {
        console.error("Error in gift eligibility check:", error);
        res.status(500).json({ message: "Failed to check gift eligibility" });
    }
});