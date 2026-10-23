"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getAuthToken, setAuthToken } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@northstar.local");
  const [password, setPassword] = useState("Demo123!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(function () {
    if (getAuthToken()) {
      router.replace("/");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await api<{ access_token: string }>("/auth/login", undefined, {
        method: "POST",
        body: JSON.stringify({ email: email, password: password }),
      });

      setAuthToken(result.access_token);
      router.push("/");
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "Unable to sign in.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "radial-gradient(circle at top, #dbeafe 0%, #f8fafc 40%, #e2e8f0 100%)", fontFamily: "sans-serif" }}>
      <div style={{ width: "100%", maxWidth: 420, background: "rgba(255,255,255,0.9)", borderRadius: 24, boxShadow: "0 25px 60px rgba(15, 23, 42, 0.12)", padding: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: 2, color: "#475569", textTransform: "uppercase" }}>Northstar</div>
        <h1 style={{ margin: "12px 0 8px", fontSize: "2rem" }}>Sign in</h1>
        <p style={{ margin: "0 0 24px", color: "#475569" }}>Use the seeded demo account to access the workspace.</p>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 18 }}>
          <label style={{ display: "grid", gap: 8 }}>
            <span style={{ fontWeight: 600 }}>Email</span>
            <input value={email} onChange={function (event) { setEmail(event.target.value); }} type="email" required style={{ border: "1px solid #cbd5e1", borderRadius: 12, padding: "12px 14px", fontSize: 16 }} />
          </label>

          <label style={{ display: "grid", gap: 8 }}>
            <span style={{ fontWeight: 600 }}>Password</span>
            <input value={password} onChange={function (event) { setPassword(event.target.value); }} type="password" required style={{ border: "1px solid #cbd5e1", borderRadius: 12, padding: "12px 14px", fontSize: 16 }} />
          </label>

          {error ? <div style={{ color: "#b91c1c", background: "#fef2f2", borderRadius: 12, padding: "10px 12px" }}>{error}</div> : null}

          <button type="submit" disabled={loading} style={{ border: "none", borderRadius: 12, background: "#0f172a", color: "white", padding: "12px 16px", cursor: "pointer", fontWeight: 700, opacity: loading ? 0.7 : 1 }}>
            {loading ? "Signing in?" : "Continue"}
          </button>
        </form>

        <div style={{ marginTop: 20, color: "#64748b", fontSize: 14 }}>Demo user: admin@northstar.local / Demo123!</div>
      </div>
    </main>
  );
}
