import mongoose, { Schema, Document, Types } from "mongoose";

export interface IComment {
  _id?: Types.ObjectId;
  text: string;
  author: string;
  userId: Types.ObjectId; 
  date: Date;
}

const CommentSchema = new Schema<IComment>({
  text: { type: String, required: true },
  author: { type: String, required: true },
  userId: { type: Schema.Types.ObjectId, ref: "User", required: true },
  date: { type: Date, required: true },
});

export interface IBlog extends Document {
  title: string;
  description: string;
  visible: boolean;
  date: Date;
  readTime: string;
  likes: number;
  comments: IComment[];
  userId: Types.ObjectId;

}

const BlogSchema = new Schema<IBlog>(
  {
    title: { type: String, required: true },
    description: { type: String, required: true },
    visible: { type: Boolean, default: true },
    date: { type: Date, required: true },
    readTime: { type: String, required: true },
    likes: { type: Number, default: 0 },
    comments: [CommentSchema],
    userId: { type: Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

export const Blog = mongoose.model<IBlog>("Blog", BlogSchema);
