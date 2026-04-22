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
  const chatEndRef = useRef<HTMLDivElement | null>(null);

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

  if (activeCrisis) {
    return (
      <main className="min-h-screen bg-red-50 p-6">
        <div className="mx-auto max-w-2xl rounded-2xl border border-red-200 bg-white p-6 shadow-md">
          <h1 className="text-2xl font-bold text-red-700">Necesitas apoyo inmediato</h1>
          <p className="mt-3 text-slate-700">
            Hemos detectado señales de crisis en tu mensaje. Tu seguridad es prioritaria.
          </p>

          <ul className="mt-4 list-disc space-y-2 pl-5 text-slate-700">
            {(activeCrisis.crisis_resources || []).map((resource, idx) => (
              <li key={idx}>{resource}</li>
            ))}
          </ul>

          <p className="mt-4 rounded-lg bg-red-100 p-3 text-sm text-red-800">
            Si hay riesgo inmediato, llama a emergencias ahora mismo y busca acompañamiento.
          </p>

          <button
            onClick={() => setActiveCrisis(null)}
            className="mt-6 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Volver al chat
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col rounded-2xl border bg-white shadow-lg lg:col-span-2">
          <div className="flex items-center justify-between border-b px-4 py-4 md:px-6">
            <div>
              <h1 className="text-xl font-bold text-slate-900 md:text-2xl">Asistente emocional</h1>
              {user && (
                <p className="mt-1 text-xs text-slate-500 md:text-sm">
                  {user.name} · {user.email}
                </p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push("/profile")}
                className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Ver perfil
              </button>

              <button
                onClick={handleLogout}
                className="rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Cerrar sesión
              </button>
            </div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50 px-4 py-4 md:px-6">
            {chat.some((item) => item.crisis_detected) && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                Se detectó una situación de crisis recientemente. Prioriza recursos de ayuda inmediata.
              </div>
            )}
            {chat.length === 0 && (
              <p className="text-sm text-slate-500">Escribe cómo te sientes para empezar la conversación.</p>
            )}

            {chat.map((item, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-end">
                  <div className="max-w-[75%] rounded-2xl bg-blue-500 px-4 py-3 text-white">
                    <p>{item.user_message}</p>
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl border bg-white px-4 py-3">
                    <p>{item.assistant_message}</p>
                    <p className="mt-2 text-xs text-gray-500">{formatTimestamp(item.created_at)}</p>
                    <p className="mt-2 text-sm">
                      Emoción: {emotionLabels[item.emotion] || item.emotion}
                    </p>

                    {!item.crisis_detected && item.recommendations && item.recommendations.length > 0 && (
                      <ul className="mt-2 list-disc pl-5 text-sm text-green-700">
                        {item.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="rounded-xl border bg-white p-3 text-sm text-slate-600">
                Analizando tu mensaje y preparando una respuesta personalizada…
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="flex gap-2 border-t px-4 py-4">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="min-h-[70px] flex-1 rounded-lg border p-2"
              placeholder="Escribe tu mensaje..."
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
            >
              {loading ? "Enviando..." : "Enviar"}
            </button>
          </div>

          {error && <p className="px-4 pb-4 text-sm font-medium text-red-600">{error}</p>}
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border bg-white p-4">
            <h3 className="font-semibold">Resumen emocional</h3>
            <p className="mt-2 text-sm text-slate-600">
              {chat.length} mensajes analizados
            </p>

            <div className="mt-3 space-y-1 text-sm text-slate-600">
              {Object.keys(emotionStats).length === 0 && <p>No hay datos todavía</p>}
              {Object.entries(emotionStats).map(([emotion, count]) => (
                <div key={emotion} className="flex justify-between">
                  <span>{emotionLabels[emotion] || emotion}</span>
                  <span>{count}</span>
                </div>
              ))}
            </div>
          </div>

          <QuickResources />
        </aside>
      </div>
    </main>
  );
}