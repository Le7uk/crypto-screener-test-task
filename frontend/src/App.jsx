import { useEffect, useState } from "react";

import { fetchProjects } from "./api.js";
import Controls from "./components/Controls.jsx";
import ProjectTable from "./components/ProjectTable.jsx";

export default function App() {
  const [search, setSearch] = useState("");
  const [fdvMax, setFdvMax] = useState("");
  const [sortBy, setSortBy] = useState("");
  const [sortOrder, setSortOrder] = useState("desc");

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setLoading(true);
      setError(null);

      fetchProjects({ fdvMax, search, sortBy, sortOrder })
        .then(setProjects)
        .catch(() => setError("Could not load projects. Is the backend running?"))
        .finally(() => setLoading(false));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [search, fdvMax, sortBy, sortOrder]);

  return (
    <main>
      <h1>Crypto Screener</h1>
      <p className="subtitle">Small-cap projects screened for market cap, FDV, volume and TVL.</p>

      <Controls search={search} onSearchChange={setSearch} fdvMax={fdvMax} onFdvMaxChange={setFdvMax} />

      <ProjectTable
        projects={projects}
        loading={loading}
        error={error}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={(nextSortBy, nextSortOrder) => {
          setSortBy(nextSortBy);
          setSortOrder(nextSortOrder);
        }}
      />
    </main>
  );
}
