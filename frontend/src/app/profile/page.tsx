"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserSummary } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return router.push("/login");

    getUserSummary(token).then(setSummary);
  }, []);

  if (!summary) return <p className="p-6">Cargando...</p>;

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">Perfil</h1>

      <p>{summary.user.name}</p>
      <p>{summary.user.email}</p>

      <h2 className="mt-4">Mensajes: {summary.total_messages}</h2>

      <h3 className="mt-4">Emociones</h3>
      {Object.entries(summary.emotion_counts).map(([k, v]) => (
        <p key={k}>{k}: {v as number}</p>
      ))}

      <button
        onClick={() => router.push("/chat")}
        className="mt-6 border px-4 py-2"
      >
        Volver
      </button>
    </main>
  );
}