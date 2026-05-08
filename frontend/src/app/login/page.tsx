"use client";

import Link from "next/link"
import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
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
    setLoading(true);

    try {
      const result = await loginUser(form);

      localStorage.setItem("token", result.access_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      router.push("/chat");
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
      <section className="grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-white/70 bg-white/85 shadow-2xl shadow-blue-100/70 backdrop-blur lg:grid-cols-[1fr_0.9fr]">
        <div className="hidden bg-gradient-to-br from-blue-600 via-indigo-600 to-violet-600 p-10 text-white lg:block">
          <div className="flex h-full flex-col justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-100">
                Bienvenido de nuevo
              </p>
              <h1 className="mt-5 text-4xl font-black leading-tight">
                Retoma tu espacio seguro para conversar y cuidarte.
              </h1>
            </div>
            <div className="rounded-3xl bg-white/15 p-5 backdrop-blur">
              <p className="text-sm leading-6 text-blue-50">
                Accede a tu chat emocional, revisa tus patrones recientes y utiliza
                recursos rápidos cuando necesites una pausa.
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 md:p-10">
          <Link href="/" className="text-sm font-semibold text-blue-600 hover:text-blue-700">
            ← Volver al inicio
          </Link>
          <h2 className="mt-8 text-3xl font-black tracking-tight text-slate-950">
            Iniciar sesión
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Entra para continuar con tu acompañamiento emocional.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
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
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 placeholder:text-slate-400"
                required
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-slate-950 p-3 font-bold text-white shadow-lg shadow-slate-200 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>

          {error && (
            <p className="mt-4 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              {error}
            </p>
          )}

          <p className="mt-6 text-center text-sm text-slate-500">
            ¿Aún no tienes cuenta?{" "}
            <Link href="/register" className="font-bold text-blue-600 hover:text-blue-700">
              Regístrate
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}