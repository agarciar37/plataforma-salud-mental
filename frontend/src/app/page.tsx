import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-2xl shadow-lg p-8 border text-center">
        <h1 className="text-3xl font-bold mb-4">TFG Salud Mental</h1>
        <p className="mb-6">
          Plataforma inteligente de asistencia en salud mental basada en IA generativa.
        </p>

        <div className="flex gap-4 justify-center">
          <Link href="/login" className="rounded-lg border px-4 py-2 font-semibold">
            Iniciar sesión
          </Link>
          <Link href="/register" className="rounded-lg border px-4 py-2 font-semibold">
            Registrarse
          </Link>
        </div>
      </div>
    </main>
  );
}