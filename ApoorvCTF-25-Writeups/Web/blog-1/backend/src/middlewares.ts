import { error } from "console";
import {Request, Response, NextFunction } from "express";

import jwt from "jsonwebtoken";

const authenticateToken = (req: Request, res: Response, next: NextFunction): void => {

    const JWT_SECRET = process.env.JWT_SECRET!;
    const authHeader = req.headers["authorization"];
    const token = authHeader?.split(" ")[1];
  
    if (!token) {
      res.status(401).json({ message: "Access Denied" });
      return; 
    }
  
    jwt.verify(token, JWT_SECRET, (err, user) => {
      if (err) {
        res.status(403).json({ message: "Invalid Token" });
        return; 
      }
      (req as any).user = user;
      next(); 
    });
};


export default authenticateToken