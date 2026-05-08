type QuickResource = {
  title: string;
  description: string;
  icon: string;
  accent: string;
};

const resources: QuickResource[] = [
  {
    title: "Respiración guiada",
    description: "Inhala 4 segundos, mantén 4 y exhala 6. Repite durante 2 minutos.",
    icon: "◌",
    accent: "from-sky-400 to-blue-500",
  },
  {
    title: "Diario rápido",
    description: "Escribe durante 5 minutos qué sientes, qué lo causa y qué necesitas ahora.",
    icon: "✎",
    accent: "from-violet-400 to-fuchsia-500",
  },
  {
    title: "Pausa breve",
    description: "Levántate, bebe agua y aléjate de la pantalla durante 3-5 minutos.",
    icon: "☕",
    accent: "from-amber-300 to-orange-500",
  },
  {
    title: "Descanso digital",
    description: "Reduce notificaciones y estímulos durante un rato para bajar el agobio.",
    icon: "◒",
    accent: "from-emerald-300 to-teal-500",
  },
  {
    title: "Apoyo profesional",
    description: "Si el malestar es intenso o persistente, busca ayuda psicológica profesional.",
    icon: "♡",
    accent: "from-rose-300 to-red-500",
  },
];

export default function QuickResources() {
  return (
    <section className="overflow-hidden rounded-[1.75rem] border border-white/70 bg-white/85 p-4 shadow-xl shadow-slate-200/60 backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-blue-500">
            Kit de calma
          </p>
          <h3 className="mt-1 text-lg font-black text-slate-950">Recursos rápidos</h3>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-600">
          5 min
        </span>
      </div>

      <div className="space-y-3">
        {resources.map((resource) => (
          <article
            key={resource.title}
            className="group rounded-2xl border border-slate-100 bg-slate-50/80 p-3 hover:border-blue-100 hover:bg-white hover:shadow-md hover:shadow-blue-100/60"
          >
          <div className="flex gap-3">
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${resource.accent} font-black text-white shadow-sm`}
              >
                {resource.icon}
              </div>
              <div>
                <p className="text-sm font-bold text-slate-900">{resource.title}</p>
                <p className="mt-1 text-sm leading-5 text-slate-600">{resource.description}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}