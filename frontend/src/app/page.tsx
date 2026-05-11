import Link from "next/link";

export default function HomePage() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-12">
      <div className="absolute inset-x-6 top-10 h-48 rounded-full bg-blue-200/30 blur-3xl" />
      <section className="relative w-full max-w-4xl overflow-hidden rounded-[2rem] border border-white/70 bg-white/80 p-8 text-center shadow-2xl shadow-blue-100/70 backdrop-blur md:p-12">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-violet-500 text-3xl shadow-lg shadow-blue-200">
          ✦
        </div>
        <p className="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-blue-600">
          Bienestar emocional
        </p>
        <h1 className="text-4xl font-black tracking-tight text-slate-950 md:text-6xl">
          TFG Salud Mental
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
          Plataforma inteligente de asistencia en salud mental basada en IA generativa,
          pensada para acompañarte con conversaciones cuidadas, recursos prácticos y
          un seguimiento emocional claro.
        </p>

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <Link
            href="/login"
            className="rounded-2xl bg-slate-950 px-6 py-3 font-bold text-white shadow-lg shadow-slate-300 hover:bg-slate-800"
          >
            Iniciar sesión
          </Link>
          <Link
            href="/register"
            className="rounded-2xl border border-slate-200 bg-white px-6 py-3 font-bold text-slate-800 shadow-sm hover:border-blue-200 hover:bg-blue-50"
          >
            Registrarse
          </Link>
        </div>
        <div className="mt-10 grid gap-4 text-left md:grid-cols-3">
          {["Chat empático", "Resumen emocional", "Recursos rápidos"].map((item) => (
            <div key={item} className="rounded-2xl border border-slate-100 bg-slate-50/80 p-4">
              <p className="font-semibold text-slate-900">{item}</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Herramientas visuales y sencillas para ayudarte a entender mejor cómo te sientes.
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}