import { User, Mail } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const ProfileSection = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-md mx-auto bg-white shadow-md rounded-lg p-6 mt-8">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
          <User className="w-8 h-8 text-gray-600" />
        </div>
        <h2 className="text-xl font-semibold text-gray-800">{user.username}</h2>
      </div>

      <div className="mt-4 flex items-center gap-2 text-gray-700">
        <Mail className="w-5 h-5 text-gray-500" />
        <span>{user.username}</span> {/* Dummy Email */}
      </div>
    </div>
  );
};

export default ProfileSection;
