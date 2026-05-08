"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { registerUser } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(form);
      setSuccess("Usuario registrado correctamente");
      setTimeout(() => {
        router.push("/login");
      }, 1000);
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

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/70 bg-white/85 shadow-2xl shadow-violet-100/70 backdrop-blur lg:grid-cols-[0.9fr_1fr]">
        <div className="p-6 md:p-10">
          <Link href="/" className="text-sm font-semibold text-blue-600 hover:text-blue-700">
            ← Volver al inicio
          </Link>
          <h1 className="mt-8 text-3xl font-black tracking-tight text-slate-950">
            Crea tu cuenta
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Empieza a construir tu historial emocional con una interfaz clara y segura.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <label className="block">
              <span className="text-sm font-semibold text-slate-700">Nombre</span>
              <input
                type="text"
                name="name"
                placeholder="Tu nombre"
                value={form.name}
                onChange={handleChange}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 placeholder:text-slate-400"
                required
              />
            </label>

            <label className="block">
              <span className="text-sm font-semibold text-slate-700">Correo electrónico</span>
              <input
                type="email"
                name="email"
                placeholder="tu@email.com"
                value={form.email}
                onChange={handleChange}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 placeholder:text-slate-400"
                required
              />
            </label>

            <label className="block">
              <span className="text-sm font-semibold text-slate-700">Contraseña</span>
              <input
                type="password"
                name="password"
                placeholder="Crea una contraseña"
                value={form.password}
                onChange={handleChange}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 placeholder:text-slate-400"
                required
              />
            </label>

          <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 p-3 font-bold text-white shadow-lg shadow-blue-200 hover:from-blue-700 hover:to-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Registrando..." : "Registrarse"}
            </button>
          </form>

        {error && (
            <p className="mt-4 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </p>
          )}
          {success && (
            <p className="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
              {success}
            </p>
          )}

          <p className="mt-6 text-center text-sm text-slate-500">
            ¿Ya tienes cuenta?{" "}
            <Link href="/login" className="font-bold text-blue-600 hover:text-blue-700">
              Inicia sesión
            </Link>
          </p>
        </div>

        <div className="hidden bg-gradient-to-br from-sky-500 via-blue-600 to-violet-600 p-10 text-white lg:block">
          <div className="flex h-full flex-col justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-100">
                Primer paso
              </p>
              <h2 className="mt-5 text-4xl font-black leading-tight">
                Una experiencia visual serena para registrar cómo te sientes.
              </h2>
            </div>
            <div className="grid gap-3">
              {["Conversaciones privadas", "Métricas emocionales", "Recomendaciones prácticas"].map((item) => (
                <div key={item} className="rounded-2xl bg-white/15 px-4 py-3 font-semibold backdrop-blur">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}