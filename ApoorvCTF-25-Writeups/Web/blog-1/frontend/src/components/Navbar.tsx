import { useAuth } from "../context/AuthContext";
import {  LogOut, LogIn, Gift } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import RewardsPage from "./DailyRewards";

const Navbar = () => {
  const { user, logout } = useAuth();
  const [isRewardsOpen, setIsRewardsOpen] = useState(false);

  return (
    <nav className="w-full shadow-md px-6 py-3 bg-white">
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold text-gray-800">Blog-1</Link>

        {user ? (
          <div className="flex items-center gap-4">
            <span className="text-gray-800">Hello, {user.username}!</span>
            <button onClick={() => setIsRewardsOpen(true)} className="flex items-center gap-2 text-black">
              <Gift className="w-5 h-5" /> Daily Rewards
            </button>
            <button onClick={logout} className="flex items-center gap-2 text-red-500">
              <LogOut className="w-5 h-5" /> Logout
            </button>
          </div>
        ) : (
          <Link to="/login" className="flex items-center gap-2 text-gray-700">
            <LogIn className="w-5 h-5" /> Login
          </Link>
        )}
      </div>
      {isRewardsOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-transparent bg-opacity-10">
          <div className="bg-white p-6 rounded-lg shadow-lg relative">
            <button className="absolute top-2 right-2 text-gray-600" onClick={() => setIsRewardsOpen(false)}>
              ✕
            </button>
            <RewardsPage />
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
