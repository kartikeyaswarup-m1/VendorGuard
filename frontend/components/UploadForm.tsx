import React, { useCallback, useRef, useState } from "react";
import { Loader2, RefreshCw, ShieldCheck, UploadCloud } from "lucide-react";

import { cn } from "../lib/utils";
import { FileList } from "./FileList";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UploadResponse {
  vendor_id: string;
  filename: string;
  path: string;
  document_type?: string;
}

interface UploadFormProps {
  onUploaded: (data: UploadResponse) => void;
}

export default function UploadForm({ onUploaded }: UploadFormProps) {
  const [vendorId, setVendorId] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [dragging, setDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const onDrop = useCallback((event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) {
      setFile(dropped);
    }
  }, []);

  const onBrowse = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = useCallback(async () => {
    if (!vendorId) return alert("Enter vendor id (eg: vendor-001)");
    if (!file) return alert("Select a PDF file");
    setLoading(true);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API_BASE}/api/upload/${vendorId}`, {
        method: "POST",
        body: form
      });

      const text = await res.text();
      let data: UploadResponse | null = null;
      try {
        data = text ? JSON.parse(text) : null;
      } catch (e) {
        throw new Error("Upload: failed to parse server response: " + text);
      }

      if (!res.ok) {
        throw new Error((data as any)?.detail || JSON.stringify(data) || "Upload failed");
      }

      onUploaded(data!);
    } catch (err: any) {
      console.error("Upload error:", err);
      alert("Upload error: " + err.message);
    } finally {
      setLoading(false);
    }
  }, [file, onUploaded, vendorId]);

  const reset = () => {
    setFile(null);
    setVendorId("");
  };

  const selectedFiles = file
    ? [
        {
          name: file.name,
          status: loading ? "Uploading" : "Ready to upload",
          meta: `${(file.size / 1024 / 1024).toFixed(2)} MB • PDF`,
          type: "pdf"
        }
      ]
    : [];

  return (
    <Card className="border-primary/20 bg-card/80">
      <CardHeader className="flex flex-row items-start justify-between gap-3">
        <div>
          <CardTitle className="text-lg">Upload vendor documents</CardTitle>
          <CardDescription>Drop a PDF or browse to upload for analysis.</CardDescription>
        </div>
        <ShieldCheck className="h-6 w-6 text-primary" aria-hidden="true" />
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-foreground">Vendor ID</label>
          <Input
            placeholder="vendor-001"
            value={vendorId}
            onChange={(e) => setVendorId(e.target.value)}
            disabled={loading}
            aria-label="Vendor ID"
          />
        </div>

        <label
          onDrop={onDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onClick={onBrowse}
          className={cn(
            "group relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border/70 bg-muted/20 px-6 py-8 text-center transition hover:border-primary hover:bg-primary/5",
            dragging && "border-primary bg-primary/5"
          )}
        >
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            {loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : <UploadCloud className="h-5 w-5" aria-hidden="true" />}
          </div>
          <p className="text-sm font-semibold text-foreground">Drag & drop PDF</p>
          <p className="text-xs text-muted-foreground">or click to browse from your computer</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            className="vg-file-input"
            hidden
            style={{ display: "none" }}
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            aria-label="File upload"
          />
        </label>

        <div className="space-y-2">
          <FileList items={selectedFiles} emptyLabel="No file selected yet" loading={loading} />
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Button onClick={handleUpload} disabled={loading} size="lg" className="w-full">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <UploadCloud className="h-4 w-4" aria-hidden="true" />}
            {loading ? "Uploading..." : "Upload"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={reset}
            disabled={loading}
            size="lg"
            className="w-full"
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" /> Reset
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
