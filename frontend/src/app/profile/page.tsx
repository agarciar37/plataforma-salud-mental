"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserSummary } from "@/lib/api";

const emotionColors: Record<string, string> = {
  ansiedad: "from-amber-300 to-orange-400",
  estres: "from-orange-300 to-red-400",
  tristeza: "from-blue-300 to-sky-500",
  neutral: "from-slate-300 to-slate-500",
  positivo: "from-emerald-300 to-teal-500",
  crisis: "from-red-400 to-rose-600",
};

const emotionLabels: Record<string, string> = {
  ansiedad: "Ansiedad",
  estres: "Estrés",
  tristeza: "Tristeza",
  neutral: "Neutral",
  positivo: "Positivo",
  crisis: "Crisis",
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSummary = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        router.push("/login");
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await getUserSummary(token);
        setSummary(data);
      } catch (err) {
        console.error("Error cargando el perfil:", err);
        setError("No se pudo cargar el perfil emocional. Inténtalo de nuevo.");
      } finally {
        setLoading(false);
      }
    };

    loadSummary();
  }, [router]);

  const totalEmotionCount = useMemo(() => {
    if (!summary) return 0;
    return Object.values(summary.emotion_counts).reduce((sum, value) => sum + value, 0);
  }, [summary]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="rounded-[2rem] border border-white/70 bg-white/85 p-8 text-center shadow-2xl shadow-blue-100/70 backdrop-blur">
          <div className="mx-auto mb-4 h-12 w-12 animate-pulse rounded-2xl bg-blue-100" />
          <p className="font-semibold text-slate-700">Cargando perfil emocional...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-6">
        <div className="mx-auto max-w-2xl rounded-[2rem] border border-red-100 bg-white/90 p-6 shadow-xl shadow-red-100/60 backdrop-blur">
          <h1 className="text-2xl font-black text-slate-950">Perfil emocional</h1>
          <p className="mt-3 rounded-2xl bg-red-50 px-4 py-3 text-red-700">{error}</p>
          <button
            onClick={() => router.push("/chat")}
            className="mt-5 rounded-2xl bg-slate-950 px-4 py-2 font-bold text-white hover:bg-slate-800"
          >
            Volver al chat
          </button>
        </div>
      </main>
    );
  }

  if (!summary) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <p className="rounded-[2rem] bg-white/90 p-6 font-semibold text-slate-600 shadow-xl">
          No hay datos del perfil emocional.
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-6 md:px-6 md:py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="overflow-hidden rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-2xl shadow-blue-100/70 backdrop-blur md:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.25em] text-blue-500">
                Tu evolución
              </p>
              <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-950 md:text-4xl">
                Perfil emocional
              </h1>
              <p className="mt-2 text-slate-600">
                {summary.user.name} · {summary.user.email}
              </p>
            </div>
            <div className="rounded-3xl bg-gradient-to-br from-blue-600 to-violet-600 px-6 py-5 text-white shadow-lg shadow-blue-200">
              <p className="text-sm text-blue-100">Mensajes analizados</p>
              <p className="text-4xl font-black">{summary.total_messages}</p>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <section className="rounded-[1.75rem] border border-white/70 bg-white/85 p-6 shadow-xl shadow-slate-200/60 backdrop-blur">
            <h2 className="text-lg font-black text-slate-950">Distribución de emociones</h2>
            <div className="mt-5 space-y-4">
              {Object.entries(summary.emotion_counts).map(([emotion, count]) => {
                const pct = totalEmotionCount > 0 ? Math.round((count / totalEmotionCount) * 100) : 0;

                return (
                  <div key={emotion} className="rounded-2xl bg-slate-50/80 p-3">
                    <div className="mb-2 flex justify-between text-sm font-semibold text-slate-700">
                      <span>{emotionLabels[emotion] || emotion}</span>
                      <span>
                        {count} ({pct}%)
                      </span>
                    </div>
                    <div className="h-3 rounded-full bg-white">
                      <div
                        className={`h-3 rounded-full bg-gradient-to-r ${emotionColors[emotion] || "from-slate-300 to-slate-500"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="rounded-[1.75rem] border border-white/70 bg-white/85 p-6 shadow-xl shadow-slate-200/60 backdrop-blur">
            <h2 className="text-lg font-black text-slate-950">Frecuencia semanal</h2>
            <div className="mt-5 space-y-2 text-sm text-slate-700">
              {Object.keys(summary.weekly_frequency || {}).length === 0 && (
                <p className="rounded-2xl bg-slate-50 px-3 py-3">Sin actividad en la última semana.</p>
              )}

              {Object.entries(summary.weekly_frequency || {}).map(([day, value]) => (
                <div
                  key={day}
                  className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/80 px-4 py-3"
                >
                  <span className="font-semibold">{day}</span>
                  <span className="rounded-full bg-blue-50 px-3 py-1 font-bold text-blue-700">
                    {value} mensajes
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="rounded-[1.75rem] border border-white/70 bg-white/85 p-6 shadow-xl shadow-slate-200/60 backdrop-blur">
          <h2 className="text-lg font-black text-slate-950">Últimas emociones predominantes</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {(summary.predominant_recent || []).map((emotion, idx) => (
              <span
                key={`${emotion}-${idx}`}
                className="rounded-full bg-gradient-to-r from-blue-50 to-violet-50 px-3 py-1.5 text-sm font-bold text-slate-700"
              >
                {emotionLabels[emotion] || emotion}
              </span>
            ))}
          </div>

          <h3 className="mt-8 text-lg font-black text-slate-950">Evolución temporal</h3>
          <div className="mt-4 space-y-2">
            {(summary.emotion_timeline || []).length === 0 && (
              <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                Todavía no hay suficiente historial para mostrar evolución.
              </p>
            )}

            {(summary.emotion_timeline || []).map((item, idx) => (
              <div
                key={idx}
                className="flex flex-col gap-1 rounded-2xl border border-slate-100 bg-slate-50/80 px-4 py-3 text-sm sm:flex-row sm:items-center sm:justify-between"
              >
                <span className="font-bold text-slate-800">{emotionLabels[item.emotion] || item.emotion}</span>
                <span className="text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </section>

        <button
          onClick={() => router.push("/chat")}
          className="rounded-2xl bg-slate-950 px-5 py-3 font-bold text-white shadow-lg shadow-slate-200 hover:bg-slate-800"
        >
          Volver al chat
        </button>
      </div>
    </main>
  );
}