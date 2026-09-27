export default function Controls({ search, onSearchChange, fdvMax, onFdvMaxChange, onReset }) {
  const hasActiveFilters = search !== "" || fdvMax !== "";

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

      <button type="button" className="reset-button" onClick={onReset} disabled={!hasActiveFilters}>
        Reset
      </button>
    </div>
  );
}
