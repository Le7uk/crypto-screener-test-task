function formatUsd(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

function SortableHeader({ label, column, sortBy, sortOrder, onSortChange }) {
  const isActive = sortBy === column;

  const handleClick = () => {
    if (isActive) {
      onSortChange(column, sortOrder === "asc" ? "desc" : "asc");
    } else {
      onSortChange(column, "desc");
    }
  };

  return (
    <th className="sortable" onClick={handleClick} aria-sort={isActive ? sortOrder : "none"}>
      {label}
      <span className={`sort-arrow ${isActive ? "active" : ""}`}>{isActive && sortOrder === "asc" ? "▲" : "▼"}</span>
    </th>
  );
}

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <tr key={i} className="skeleton-row">
          <td colSpan={6}>
            <div className="skeleton-bar" />
          </td>
        </tr>
      ))}
    </>
  );
}

export default function ProjectTable({ projects, loading, error, sortBy, sortOrder, onSortChange }) {
  return (
    <>
      <p className="result-count">
        {loading ? "Loading…" : error ? null : `Showing ${projects.length} project${projects.length === 1 ? "" : "s"}`}
      </p>

      {error && <p className="status error">{error}</p>}

      {!error && (
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Price</th>
              <SortableHeader label="Market Cap" column="market_cap" sortBy={sortBy} sortOrder={sortOrder} onSortChange={onSortChange} />
              <th>FDV</th>
              <SortableHeader label="24h Volume" column="total_volume" sortBy={sortBy} sortOrder={sortOrder} onSortChange={onSortChange} />
              <th>TVL</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <SkeletonRows />
            ) : projects.length === 0 ? (
              <tr>
                <td colSpan={6} className="status">
                  No projects match the current filters.
                </td>
              </tr>
            ) : (
              projects.map((p) => (
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
              ))
            )}
          </tbody>
        </table>
      )}
    </>
  );
}
