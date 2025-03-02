export const sampleComments = {
    1: [
      {
        id: 1,
        text: "This was an amazing read! Next.js really simplifies development.",
        author: "Alice Johnson",
        date: "2025-02-11",
      },
      {
        id: 2,
        text: "I\'d love a follow-up on API routes in Next.js.",
        author: "Mark Benson",
        date: "2025-02-12",
      },
    ],
    2: [
      {
        id: 3,
        text: "TypeScript has been a game-changer for our team!",
        author: "Sam Carter",
        date: "2025-02-13",
      },
      {
        id: 4,
        text: "Could you explain more about TypeScript generics?",
        author: "Laura Smith",
        date: "2025-02-14",
      },
    ],
    3: [
      {
        id: 5,
        text: "Tailwind CSS makes designing so much faster!",
        author: "John Wick",
        date: "2025-02-16",
      },
    ],
    4: [
      {
        id: 6,
        text: "Great tips on React optimization!",
        author: "Emily Davis",
        date: "2025-02-19",
      },
    ],
};
  
export const samplePosts = [
    {
      id: 2,
      title: "Why TypeScript is Essential for Scalable Projects",
      description:
        "Discover why TypeScript is a game-changer for large-scale projects. Learn about type safety, interfaces, generics, and how they improve development.",
      visible: true,
      date: "2025-02-12",
      readTime: "5 min read",
      likes: 175,
      comments: sampleComments[2], // Correctly assigning the comment array
    },
    {
      id: 3,
      title: "Tailwind CSS Best Practices",
      description:
        "Learn how to structure Tailwind CSS in your projects for maintainability and performance. Explore utility classes, responsive design, and custom configurations.",
      visible: true,
      date: "2025-02-15",
      readTime: "7 min read",
      likes: 143,
      comments: sampleComments[3] || [], // Providing a fallback empty array
    },
    {
      id: 4,
      title: "React Performance Optimization Techniques",
      description:
        "Understand how to optimize your React applications with useMemo, useCallback, React.memo, and other advanced techniques for a smoother user experience.",
      visible: true,
      date: "2025-02-18",
      readTime: "9 min read",
      likes: 220,
      comments: sampleComments[4] || [], // Fallback if no comments exist
    },
  ];