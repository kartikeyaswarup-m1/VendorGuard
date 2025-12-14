import { useEffect, useMemo, useState } from "react";
import { Filter, History, Shield, Sparkles } from "lucide-react";

import ReportView, { type Report } from "../components/ReportView";
import { StatusStepper, type StepItem } from "../components/StatusStepper";
import UploadForm, { type UploadResponse } from "../components/UploadForm";
import { FileList } from "../components/FileList";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type UploadedFile = UploadResponse;

type HistoryItem = {
  analysis_timestamp: string;
  risk_score: number;
  document_count: number;
  control_count: number;
};

export default function Home() {
  const [uploaded, setUploaded] = useState<UploadedFile | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [running, setRunning] = useState(false);
  const [frameworkFilter, setFrameworkFilter] = useState<string>("");
  const [frameworks, setFrameworks] = useState<string[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/controls/frameworks`)
      .then((res) => res.json())
      .then((data) => setFrameworks(data))
      .catch((err) => console.error("Failed to load frameworks:", err));
  }, []);

  useEffect(() => {
    if (uploaded?.vendor_id) {
      fetch(`${API_BASE}/api/history/${uploaded.vendor_id}?limit=5`)
        .then((res) => res.json())
        .then((data) => setHistory(data))
        .catch((err) => console.error("Failed to load history:", err));
    }
  }, [uploaded?.vendor_id]);

  async function handleUploaded(data: UploadResponse) {
    setUploaded(data);
  }

  async function runAnalyze(vendorId: string, filePaths?: string[]) {
    setRunning(true);
    try {
      if (!filePaths || filePaths.length === 0) {
        if (!uploaded || !uploaded.path)
          throw new Error("No uploaded file path available. Upload a PDF first.");
        filePaths = [uploaded.path];
      }

      const body = {
        vendor_name: vendorId,
        file_paths: filePaths,
        framework_filter: frameworkFilter || null
      };

      const res = await fetch(`${API_BASE}/api/analyze/${vendorId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const text = await res.text();
      let data: Report | null = null;
      try {
        data = text ? JSON.parse(text) : null;
      } catch (e) {
        throw new Error("Analyze: failed to parse server response: " + text);
      }

      if (!res.ok) {
        throw new Error((data as any)?.detail || JSON.stringify(data) || "Analyze failed");
      }

      setReport(data!);
    } catch (err: any) {
      console.error("Analyze failed:", err);
      alert("Analyze failed: " + err.message);
    } finally {
      setRunning(false);
    }
  }

  const steps: StepItem[] = useMemo(() => {
    const base: StepItem[] = [
      { title: "Extract", description: "Parse PDFs and normalize", state: "pending" },
      { title: "Embed", description: "Create vector embeddings", state: "pending" },
      { title: "Analyze", description: "Match controls and map gaps", state: "pending" },
      { title: "Generate report", description: "Assemble findings", state: "pending" }
    ];

    return base.map((step, idx) => {
      if (report) return { ...step, state: "done" as const };
      if (running) return { ...step, state: idx === 0 ? "done" : idx === 1 ? "active" : "pending" };
      if (uploaded) return { ...step, state: idx === 0 ? "active" : "pending" };
      return step;
    });
  }, [report, running, uploaded]);

  return (
    <div className="page-shell space-y-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-emerald-400 text-lg font-bold text-primary-foreground shadow-glow">
            VG
          </div>
          <div>
            <p className="text-xl font-semibold text-foreground">VendorGuard</p>
            <p className="text-sm text-muted-foreground">Enterprise vendor risk and compliance dashboard</p>
          </div>
        </div>
        <Badge variant="info" className="text-[11px]">
          Live demo • AI-powered analysis
        </Badge>
      </header>

      <div className="card-grid items-start">
        <div className="space-y-4">
          <UploadForm onUploaded={handleUploaded} />

          {uploaded ? (
            <Card className="bg-card/80">
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div>
                  <CardTitle className="text-lg">Uploaded document</CardTitle>
                  <CardDescription>Ready for analysis</CardDescription>
                </div>
                <Badge variant="outline" className="text-[11px]">
                  {uploaded.document_type || "Unknown"}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                <FileList
                  items={[
                    {
                      name: uploaded.filename,
                      status: "Uploaded",
                      meta: undefined,
                      type: uploaded.document_type
                    }
                  ]}
                />

                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
                    <Filter className="h-4 w-4" aria-hidden="true" /> Filter by framework (optional)
                  </label>
                  <div className="relative">
                    <select
                      value={frameworkFilter}
                      onChange={(e) => setFrameworkFilter(e.target.value)}
                      className="w-full appearance-none rounded-lg border border-border/70 bg-background/70 px-3 py-2 text-sm text-foreground shadow-inner focus:border-primary focus:outline-none"
                    >
                      <option value="">All frameworks</option>
                      {frameworks.map((fw) => (
                        <option key={fw} value={fw}>
                          {fw}
                        </option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-muted-foreground">
                      <Filter className="h-4 w-4" aria-hidden="true" />
                    </div>
                  </div>
                </div>

                <Button
                  size="lg"
                  className="w-full"
                  onClick={() => runAnalyze(uploaded.vendor_id, [uploaded.path])}
                  disabled={running}
                >
                  <Shield className="h-4 w-4" aria-hidden="true" />
                  {running ? "Analyzing..." : "Analyze documents"}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-dashed border-border/60 bg-card/60">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" /> No upload yet
                </CardTitle>
                <CardDescription>Upload a vendor document to begin.</CardDescription>
              </CardHeader>
            </Card>
          )}

          <Card className="bg-card/80">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">Analysis pipeline</CardTitle>
                <CardDescription>Real-time progress through each step</CardDescription>
              </div>
              <Badge variant="outline" className="text-[11px]">
                {running ? "Running" : report ? "Completed" : "Idle"}
              </Badge>
            </CardHeader>
            <CardContent>
              <StatusStepper steps={steps} />
            </CardContent>
          </Card>

          {history.length > 0 ? (
            <Card className="bg-card/80">
              <CardHeader className="flex flex-row items-center gap-2">
                <History className="h-4 w-4 text-primary" aria-hidden="true" />
                <div>
                  <CardTitle className="text-lg">Recent analyses</CardTitle>
                  <CardDescription>Last 5 runs for this vendor</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {history.slice(0, 5).map((h, idx) => (
                  <div
                    key={`${h.analysis_timestamp}-${idx}`}
                    className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/20 px-3 py-2"
                  >
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {new Date(h.analysis_timestamp).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Docs: {h.document_count} • Controls: {h.control_count}
                      </p>
                    </div>
                    <Badge variant="info" className="text-[11px]">
                      Risk {h.risk_score}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : uploaded ? (
            <Card className="border-dashed border-border/60 bg-card/60">
              <CardHeader className="flex flex-row items-center gap-2">
                <History className="h-4 w-4 text-primary" aria-hidden="true" />
                <div>
                  <CardTitle className="text-lg">Recent analyses</CardTitle>
                  <CardDescription>No previous runs yet for this vendor.</CardDescription>
                </div>
              </CardHeader>
            </Card>
          ) : null}
        </div>

        <div className="space-y-4">
          <Card className="panel-card">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl">Security posture at a glance</CardTitle>
                <CardDescription>Automated vendor risk scoring powered by RAG</CardDescription>
              </div>

              {/* <Badge variant="outline" className="text-[11px]">
                AI + Human review ready
              </Badge> */}

            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-border/60 bg-card/80 p-3">
                <p className="text-xs text-muted-foreground">Upload</p>
                <p className="text-lg font-semibold text-foreground">PDF contracts, SOC2, ISO</p>
              </div>
              <div className="rounded-lg border border-border/60 bg-card/80 p-3">
                <p className="text-xs text-muted-foreground">Analyze</p>
                <p className="text-lg font-semibold text-foreground">Control mapping & gaps</p>
              </div>
              <div className="rounded-lg border border-border/60 bg-card/80 p-3">
                <p className="text-xs text-muted-foreground">Report</p>
                <p className="text-lg font-semibold text-foreground">Evidence-backed findings</p>
              </div>
            </CardContent>
          </Card>

          <ReportView
            report={report}
            onRerun={() => uploaded && runAnalyze(uploaded.vendor_id, [uploaded.path])}
            vendorId={uploaded?.vendor_id}
            loading={running}
          />
        </div>
      </div>
    </div>
  );
}
