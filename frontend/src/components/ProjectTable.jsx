function formatUsd(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

export default function ProjectTable({ projects, loading, error }) {
  if (loading) return <p className="status">Loading…</p>;
  if (error) return <p className="status error">{error}</p>;
  if (projects.length === 0) return <p className="status">No projects match the current filters.</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>Project</th>
          <th>Price</th>
          <th>Market Cap</th>
          <th>FDV</th>
          <th>24h Volume</th>
          <th>TVL</th>
        </tr>
      </thead>
      <tbody>
        {projects.map((p) => (
          <tr key={p.id}>
            <td className="project-cell">
              {p.image && <img src={p.image} alt="" width={20} height={20} />}
              <span>{p.name}</span>
              <span className="symbol">{p.symbol.toUpperCase()}</span>
            </td>
            <td>{formatUsd(p.current_price)}</td>
            <td>{formatUsd(p.market_cap)}</td>
            <td>{formatUsd(p.fully_diluted_valuation)}</td>
            <td>{formatUsd(p.total_volume)}</td>
            <td>{formatUsd(p.total_value_locked)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
