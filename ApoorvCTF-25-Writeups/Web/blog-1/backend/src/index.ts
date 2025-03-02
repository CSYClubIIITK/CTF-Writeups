import express, { Application, Request, Response, NextFunction } from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import cors from "cors";
import morgan from "morgan";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { body, validationResult } from "express-validator";
import { BlogRouter } from "./routes/blog";
import User from "./models/userModel";
import authenticateToken from "./middlewares";
import { GiftRouter } from "./routes/gift";
import { ActualGiftRouter } from "./routes/actualgift";

dotenv.config();

const app: Application = express();
const PORT: number = Number(process.env.PORT) || 3000;
const MONGO_URI: string = process.env.MONGO_URI as string;
const JWT_SECRET: string = process.env.JWT_SECRET || "supersecretkey";

app.use(helmet());
app.use(cors({ origin: process.env.CLIENT_URL || "*" }));
app.use(express.json());
app.use(morgan("dev"));

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 75,
  message: { message: "Too many requests, please try again later." },
});

app.use(limiter);

mongoose
  .connect(MONGO_URI)
  .then(() => ("✅ MongoDB Connected"))
  .catch((err) => {
    console.error("❌ MongoDB Connection Error:", err);
    process.exit(1);
  });

app.post(
  "/api/register",
  [
    body("username").isString().trim().notEmpty(),
    body("email").isEmail().normalizeEmail(),
    body("password").isLength({ min: 6 }),
  ],
  async (req: Request, res: Response): Promise<any> => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

    try {
      const { username, email, password } = req.body;

      const existingUser = await User.findOne({ email });
      if (existingUser) return res.status(400).json({ message: "User already exists" });

      const hashedPassword = await bcrypt.hash(password, 10);
      const newUser = new User({ username, email, password: hashedPassword });
      await newUser.save();

      res.status(201).json({ message: "User registered successfully" });
    } catch (error) {
      res.status(500).json({ message: "Server Error" });
    }
  }
);

app.post(
  "/api/login",
  [body("email").isEmail().normalizeEmail(), body("password").isString().notEmpty()],
  async (req: Request, res: Response): Promise<any> => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

    try {
      const { email, password } = req.body;

      const user = await User.findOne({ email });
      if (!user) return res.status(400).json({ message: "Invalid credentials" });

      const isMatch = await bcrypt.compare(password, user.password);
      if (!isMatch) return res.status(400).json({ message: "Invalid credentials" });

      const token = jwt.sign({ userId: user._id, username: user.username }, JWT_SECRET, {
        expiresIn: "1h",
      });

      res.json({ message: "Login successful", token });
    } catch (error) {
      res.status(500).json({ message: "Server Error" });
    }
  }
);

app.get("/api/dashboard", authenticateToken, (req: Request, res: Response) => {
  res.json({ message: `Welcome, ${(req as any).user.username}!` });
});

app.use("/api/v1/blog", authenticateToken, BlogRouter);
app.use("/api/v2/gift", authenticateToken, GiftRouter);
app.use("/api/v1/gift", authenticateToken, ActualGiftRouter);

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error("🔥 Error:", err.message);
  res.status(500).json({ message: "Internal Server Error" });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
