import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  BadgeCheck,
  BookOpen,
  Download,
  FileText,
  Loader2,
  RefreshCw,
  Shield,
  Sparkles
} from "lucide-react";

import { ConfidenceBadge } from "./ConfidenceBadge";
import { RiskScoreCard } from "./RiskScoreCard";
import { cn } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { Skeleton } from "./ui/skeleton";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Evidence {
  doc: string;
  page?: number;
  excerpt?: string;
}

interface Control {
  control_id: string;
  control_name: string;
  status: string;
  risk_level?: string;
  confidence?: number;
  frameworks?: string[];
  key_findings?: string[];
  missing_requirements?: string[];
  top_evidence?: Evidence[];
  recommended_actions?: string[];
}

export interface Report {
  vendor_id: string;
  vendor_name?: string;
  overall_risk_score: number;
  analysis_timestamp?: string;
  documents_analyzed?: { filename: string; doc_type?: string }[];
  controls: Control[];
  summary?: string;
  document_count?: number;
  control_count?: number;
}

interface ReportViewProps {
  report: Report | null;
  onRerun: () => void;
  vendorId?: string;
  loading?: boolean;
}

const statusVariant = (status: string) => {
  if (status === "Covered") return "success" as const;
  if (status === "Partial") return "warning" as const;
  if (status === "Missing") return "destructive" as const;
  return "outline" as const;
};

const statusTone = (status: string) => {
  if (status === "Covered") return "text-success-foreground";
  if (status === "Partial") return "text-warning-foreground";
  if (status === "Missing") return "text-destructive-foreground";
  return "text-muted-foreground";
};

const LoadingState = () => (
  <div className="space-y-4">
    <Skeleton className="h-32 w-full" />
    <Skeleton className="h-16 w-full" />
    <Skeleton className="h-12 w-full" />
    <div className="grid gap-3 md:grid-cols-2">
      <Skeleton className="h-44" />
      <Skeleton className="h-44" />
    </div>
  </div>
);

