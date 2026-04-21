"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { sendChatMessage, getChatHistory } from "@/lib/api";
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
};

export default function ChatPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

  const loadHistory = async (authToken: string) => {
    try {
      const history = await getChatHistory(authToken);

      const formatted = history.map((item: any) => ({
        user_message: item.user_message,
        assistant_message: item.assistant_message,
        emotion: item.emotion,
        recommendations: item.recommendations || [],
        created_at: item.created_at,
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

      setChat((prev) => [
        ...prev,
        {
          user_message: result.user_message,
          assistant_message: result.assistant_message,
          emotion: result.emotion,
          recommendations: result.recommendations || [],
          created_at: result.created_at,
        },
      ]);

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

  return (
    <main className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 flex flex-col rounded-2xl bg-white shadow-lg border">
          <div className="flex items-center justify-between border-b px-4 py-4 md:px-6">
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-slate-900">
                Asistente emocional
              </h1>
              {user && (
                <p className="text-xs md:text-sm text-slate-500 mt-1">
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

          <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4 md:px-6 bg-slate-50">
            {chat.length === 0 && (
              <p className="text-sm text-slate-500">
                Escribe cómo te sientes para empezar la conversación.
              </p>
            )}

            {chat.map((item, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-end">
                  <div className="max-w-[75%] rounded-2xl bg-blue-500 text-white px-4 py-3">
                    <p>{item.user_message}</p>
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl border bg-white px-4 py-3">
                    <p>{item.assistant_message}</p>

                    <p className="text-xs mt-2 text-gray-500">
                      {formatTimestamp(item.created_at)}
                    </p>

                    <p className="text-sm mt-2">
                      Emoción: {item.emotion}
                    </p>

                    {item.recommendations && item.recommendations.length > 0 && (
                      <ul className="mt-2 text-sm text-green-700 list-disc pl-5">
                        {item.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t px-4 py-4 flex gap-2">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1 border rounded-lg p-2"
              placeholder="Escribe tu mensaje..."
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
            >
              {loading ? "..." : "Enviar"}
            </button>
          </div>

          {error && <p className="px-4 pb-4 text-sm text-red-600">{error}</p>}
        </div>

        <aside className="space-y-4">
          <div className="bg-white p-4 rounded-xl border">
            <h3 className="font-semibold">Resumen emocional</h3>
            <p className="mt-2 text-sm text-slate-600">
              {chat.length} mensajes analizados
            </p>

            <div className="mt-3 space-y-1 text-sm text-slate-600">
              {Object.keys(emotionStats).length === 0 && <p>No hay datos todavía</p>}
              {Object.entries(emotionStats).map(([emotion, count]) => (
                <div key={emotion} className="flex justify-between">
                  <span>{emotion}</span>
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