"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getChatHistory, sendChatMessage } from "@/lib/api";
import QuickResources from "@/components/QuickResources";

type User = {
  id: string;
  name: string;
  email: string;
};

type ChatItem = {
  user_message: string;
  assistant_message: string;
  emotion: string;
  recommendations?: string[];
  created_at?: string;
  crisis_detected?: boolean;
  crisis_resources?: string[];
};

const emotionLabels: Record<string, string> = {
  ansiedad: "Ansiedad",
  estres: "Estrés",
  tristeza: "Tristeza",
  neutral: "Neutral",
  positivo: "Positivo",
  crisis: "Crisis",
};

export default function ChatPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeCrisis, setActiveCrisis] = useState<ChatItem | null>(null);
  const chatStartRef = useRef<HTMLDivElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const messageInputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (!storedToken || !storedUser) {
      router.push("/login");
      return;
    }

    setToken(storedToken);
    setUser(JSON.parse(storedUser));
    loadHistory(storedToken);
  }, [router]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  const loadHistory = async (authToken: string) => {
    try {
      const history = await getChatHistory(authToken);

      const formatted = history.map((item: ChatItem) => ({
        user_message: item.user_message,
        assistant_message: item.assistant_message,
        emotion: item.emotion,
        recommendations: item.recommendations || [],
        created_at: item.created_at,
        crisis_detected: item.emotion === "crisis",
        crisis_resources: item.crisis_resources || [],
      }));

      setChat(formatted);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  const handleSend = async () => {
    if (!message.trim() || !token) return;

    setError("");
    setLoading(true);

    try {
      const result = await sendChatMessage(message, token);

      const item: ChatItem = {
        user_message: result.user_message,
        assistant_message: result.assistant_message,
        emotion: result.emotion,
        recommendations: result.recommendations || [],
        created_at: result.created_at,
        crisis_detected: result.crisis_detected,
        crisis_resources: result.crisis_resources || [],
      };

      setChat((prev) => [...prev, item]);
      if (item.crisis_detected) {
        setActiveCrisis(item);
      }

      setMessage("");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Ha ocurrido un error");
      }
    } finally {
      setLoading(false);
    }
  };

  const emotionStats = chat.reduce(
    (acc, item) => {
      acc[item.emotion] = (acc[item.emotion] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const formatTimestamp = (iso?: string) => {
    if (!iso) return "";
    const date = new Date(iso);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const scrollToChatStart = () => {
    chatStartRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const scrollToChatEnd = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  };

  const focusComposer = () => {
    messageInputRef.current?.focus();
  }; 

  if (activeCrisis) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6 py-12">
        <section className="w-full max-w-2xl overflow-hidden rounded-[2rem] border border-red-100 bg-white/90 shadow-2xl shadow-red-100/70 backdrop-blur">
          <div className="bg-gradient-to-br from-red-500 to-rose-600 p-6 text-white">
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-red-100">
              Prioridad inmediata
            </p>
            <h1 className="mt-2 text-3xl font-black">Necesitas apoyo inmediato</h1>
            <p className="mt-3 leading-7 text-red-50">
              Hemos detectado señales de crisis en tu mensaje. Tu seguridad es prioritaria.
            </p>
          </div>

          <div className="p-6">
            <ul className="space-y-3 text-slate-700">
              {(activeCrisis.crisis_resources || []).map((resource, idx) => (
                <li key={idx} className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3">
                  {resource}
                </li>
              ))}
            </ul>

            <p className="mt-5 rounded-2xl bg-slate-950 p-4 text-sm font-semibold text-white">
              Si hay riesgo inmediato, llama a emergencias ahora mismo y busca acompañamiento.
            </p>

            <button
              onClick={() => setActiveCrisis(null)}
              className="mt-6 rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Volver al chat
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="h-dvh overflow-hidden px-3 py-3 md:px-5 md:py-5">
      <div className="mx-auto grid h-full min-h-0 max-w-7xl grid-cols-1 gap-4 overflow-y-auto lg:grid-cols-[minmax(0,2fr)_minmax(320px,0.9fr)] lg:overflow-hidden">
        <section className="flex min-h-[calc(100dvh-1.5rem)] flex-col overflow-hidden rounded-[2rem] border border-white/70 bg-white/85 shadow-2xl shadow-blue-100/70 backdrop-blur md:min-h-[calc(100dvh-2.5rem)] lg:min-h-0">
          <header className="border-b border-slate-100 bg-white/80 px-4 py-4 md:px-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.24em] text-blue-500">
                  Sesión de acompañamiento
                </p>
                <h1 className="mt-1 text-2xl font-black tracking-tight text-slate-950 md:text-3xl">
                  Asistente emocional
                </h1>
                {user && (
                  <p className="mt-1 text-xs text-slate-500 md:text-sm">
                    {user.name} · {user.email}
                  </p>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => router.push("/profile")}
                  className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 shadow-sm hover:border-blue-200 hover:bg-blue-50"
                >
                  Ver perfil
                </button>

                <button
                  onClick={handleLogout}
                  className="rounded-2xl border border-slate-200 bg-slate-950 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-slate-800"
                >
                  Cerrar sesión
                </button>
              </div>
            </div>
            </header>

          <nav className="sticky top-0 z-10 border-b border-slate-100 bg-white/90 px-4 py-3 backdrop-blur md:px-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={scrollToChatStart}
                  className="rounded-full bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-blue-50 hover:text-blue-700"
                >
                  ↑ Inicio
                </button>
                <button
                  type="button"
                  onClick={scrollToChatEnd}
                  className="rounded-full bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-blue-50 hover:text-blue-700"
                >
                  ↓ Último mensaje
                </button>
                <button
                  type="button"
                  onClick={focusComposer}
                  className="rounded-full bg-blue-600 px-3 py-2 text-xs font-bold text-white shadow-sm shadow-blue-200 hover:bg-blue-700"
                >
                  Escribir ahora
                </button>
              </div>
              <p className="rounded-full bg-violet-50 px-3 py-2 text-xs font-bold text-violet-700">
                {chat.length} mensajes · {Object.keys(emotionStats).length || 0} emociones
              </p>
            </div>
          </nav>
          <div className="min-h-0 flex-1 space-y-5 overflow-y-auto bg-gradient-to-b from-slate-50/80 to-white px-4 py-5 md:px-6">
            <div ref={chatStartRef} />
            {chat.some((item) => item.crisis_detected) && (
              <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
                Se detectó una situación de crisis recientemente. Prioriza recursos de ayuda inmediata.
              </div>
            )}
            {chat.length === 0 && (
              <div className="rounded-3xl border border-dashed border-blue-200 bg-blue-50/70 p-6 text-center">
                <p className="text-base font-bold text-slate-800">Tu conversación empieza aquí</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Escribe cómo te sientes para recibir una respuesta empática y recursos adaptados.
                </p>
              </div>
            )}

            {chat.map((item, index) => (
              <article key={index} className="space-y-3">
                <div className="flex justify-end">
                  <div className="max-w-[82%] rounded-[1.5rem] rounded-br-md bg-gradient-to-br from-blue-600 to-violet-600 px-4 py-3 text-white shadow-lg shadow-blue-100 md:max-w-[72%]">
                    <p className="leading-6">{item.user_message}</p>
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="max-w-[90%] rounded-[1.5rem] rounded-bl-md border border-slate-100 bg-white px-4 py-3 shadow-md shadow-slate-100 md:max-w-[82%]">
                    <p className="leading-6 text-slate-700">{item.assistant_message}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                      {formatTimestamp(item.created_at) && (
                        <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-500">
                          {formatTimestamp(item.created_at)}
                        </span>
                      )}
                      <span className="rounded-full bg-blue-50 px-2.5 py-1 font-bold text-blue-700">
                        {emotionLabels[item.emotion] || item.emotion}
                      </span>
                    </div>

                    {!item.crisis_detected && item.recommendations && item.recommendations.length > 0 && (
                      <ul className="mt-3 space-y-2 text-sm text-emerald-700">
                        {item.recommendations.map((rec, i) => (
                          <li key={i} className="rounded-2xl bg-emerald-50 px-3 py-2">
                            {rec}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </article>
            ))}
            {loading && (
              <div className="rounded-2xl border border-blue-100 bg-white p-4 text-sm font-medium text-slate-600 shadow-sm">
                Analizando tu mensaje y preparando una respuesta personalizada…
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="border-t border-slate-100 bg-white/90 px-4 py-4 md:px-6">
            <div className="flex flex-col gap-3 md:flex-row">
              <textarea
                ref={messageInputRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="min-h-[72px] max-h-32 flex-1 resize-none rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-900 placeholder:text-slate-400"
                placeholder="Escribe tu mensaje..."
              />
              <button
                onClick={handleSend}
                disabled={loading}
                className="rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 px-6 py-3 font-bold text-white shadow-lg shadow-blue-200 hover:from-blue-700 hover:to-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Enviando..." : "Enviar"}
              </button>
            </div>
            {error && <p className="mt-3 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-700">{error}</p>}
          </div>
        </section>
          <aside className="min-h-0 space-y-4 pb-3 lg:overflow-y-auto lg:pb-0">
          <section className="rounded-[1.75rem] border border-white/70 bg-white/85 p-5 shadow-xl shadow-slate-200/60 backdrop-blur">
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-violet-500">
              Panel activo
            </p>
            <h3 className="mt-1 text-lg font-black text-slate-950">Resumen emocional</h3>
            <p className="mt-2 text-sm text-slate-600">
              {chat.length} mensajes analizados en esta conversación.
            </p>

            <div className="mt-4 space-y-3 text-sm text-slate-600">
              {Object.keys(emotionStats).length === 0 && (
                <p className="rounded-2xl bg-slate-50 px-3 py-3">No hay datos todavía</p>
              )}
              {Object.entries(emotionStats).map(([emotion, count]) => (
                <div key={emotion} className="rounded-2xl border border-slate-100 bg-slate-50/80 px-3 py-3">
                  <div className="flex justify-between font-semibold text-slate-800">
                    <span>{emotionLabels[emotion] || emotion}</span>
                    <span>{count}</span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-white">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-violet-500"
                      style={{ width: `${Math.max(12, Math.round((count / Math.max(chat.length, 1)) * 100))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <QuickResources />
        </aside>
      </div>
    </main>
  );
}