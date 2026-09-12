"use client";

import { useEffect, useState } from "react";

import { useParams } from "next/navigation";

import type { Overview } from "../../types";

import axios from "axios";

import { Activity, AlertTriangle, CheckCircle, Database } from "lucide-react";



export default function OverviewPage() {

  const params = useParams();

  const jobId = params.jobId as string;

  const [error, setError] = useState('');

  const [data, setData] = useState<Overview | null>(null);



  useEffect(() => {

    let stopped = false;

    let timer: ReturnType<typeof setTimeout>;

    const fetchJob = async () => {

      try {

        const res = await axios.get(`/api/jobs/${jobId}`);

        if (stopped) return;

        setData(res.data);

        if (!["done", "error"].includes(res.data.job.status)) timer = setTimeout(fetchJob, 2000);

      } catch {

        setError('Unable to load this dataset. Check the connection or upload a new file.');

      }

    };



    // Poll while uploading/profiling

    fetchJob();

    return () => { stopped = true; clearTimeout(timer); };

  }, [jobId]);



  if (error) return <div role="alert" className="error-banner">{error}</div>;

  if (data?.job.status === "error") return <div role="alert" className="error-banner">This CSV could not be processed. Check that it contains valid column headers and data, then upload it again.</div>;

  if (!data) return <div className="animate-pulse flex space-x-4"><div className="flex-1 space-y-6 py-1"><div className="h-2 bg-brand-dark/10 rounded"></div><div className="space-y-3"><div className="grid grid-cols-3 gap-4"><div className="h-2 bg-brand-dark/10 rounded col-span-2"></div><div className="h-2 bg-brand-dark/10 rounded col-span-1"></div></div><div className="h-2 bg-brand-dark/10 rounded"></div></div></div></div>;



  const job = data.job;

  const metrics = data.metrics;



  if (job.status !== "done") {

    return (

      <div className="flex flex-col items-center justify-center py-20">

        <Activity className="w-12 h-12 text-brand-primary animate-pulse mb-4" />

        <h2 className="text-2xl font-bold mb-2">Processing Dataset</h2>

        <p className="text-brand-dark/60">Current step: <span className="font-semibold uppercase">{job.status}</span></p>

      </div>

    );

  }



  return (

    <div className="flex flex-col gap-8">

      {/* HEADER */}

      <div>

        <h1 className="text-3xl font-bold tracking-tight mb-2">Dataset Overview</h1>

        <div className="flex items-center gap-4 text-brand-dark/60 font-medium">

          <div className="flex items-center gap-1.5"><Database size={16} /> {job.filename}</div>

          <div>•</div>

          <div>{job.row_count.toLocaleString()} rows</div>

          <div>•</div>

          <div>{job.col_count} columns</div>

        </div>

      </div>



      {/* HERO METRICS */}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

        <div className="health-feature rounded-3xl p-6 border border-brand-dark/5 shadow-sm relative overflow-hidden flex flex-col justify-center">

          <div className="absolute -right-4 -top-4 w-32 h-32 bg-brand-primary/10 rounded-full blur-2xl"></div>

          <div className="text-sm font-semibold text-brand-dark/60 mb-1 z-10">Data Health</div>

          <div className="text-5xl font-bold tracking-tighter text-brand-primary z-10">{job.health_score}<span className="text-2xl text-brand-dark/30">/100</span></div>

        </div>



        <div className="bg-white rounded-3xl p-6 border border-brand-dark/5 shadow-sm">

          <div className="text-sm font-semibold text-brand-dark/60 mb-1">Issues Found</div>

          <div className="text-4xl font-bold tracking-tight text-brand-dark">{metrics.total_issues.toLocaleString()}</div>

        </div>



        <div className="bg-white rounded-3xl p-6 border border-brand-dark/5 shadow-sm">

          <div className="text-sm font-semibold text-brand-dark/60 mb-1">Issue occurrences</div>

          <div className="text-4xl font-bold tracking-tight text-brand-dark">{metrics.affected_rows.toLocaleString()}</div>

        </div>



        <div className="bg-white rounded-3xl p-6 border border-brand-dark/5 shadow-sm">

          <div className="text-sm font-semibold text-brand-dark/60 mb-1">Columns with Issues</div>

          <div className="text-4xl font-bold tracking-tight text-brand-dark">{metrics.columns_with_issues} <span className="text-xl text-brand-dark/40">/ {job.col_count}</span></div>

        </div>

      </div>



      {/* ROW 2 */}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        <div className="lg:col-span-2 bg-white rounded-3xl p-8 border border-brand-dark/5 shadow-sm">

          <h3 className="text-lg font-bold mb-6">Data Quality Breakdown</h3>

          <div className="space-y-6">

            <ScoreBar label="Completeness" score={job.completeness_score} />

            <ScoreBar label="Validity" score={job.validity_score} />

            <ScoreBar label="Consistency" score={job.consistency_score} />

            <ScoreBar label="Uniqueness" score={job.uniqueness_score} />

          </div>

        </div>



        <div className="bg-brand-dark text-white rounded-3xl p-8 shadow-sm">

          <h3 className="text-lg font-bold mb-6 text-brand-light">Key Findings</h3>

          <ul className="space-y-6">

            {metrics.total_issues > 0 ? (

              <>

                <li className="flex gap-4">

                  <AlertTriangle className="text-yellow-400 shrink-0" size={20} />

                  <div>

                    <div className="font-semibold text-brand-light mb-1">{metrics.total_issues} issues require attention</div>

                    <div className="text-sm text-brand-light/70 leading-relaxed">Review the issues inspector for affected columns and available cleaning actions.</div>

                  </div>

                </li>

                <li className="flex gap-4">

                  <Activity className="text-brand-primary shrink-0" size={20} />

                  <div>

                    <div className="font-semibold text-brand-light mb-1">Impact on analytics</div>

                    <div className="text-sm text-brand-light/70 leading-relaxed">{metrics.affected_rows} issue occurrences were found. A record can have more than one issue.</div>

                  </div>

                </li>

              </>

            ) : (

              <li className="flex gap-4">

                <CheckCircle className="text-green-400 shrink-0" size={20} />

                <div>

                  <div className="font-semibold text-brand-light mb-1">Dataset looks great</div>

                  <div className="text-sm text-brand-light/70 leading-relaxed">No critical issues were detected during the profiling and validation process.</div>

                </div>

              </li>

            )}

          </ul>

        </div>

      </div>

    </div>

  );

}



function ScoreBar({ label, score }: { label: string, score: number }) {

  return (

    <div>

      <div className="flex justify-between text-sm font-semibold mb-2 text-brand-dark">

        <span>{label}</span>

        <span>{score}%</span>

      </div>

      <div className="w-full h-3 bg-brand-light rounded-full overflow-hidden">

        <div

          className="h-full bg-brand-primary transition-all duration-1000 ease-out rounded-full"

          style={{ width: `${score}%` }}

        />

      </div>

    </div>

  );

}
