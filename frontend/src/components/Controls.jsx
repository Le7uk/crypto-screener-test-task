export default function Controls({ search, onSearchChange, fdvMax, onFdvMaxChange, sortBy, sortOrder, onSortChange }) {
  return (
    <div className="controls">
      <input
        type="text"
        placeholder="Search by name or symbol (e.g. eth)"
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      <input
        type="number"
        placeholder="Max FDV (USD)"
        min="0"
        value={fdvMax}
        onChange={(e) => onFdvMaxChange(e.target.value)}
      />

      <select
        value={`${sortBy}:${sortOrder}`}
        onChange={(e) => {
          const [nextSortBy, nextSortOrder] = e.target.value.split(":");
          onSortChange(nextSortBy, nextSortOrder);
        }}
      >
        <option value=":">No sorting</option>
        <option value="market_cap:desc">Market Cap: High → Low</option>
        <option value="market_cap:asc">Market Cap: Low → High</option>
        <option value="total_volume:desc">24h Volume: High → Low</option>
        <option value="total_volume:asc">24h Volume: Low → High</option>
      </select>
    </div>
  );
}
