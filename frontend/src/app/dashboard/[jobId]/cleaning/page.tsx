"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import type { Issue } from "../../../types";
import axios from "axios";
import { CheckCircle, Wand2, Loader2 } from "lucide-react";

export default function CleaningPage() {
  const [error, setError] = useState("");
  const params = useParams();
  const jobId = params.jobId as string;
  const [issues, setIssues] = useState<Issue[]>([]);
  const [processing, setProcessing] = useState<string | null>(null);

  const fetchIssues = useCallback(() => {
    axios.get(`/api/jobs/${jobId}/issues`).then(res => {
      setIssues(res.data.filter((i: Issue) => i.status === 'open'));
    }).catch(() => setError("Unable to load cleaning suggestions."));
  }, [jobId]);

  useEffect(() => {
    fetchIssues();
  }, [fetchIssues]);

  const handleFix = async (action: string, column: string | null) => {
    setProcessing(`${action}-${column}`);
    try {
      await axios.post(`/api/jobs/${jobId}/clean?action=${action}${column ? `&column=${encodeURIComponent(column)}` : ''}`);
      fetchIssues();
    } catch {
      setError("The fix could not be applied. Please try again.");
    }
    setProcessing(null);
  };

  const getActionForIssue = (issue: Issue) => {
    if (issue.issue_type === "leading or trailing whitespace") return "trim_whitespace";
    if (issue.issue_type === "case inconsistencies") return "normalize_casing";
    if (issue.issue_type === "exact duplicates") return "remove_duplicates";
    return null;
  };

  return (
    <div className="flex flex-col gap-8">
      {error && <div className="error-banner" role="alert">{error}</div>}
      <h2 className="text-2xl font-bold">Data Cleaning</h2>

      <div className="bg-white rounded-3xl border border-brand-dark/10 p-8 shadow-sm">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2"><CheckCircle className="text-green-500" /> Safe Fixes</h3>
        <div className="space-y-4">
          {issues.map(issue => {
            const action = getActionForIssue(issue);
            if (!action) return null;

            const isProcessing = processing === `${action}-${issue.column_name}`;

            return (
              <div key={issue.id} className="flex items-center justify-between p-4 bg-brand-light/50 rounded-xl">
                <div>
                  <div className="font-semibold text-brand-dark">{issue.issue_type}</div>
                  <div className="text-sm text-brand-dark/60">{issue.affected_rows} rows • Column: {issue.column_name || 'All'}</div>
                </div>
                <button
                  onClick={() => handleFix(action, issue.column_name)}
                  disabled={processing !== null}
                  className="flex items-center gap-2 px-4 py-2 bg-brand-dark text-white text-sm font-medium rounded-full hover:bg-brand-primary transition-colors disabled:opacity-50"
                >
                  {isProcessing ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                  Apply Fix
                </button>
              </div>
            )
          })}
          {issues.filter(i => getActionForIssue(i)).length === 0 && (
            <div className="text-brand-dark/50 text-sm">No safe auto-fixes available.</div>
          )}
        </div>
      </div>
    </div>
  );
}
