"use client";
import Link from "next/link";
import { usePathname, useParams } from "next/navigation";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useParams();
  const jobId = params.jobId as string;

  const tabs = [
    { name: "Overview", path: `/dashboard/${jobId}` },
    { name: "Columns", path: `/dashboard/${jobId}/columns` },
    { name: "Issues", path: `/dashboard/${jobId}/issues` },
    { name: "Cleaning", path: `/dashboard/${jobId}/cleaning` },
    { name: "Report", path: `/dashboard/${jobId}/report` },
  ];

  return (
    <div className="flex flex-col animate-fade-in-up">
      <div className="flex items-center gap-8 overflow-x-auto whitespace-nowrap mb-8 border-b border-brand-dark/10 pb-4 mt-4">
        {tabs.map((t) => {
          const isActive = pathname === t.path;
          return (
            <Link key={t.name} href={t.path} className={`text-sm font-medium transition-colors relative pb-4 -mb-4 ${isActive ? 'text-brand-primary' : 'text-brand-dark/60 hover:text-brand-dark'}`}>
              {t.name}
              {isActive && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-primary rounded-t-full" />}
            </Link>
          )
        })}
      </div>
      {children}
    </div>
  );
}
