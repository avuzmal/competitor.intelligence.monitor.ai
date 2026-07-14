"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { apiClient } from "@/lib/api";
import { BriefingHistory } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { format } from "date-fns";
import { AlertCircle, ArrowRight, Activity } from "lucide-react";

export default function BriefingDetail() {
  const params = useParams();
  
  const { data: briefings, isLoading } = useQuery<BriefingHistory[]>({
    queryKey: ["briefings"],
    queryFn: async () => {
      const res = await apiClient.get("/api/v1/dashboard/briefings");
      return res.data;
    },
  });

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  const briefing = briefings?.find(b => b.id === Number(params.id));

  if (!briefing) {
    return <div>Briefing not found</div>;
  }

  const { insight_json: insight } = briefing;

  return (
    <div className="mx-auto max-w-4xl space-y-8 pb-12">
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <Badge variant="outline">{format(new Date(briefing.scrape_date), "PPP")}</Badge>
          <Badge className={
            insight.threat_level === "HIGH" ? "bg-red-500" : 
            insight.threat_level === "MEDIUM" ? "bg-orange-500" : "bg-green-500"
          }>
            {insight.threat_level} THREAT
          </Badge>
        </div>
        <h1 className="text-3xl font-bold tracking-tight">Executive Summary</h1>
        <p className="text-lg leading-relaxed text-muted-foreground">
          {insight.executive_summary}
        </p>
      </div>

      <Separator />

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-500" />
          <h2 className="text-2xl font-semibold">What Changed</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {insight.what_changed.length === 0 ? <p className="text-muted-foreground">No significant changes detected.</p> : null}
          {insight.what_changed.map((item, i) => (
            <div key={i} className="rounded-lg border bg-card p-4 shadow-sm">
              <h3 className="font-semibold text-primary">{item.category}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-orange-500" />
          <h2 className="text-2xl font-semibold">What It Means</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {insight.what_it_means.length === 0 ? <p className="text-muted-foreground">No implications generated.</p> : null}
          {insight.what_it_means.map((item, i) => (
            <div key={i} className="rounded-lg border bg-card p-4 shadow-sm">
              <h3 className="font-semibold text-primary">{item.category}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-4 rounded-xl bg-blue-50/50 p-6 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900">
        <div className="flex items-center gap-2">
          <ArrowRight className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-2xl font-semibold text-blue-900 dark:text-blue-100">What To Do</h2>
        </div>
        <div className="mt-4 space-y-4">
          {insight.what_to_do.length === 0 ? <p className="text-muted-foreground">No recommended actions.</p> : null}
          {insight.what_to_do.map((item, i) => (
            <div key={i} className="flex gap-4">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 font-semibold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                {i + 1}
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">{item.category}</h3>
                <p className="text-blue-800/80 dark:text-blue-200/80">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
