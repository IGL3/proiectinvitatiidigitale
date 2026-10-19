/* Lista modelelor de invitații.
   Pentru un model nou: creezi folderul templates/<slug>/index.html și adaugi aici o intrare.
   v = versiunea; se schimbă la fiecare modificare a modelului, ca telefoanele să nu arate varianta veche din cache.
   Reguli pentru modele: numărătoarea inversă stă mereu chiar înainte de confirmare; confirmarea trimite în Google Sheets (RSVP_URL, vezi rsvp/);
   fiecare model are muzica lui originală (muzica.mp3, vezi unelte/muzica/), pornită la deschiderea plicului. */
window.MODELE = [
  {
    slug: "arcada-aurie",
    v: "202610190928",
    nume: "Arcada Aurie",
    eveniment: "Nuntă",
    descriere: "Plic cu sigiliu de ceară care se deschide la atingere, arcadă aurie cu vrejuri, dată răzuibilă, locații cu poze, numărătoare inversă și confirmare de participare.",
    culori: ["#f2e8d6", "#a8843f", "#6e1f2a", "#7d9270"]
  },
  {
    slug: "apus-toscan",
    v: "202610190928",
    nume: "Apus Toscan",
    eveniment: "Nuntă",
    descriere: "Plic verde-măslin cu banderolă aurie care se deschide ca o poartă, un peisaj toscan la apus, apoi o invitație pe hârtie fildeș cu ramuri de măslin: programul zilei, numărătoare inversă, locații, ținută și confirmare.",
    culori: ["#f7f0e4", "#c48f45", "#b5653f", "#55603a"]
  },
  {
    slug: "constelatia-lebedei",
    v: "202610190928",
    nume: "Constelația Lebedei",
    eveniment: "Nuntă",
    descriere: "Copertă cu universul, nebuloase, planete și stele care sclipesc; la atingerea stelei din mijloc, lumina ei deschide invitația. Paletă perlă, albastru-ceață și bleumarin, program cu hartă, numărătoare, ținută, confirmare și salvare în calendar.",
    culori: ["#f5f3ef", "#c9d6e3", "#8fa5bc", "#1c2943"]
  },
  {
    slug: "micul-astronaut",
    v: "202610190928",
    nume: "Micul Astronaut",
    eveniment: "Botez",
    descriere: "Plic tip poartă cu imprimeu de cosmos și sigiliu auriu: sigiliul se rupe, aripile se deschid și o rachetă decolează. Invitația e o misiune spațială cu astronaut, echipaj, plan de zbor cu hartă, numărătoare până la lansare și confirmare.",
    culori: ["#0f1838", "#e0b24f", "#f08a6c", "#fbf6ea"]
  }
];
