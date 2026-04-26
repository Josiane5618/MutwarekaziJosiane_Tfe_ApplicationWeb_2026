const [majorRaw, minorRaw] = process.versions.node.split(".");
const major = Number.parseInt(majorRaw, 10);
const minor = Number.parseInt(minorRaw, 10);

const isSupported =
  (major === 20 && minor >= 19) ||
  (major >= 22 && !(major === 22 && minor < 12));

if (isSupported) {
  process.exit(0);
}

console.error(
  [
    "",
    `Node.js ${process.versions.node} n'est pas supporte par ce frontend.`,
    "Version requise: 20.19+ ou 22.12+.",
    `Version detectee ici: ${process.versions.node}.`,
    "Installe Node 22.12+ puis relance npm run dev ou npm run build.",
    ""
  ].join("\n")
);

process.exit(1);
