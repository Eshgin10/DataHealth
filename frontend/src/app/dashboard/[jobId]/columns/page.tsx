"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { ColumnProfile } from "../../../types";
import axios from "axios";
import { Database } from "lucide-react";

export default function ColumnsPage() {
  const [error, setError] = useState("");
  const params = useParams();
  const jobId = params.jobId as string;
  const [columns, setColumns] = useState<ColumnProfile[]>([]);

  useEffect(() => {
    axios.get(`/api/jobs/${jobId}/columns`).then(res => {
      setColumns(res.data);
    }).catch(() => setError("Unable to load this dataset. Please try again."));
  }, [jobId]);

  if (error) return <div className="error-banner" role="alert">{error}</div>;
  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-2xl font-bold mb-4">Column Profiling</h2>
      <div className="bg-white rounded-3xl border border-brand-dark/10 shadow-sm overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-brand-light/50 border-b border-brand-dark/10 text-brand-dark/70 text-sm uppercase tracking-wider font-semibold">
            <tr>
              <th className="p-4 pl-6">Column</th>
              <th className="p-4">Type</th>
              <th className="p-4">Missing</th>
              <th className="p-4">Unique</th>
              <th className="p-4">Stats</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-dark/10">
            {columns.map(col => (
              <tr key={col.name} className="hover:bg-brand-light/30 transition-colors">
                <td className="p-4 pl-6 font-medium flex items-center gap-2"><Database size={16} className="text-brand-dark/30"/> {col.name}</td>
                <td className="p-4"><span className="px-2.5 py-1 bg-brand-dark/5 rounded-md text-xs font-semibold text-brand-dark/70">{col.semantic_type}</span></td>
                <td className="p-4 text-sm">{col.null_count} <span className="text-brand-dark/40">({col.null_pct}%)</span></td>
                <td className="p-4 text-sm">{col.unique_count} <span className="text-brand-dark/40">({col.unique_pct}%)</span></td>
                <td className="p-4 text-sm text-brand-dark/60">
                    {col.min_val !== null && <span>Min: {col.min_val} • </span>}
                    {col.max_val !== null && <span>Max: {col.max_val} </span>}
                    {!col.min_val && !col.max_val && '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
