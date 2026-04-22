"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserSummary } from "@/lib/api";

const emotionColors: Record<string, string> = {
  ansiedad: "bg-amber-400",
  estres: "bg-orange-400",
  tristeza: "bg-blue-400",
  neutral: "bg-slate-400",
  positivo: "bg-emerald-400",
  crisis: "bg-red-500",
};

type Summary = {
  user: { name: string; email: string };
  total_messages: number;
  emotion_counts: Record<string, number>;
  predominant_recent: string[];
  weekly_frequency: Record<string, number>;
  emotion_timeline: Array<{ emotion: string; created_at: string }>;
};

export default function ProfilePage() {
  const router = useRouter();
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return void router.push("/login");

    getUserSummary(token).then(setSummary);
  }, [router]);

  const totalEmotionCount = useMemo(() => {
    if (!summary) return 0;
    return Object.values(summary.emotion_counts).reduce((acc, value) => acc + Number(value), 0);
  }, [summary]);

  if (!summary) return <p className="p-6">Cargando perfil emocional...</p>;

  return (
    <main className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-5xl space-y-5">
        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">Perfil emocional</h1>
          <p className="mt-2 text-slate-600">{summary.user.name} · {summary.user.email}</p>
          <p className="mt-1 text-sm text-slate-500">Mensajes analizados: {summary.total_messages}</p>
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <section className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="font-semibold text-slate-900">Distribución de emociones</h2>
            <div className="mt-4 space-y-3">
              {Object.entries(summary.emotion_counts).map(([emotion, count]) => {
                const pct = totalEmotionCount > 0 ? Math.round((count / totalEmotionCount) * 100) : 0;
                return (
                  <div key={emotion}>
                    <div className="mb-1 flex justify-between text-sm text-slate-700">
                      <span>{emotion}</span>
                      <span>{count} ({pct}%)</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100">
                      <div
                        className={`h-2 rounded-full ${emotionColors[emotion] || "bg-slate-500"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="rounded-2xl border bg-white p-6 shadow-sm">
                <h2 className="font-semibold text-slate-900">Frecuencia semanal</h2>
                <div className="mt-4 space-y-2 text-sm text-slate-700">
                  {Object.keys(summary.weekly_frequency || {}).length === 0 && <p>Sin actividad en la última semana.</p>}
                  {Object.entries(summary.weekly_frequency || {}).map(([day, value]) => (
                    <div key={day} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                      <span>{day}</span>
                      <span className="font-medium">{value} mensajes</span>
                    </div>
                  ))}
                </div>
          </section>
        </div>

        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900">Últimas emociones predominantes</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {(summary.predominant_recent || []).map((emotion, idx) => (
              <span key={`${emotion}-${idx}`} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">
                {emotion}
              </span>
            ))}
          </div>            

          <h3 className="mt-6 font-semibold text-slate-900">Evolución temporal</h3>
            <div className="mt-3 space-y-2">
                {(summary.emotion_timeline || []).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm">
                    <span>{item.emotion}</span>
                    <span className="text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
          </section>
          
        <button onClick={() => router.push("/chat")} className="rounded-lg border bg-white px-4 py-2 hover:bg-slate-50">
          Volver al chat
        </button>        
      </div>
    </main>
  );
}