export default function ReportView({ report, onRerun, vendorId, loading = false }: ReportViewProps) {
  const [activeFramework, setActiveFramework] = useState<string>("All");

  useEffect(() => {
    setActiveFramework("All");
  }, [report?.vendor_id]);

  const frameworks = useMemo(() => {
    const set = new Set<string>();
    report?.controls?.forEach((control) => {
      control.frameworks?.forEach((fw) => set.add(fw));
    });
    return ["All", ...Array.from(set)];
  }, [report?.controls]);

  const statusCounts = useMemo(() => {
    const base = { Covered: 0, Partial: 0, Missing: 0 } as Record<string, number>;
    report?.controls?.forEach((c) => {
      if (base[c.status] !== undefined) base[c.status] += 1;
    });
    return base;
  }, [report?.controls]);

  const filteredControls = useMemo(() => {
    if (!report) return [];
    if (activeFramework === "All") return report.controls;
    return report.controls.filter((c) => c.frameworks?.includes(activeFramework));
  }, [activeFramework, report]);

  const exportReport = async (format: string) => {
    try {
      const url = `${API_BASE}/api/export/${vendorId || report?.vendor_id}/${format}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Export failed");

      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `vendorguard_${report?.vendor_id}_${new Date().toISOString().split("T")[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (err: any) {
      alert("Export failed: " + err.message);
    }
  };

  if (loading) {
    return (
      <Card className="bg-card/70 min-h-[340px]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary" aria-hidden="true" /> Running analysis...
          </CardTitle>
          <CardDescription>We are extracting, embedding, and evaluating controls.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
          <LoadingState />
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card className="border-dashed border-border/60 bg-card/70">
        <CardHeader className="items-start gap-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" /> No report yet
          </CardTitle>
          <CardDescription>Upload a PDF and analyze to see vendor risk findings here.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <TooltipProvider>
      <div className="space-y-4">
        <RiskScoreCard
          score={report.overall_risk_score}
          timestamp={report.analysis_timestamp}
          vendorName={report.vendor_name || report.vendor_id}
        />

        <Card className="bg-card/80">
          <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-xl font-semibold">
                <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
                {report.vendor_name || report.vendor_id || "Vendor Report"}
              </CardTitle>
              <CardDescription>
                {report.analysis_timestamp && new Date(report.analysis_timestamp).toLocaleString()}
              </CardDescription>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="secondary" size="sm" onClick={() => exportReport("json")}>
                <Download className="h-4 w-4" aria-hidden="true" /> JSON
              </Button>
              <Button variant="secondary" size="sm" onClick={() => exportReport("csv")}>
                <Download className="h-4 w-4" aria-hidden="true" /> CSV
              </Button>
              <Button size="sm" onClick={onRerun}>
                <RefreshCw className="h-4 w-4" aria-hidden="true" /> Re-analyze
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border border-border/70 bg-muted/20 p-3">
                <p className="text-xs text-muted-foreground">Documents</p>
                <p className="text-lg font-semibold text-foreground">
                  {report.documents_analyzed?.length ?? report.document_count ?? "—"}
                </p>
                {report.documents_analyzed?.length ? (
                  <p className="text-xs text-muted-foreground">
                    {report.documents_analyzed.map((d) => `${d.filename} (${d.doc_type || "unknown"})`).join(", ")}
                  </p>
                ) : null}
              </div>
              <div className="rounded-lg border border-border/70 bg-muted/20 p-3">
                <p className="text-xs text-muted-foreground">Controls evaluated</p>
                <p className="text-lg font-semibold text-foreground">{report.control_count ?? report.controls.length}</p>
                <Progress value={Math.min(100, (report.controls.length / 100) * 100)} aria-label="Controls progress" />
              </div>
              <div className="rounded-lg border border-border/70 bg-muted/20 p-3">
                <p className="text-xs text-muted-foreground">Summary</p>
                <p className="text-sm text-foreground">
                  {report.summary || "Automated summary of key risks and controls."}
                </p>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border border-success/30 bg-success/5 p-3">
                <p className="text-xs text-success-foreground">Covered</p>
                <p className="text-lg font-semibold text-foreground">{statusCounts.Covered}</p>
              </div>
              <div className="rounded-lg border border-warning/40 bg-warning/10 p-3">
                <p className="text-xs text-warning-foreground">Partial</p>
                <p className="text-lg font-semibold text-foreground">{statusCounts.Partial}</p>
              </div>
              <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-3">
                <p className="text-xs text-destructive-foreground">Missing</p>
                <p className="text-lg font-semibold text-foreground">{statusCounts.Missing}</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-muted-foreground">Frameworks</h4>
                <Badge variant="outline" className="text-[11px]">
                  {frameworks.length - 1} detected
                </Badge>
              </div>
              <Tabs value={activeFramework} onValueChange={setActiveFramework} className="w-full">
                <TabsList>
                  {frameworks.map((fw) => (
                    <TabsTrigger key={fw} value={fw} className="capitalize">
                      {fw === "All" ? "All" : fw.toUpperCase()}
                    </TabsTrigger>
                  ))}
                </TabsList>
                <TabsContent
                  value={activeFramework}
                  className="mt-3 border border-border/60 bg-muted/10"
                >
                  <div className="scroll-area max-h-[70vh] space-y-3 overflow-auto pr-1">
                    {filteredControls.length === 0 ? (
                      <div className="flex items-center gap-2 rounded-lg border border-dashed border-border/60 bg-card/70 px-4 py-3 text-sm text-muted-foreground">
                        <AlertCircle className="h-4 w-4" aria-hidden="true" /> No controls match this framework.
                      </div>
                    ) : (
                      filteredControls.map((control) => (
                        <Card
                          key={control.control_id}
                          className="border border-border/70 bg-card/70 p-4 shadow-inner"
                        >
                          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                            <div className="space-y-2">
                              <div className="flex flex-wrap items-center gap-2">
                                <Badge variant="outline" className="text-[11px]">
                                  {control.control_id}
                                </Badge>
                                {(control.frameworks || []).map((fw) => (
                                  <Badge key={fw} variant="info" className="text-[11px] uppercase">
                                    {fw}
                                  </Badge>
                                ))}
                              </div>
                              <div>
                                <p className="text-base font-semibold text-foreground">{control.control_name}</p>
                                <p className="text-xs text-muted-foreground">
                                  Risk: <span className={cn("font-semibold", statusTone(control.status))}>{control.risk_level || "—"}</span>
                                </p>
                              </div>
                              <div className="flex flex-wrap items-center gap-2">
                                <Badge variant={statusVariant(control.status)} className="text-[11px]">
                                  {control.status}
                                </Badge>
                                <ConfidenceBadge confidence={control.confidence} />
                              </div>
                            </div>

                            <div className="w-full space-y-3 md:w-72">
                              {control.key_findings?.length ? (
                                <div className="rounded-lg border border-border/60 bg-muted/20 p-3 text-xs text-foreground">
                                  <div className="mb-2 flex items-center gap-2 font-semibold">
                                    <BadgeCheck className="h-4 w-4 text-primary" aria-hidden="true" /> Key findings
                                  </div>
                                  <ul className="list-disc space-y-1 pl-4 text-muted-foreground">
                                    {control.key_findings.map((finding, idx) => (
                                      <li key={idx}>{finding}</li>
                                    ))}
                                  </ul>
                                </div>
                              ) : null}

                              {control.missing_requirements?.length ? (
                                <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive-foreground">
                                  <div className="mb-2 flex items-center gap-2 font-semibold">
                                    <AlertCircle className="h-4 w-4" aria-hidden="true" /> Missing requirements
                                  </div>
                                  <ul className="list-disc space-y-1 pl-4">
                                    {control.missing_requirements.map((req, idx) => (
                                      <li key={idx}>{req}</li>
                                    ))}
                                  </ul>
                                </div>
                              ) : null}

                              {control.top_evidence?.length ? (
                                <div className="rounded-lg border border-border/60 bg-muted/10 p-3 text-xs text-foreground">
                                  <div className="mb-2 flex items-center gap-2 font-semibold">
                                    <BookOpen className="h-4 w-4 text-primary" aria-hidden="true" /> Evidence
                                  </div>
                                  <div className="space-y-2">
                                    {control.top_evidence.map((evidence, idx) => (
                                      <Tooltip key={`${evidence.doc}-${idx}`}>
                                        <TooltipTrigger asChild>
                                          <div className="flex items-start gap-2 rounded-md border border-border/50 bg-background/60 px-2 py-2">
                                            <FileText className="mt-0.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                                            <div className="flex-1">
                                              <p className="text-xs font-semibold text-foreground">{evidence.doc}</p>
                                              <p className="text-[11px] text-muted-foreground">Page {evidence.page ?? "—"}</p>
                                            </div>
                                          </div>
                                        </TooltipTrigger>
                                        {evidence.excerpt ? (
                                          <TooltipContent className="max-w-xs text-left text-xs leading-snug">
                                            {evidence.excerpt}
                                          </TooltipContent>
                                        ) : null}
                                      </Tooltip>
                                    ))}
                                  </div>
                                </div>
                              ) : null}

                              {control.recommended_actions?.length ? (
                                <div className="rounded-lg border border-warning/40 bg-warning/10 p-3 text-xs text-warning-foreground">
                                  <div className="mb-2 flex items-center gap-2 font-semibold">
                                    <Sparkles className="h-4 w-4" aria-hidden="true" /> Recommended actions
                                  </div>
                                  <ul className="list-disc space-y-1 pl-4">
                                    {control.recommended_actions.map((action, idx) => (
                                      <li key={idx}>{action}</li>
                                    ))}
                                  </ul>
                                </div>
                              ) : null}
                            </div>
                          </div>
                        </Card>
                      ))
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}
