import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import BlogSection from "./components/BlogSection";
import ProfileSection from "./components/ProfileSection";
import Login from "./components/Login";
import Register from "./components/Register";
import ProtectedRoute from "./components/ProtectedRoute";

const App = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* 🔹 Protected Routes Now Use Outlet */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<BlogSection />} />
            <Route path="/profile" element={<ProfileSection />} />
          </Route>

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
