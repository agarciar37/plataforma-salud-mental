type QuickResource = {
  title: string;
  description: string;
};

const resources: QuickResource[] = [
  {
    title: "Respiración guiada",
    description: "Inhala 4 segundos, mantén 4 y exhala 6. Repite durante 2 minutos.",
  },
  {
    title: "Diario rápido",
    description: "Escribe durante 5 minutos qué sientes, qué lo causa y qué necesitas ahora.",
  },
  {
    title: "Pausa breve",
    description: "Levántate, bebe agua y aléjate de la pantalla durante 3-5 minutos.",
  },
  {
    title: "Descanso digital",
    description: "Reduce notificaciones y estímulos durante un rato para bajar el agobio.",
  },
  {
    title: "Apoyo profesional",
    description: "Si el malestar es intenso o persistente, busca ayuda psicológica profesional.",
  },
];

export default function QuickResources() {
  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-base font-semibold text-slate-900">
        Recursos rápidos
      </h3>

      <div className="space-y-3">
        {resources.map((resource, index) => (
          <div
            key={index}
            className="rounded-xl bg-slate-50 p-3"
          >
            <p className="text-sm font-semibold text-slate-800">
              {resource.title}
            </p>
            <p className="mt-1 text-sm text-slate-600">
              {resource.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}