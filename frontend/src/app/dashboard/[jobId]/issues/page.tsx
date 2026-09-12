"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { Issue } from "../../../types";
import axios from "axios";
import { AlertCircle } from "lucide-react";

export default function IssuesPage() {
  const [error, setError] = useState("");
  const params = useParams();
  const jobId = params.jobId as string;
  const [issues, setIssues] = useState<Issue[]>([]);

  useEffect(() => {
    axios.get(`/api/jobs/${jobId}/issues`).then(res => {
      setIssues(res.data.filter((i: Issue) => i.status === 'open'));
    }).catch(() => setError("Unable to load this dataset. Please try again."));
  }, [jobId]);

  if (error) return <div className="error-banner" role="alert">{error}</div>;
  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-2xl font-bold">Issues Inspector</h2>
      <div className="grid grid-cols-1 gap-4">
        {issues.map(issue => (
          <div key={issue.id} className="bg-white p-6 rounded-2xl border border-brand-dark/10 shadow-sm flex items-start gap-4">
            <div className={`p-3 rounded-xl ${issue.severity === 'high' ? 'bg-red-100 text-red-600' : issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-600' : 'bg-blue-100 text-blue-600'}`}>
              <AlertCircle size={24} />
            </div>
            <div>
              <div className="text-sm font-semibold text-brand-dark/50 mb-1">{issue.category}</div>
              <h3 className="text-lg font-bold text-brand-dark capitalize">{issue.issue_type}</h3>
              {issue.column_name && <div className="text-sm mt-2"><span className="font-semibold text-brand-dark/70">Column:</span> {issue.column_name}</div>}
              <div className="text-sm mt-1"><span className="font-semibold text-brand-dark/70">Affected Rows:</span> {issue.affected_rows}</div>
            </div>
          </div>
        ))}
        {issues.length === 0 && (
          <div className="p-8 text-center text-brand-dark/50">No open issues found.</div>
        )}
      </div>
    </div>
  );
}
