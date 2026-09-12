"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { Overview } from "../../../types";
import axios from "axios";
import { Download, CheckCircle2 } from "lucide-react";

export default function ReportPage() {
  const [error, setError] = useState("");
  const params = useParams();
  const jobId = params.jobId as string;
  const [data, setData] = useState<Overview | null>(null);

  useEffect(() => {
    axios.get(`/api/jobs/${jobId}`).then(res => {
      setData(res.data);
    }).catch(() => setError("Unable to load this dataset. Please try again."));
  }, [jobId]);

  if (error) return <div className="error-banner" role="alert">{error}</div>;
  if (!data) return <p>Loading report…</p>;

  return (
    <div className="flex flex-col gap-8 items-center pt-8">

      <div className="bg-brand-primary text-white rounded-3xl p-12 w-full max-w-2xl flex flex-col items-center justify-center text-center shadow-lg shadow-brand-primary/20 relative overflow-hidden">
        <div className="absolute inset-0 bg-white/10 blur-3xl rounded-full scale-150 transform -translate-y-1/2 pointer-events-none"></div>
        <div className="text-xl font-medium mb-4 relative z-10 opacity-90">Current Data Health</div>
        <div className="text-8xl font-bold relative z-10 tracking-tighter mb-8">{data.job.health_score} <span className="text-4xl opacity-60">/ 100</span></div>

        <div className="flex gap-8 relative z-10">
            <div className="flex flex-col items-center">
                <div className="text-sm font-semibold opacity-80 uppercase tracking-widest mb-1">Open Issues</div>
                <div className="text-3xl font-bold">{data.metrics.total_issues}</div>
            </div>
            <div className="w-px h-12 bg-white/20"></div>
            <div className="flex flex-col items-center">
                <div className="text-sm font-semibold opacity-80 uppercase tracking-widest mb-1">Rows in dataset</div>
                <div className="text-3xl font-bold text-white flex items-center gap-2"><CheckCircle2 /> {data.job.row_count}</div>
            </div>
        </div>
      </div>

      <div className="flex justify-center mt-8">
        <a
          href={`/api/jobs/${jobId}/download/cleaned`}
          className="flex items-center gap-3 bg-brand-dark text-white px-8 py-4 rounded-full font-bold hover:bg-brand-primary transition-all duration-300 text-lg shadow-xl hover:shadow-brand-primary/30 hover:-translate-y-1"
          download
        >
          <Download size={24} />
          Download Cleaned Dataset
        </a>
      </div>
    </div>
  );
}
