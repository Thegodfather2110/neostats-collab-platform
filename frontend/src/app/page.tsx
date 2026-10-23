"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken } from "../lib/api";

const cards = [
  { label: "Active projects", value: "08", detail: "Across launch, research, and design" },
  { label: "Pending tasks", value: "24", detail: "4 require review" },
  { label: "Team velocity", value: "92%", detail: "Compared with last week" },
  { label: "Launch date", value: "Nov 12", detail: "3 milestones left" },
];

const tasks = [
  { title: "Finalize launch messaging", owner: "Q4 Product Launch", status: "In progress" },
  { title: "QA onboarding flow", owner: "Q4 Product Launch", status: "To do" },
  { title: "Share research synthesis", owner: "Customer Discovery", status: "In progress" },
  { title: "Approve release checklist", owner: "Q4 Product Launch", status: "Done" },
];

const milestones = [
  { name: "Launch readiness", value: 82 },
  { name: "Customer feedback", value: 68 },
  { name: "Website refresh", value: 91 },
];

function getStatusStyle(status: string) {
  if (status === "Done") {
    return { background: "#dcfce7", color: "#166534" };
  }
  if (status === "In progress") {
    return { background: "#dbeafe", color: "#1d4ed8" };
  }
  return { background: "#fef3c7", color: "#92400e" };
}

export default function Home() {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(function () {
    const token = getAuthToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", fontFamily: "sans-serif", background: "#f1f5f9", color: "#0f172a" }}>
        <div>Checking workspace access?</div>
      </main>
    );
  }

  return (
    <main style={{ minHeight: "100vh", padding: "32px", background: "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)", color: "#0f172a", fontFamily: "sans-serif" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "28px" }}>
          <div>
            <div style={{ fontSize: 12, letterSpacing: 2, textTransform: "uppercase", color: "#475569" }}>Studio North</div>
            <h1 style={{ fontSize: "2.25rem", margin: "8px 0 0" }}>Project dashboard</h1>
          </div>
          <button
            onClick={function () { localStorage.removeItem("northstar_token"); router.replace("/login"); }}
            style={{ border: "none", background: "#0f172a", color: "white", borderRadius: 999, padding: "10px 16px", cursor: "pointer" }}
          >
            Sign out
          </button>
        </header>

        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20, marginBottom: 28 }}>
          {cards.map(function (card) {
            return (
              <div key={card.label} style={{ background: "white", borderRadius: 18, padding: 20, boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)" }}>
                <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: 1.2 }}>{card.label}</div>
                <div style={{ fontSize: "2rem", fontWeight: 700, marginTop: 12 }}>{card.value}</div>
                <div style={{ marginTop: 8, color: "#475569" }}>{card.detail}</div>
              </div>
            );
          })}
        </section>

        <section style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 20 }}>
          <div style={{ background: "white", borderRadius: 18, padding: 20, boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)" }}>
            <h2 style={{ marginTop: 0 }}>Recent tasks</h2>
            <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 14 }}>
              {tasks.map(function (task) {
                return (
                  <li key={task.title} style={{ padding: "14px 16px", border: "1px solid #e2e8f0", borderRadius: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>{task.title}</div>
                      <div style={{ color: "#64748b", fontSize: 14 }}>{task.owner}</div>
                    </div>
                    <span style={{ ...getStatusStyle(task.status), borderRadius: 999, padding: "6px 10px", fontSize: 12, fontWeight: 600 }}>{task.status}</span>
                  </li>
                );
              })}
            </ul>
          </div>

          <div style={{ background: "white", borderRadius: 18, padding: 20, boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)" }}>
            <h2 style={{ marginTop: 0 }}>Workspace health</h2>
            {milestones.map(function (entry) {
              return (
                <div key={entry.name} style={{ marginBottom: 18 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span>{entry.name}</span>
                    <strong>{entry.value}%</strong>
                  </div>
                  <div style={{ height: 10, background: "#e2e8f0", borderRadius: 999, overflow: "hidden" }}>
                    <div style={{ width: entry.value + "%", height: "100%", background: "linear-gradient(90deg, #22c55e 0%, #38bdf8 100%)" }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}
