function DataTable({ columns = [], rows = [], emptyTitle = 'No entries available yet', emptyDescription = 'The live backend data has not been connected yet.' }) {
  if (!rows.length) {
    return (
      <div className="rounded-[24px] border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
        <h3 className="text-base font-semibold text-slate-800">{emptyTitle}</h3>
        <p className="mt-2 text-sm text-slate-600">{emptyDescription}</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead className="bg-slate-50 text-sm text-slate-600">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-4 py-3 font-semibold">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-sm text-slate-700">
            {rows.map((row, index) => (
              <tr key={`${row.id || index}`} className="bg-white hover:bg-slate-50">
                {columns.map((column) => (
                  <td key={`${row.id || index}-${column.key}`} className="px-4 py-3 align-middle">
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
