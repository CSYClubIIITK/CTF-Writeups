import { useState, useEffect, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // ✅ Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/blog");
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    try {
      const res = await fetch(`/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Invalid email or password");

      login(data.token);
      alert("✅ Login successful!");
      navigate("/blog"); // ✅ Redirect to blog after login
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-6 shadow-md rounded w-96">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">Welcome Back</h2>
        
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <input
          className="border p-2 w-full mb-2 rounded"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="border p-2 w-full mb-4 rounded"
          type="password"
          placeholder="Password (6+ characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button className="bg-black text-white px-4 py-2 w-full rounded hover:bg-gray-800 transition">
          Login
        </button>

        <p className="text-center mt-3 text-sm text-gray-600">
          Don't have an account?{" "}
          <button
            type="button"
            className="text-black hover:underline"
            onClick={() => navigate("/register")}
          >
            Register here
          </button>
        </p>
      </form>
    </div>
  );
};

export default Login;
