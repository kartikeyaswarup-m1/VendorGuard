import { FileText, ShieldCheck, UploadCloud } from "lucide-react";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";

export interface FileListItem {
  name: string;
  status?: string;
  meta?: string;
  type?: string;
}

interface FileListProps {
  items: FileListItem[];
  emptyLabel?: string;
  loading?: boolean;
}

// Presentational file list with subtle vendor security affordances
export function FileList({ items, emptyLabel = "No files selected", loading = false }: FileListProps) {
  if (!items.length) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-dashed border-border/70 bg-muted/20 px-3 py-2 text-sm text-muted-foreground">
        <UploadCloud className="h-4 w-4" aria-hidden="true" />
        <span>{emptyLabel}</span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div
          key={item.name}
          className={cn(
            "flex items-center gap-3 rounded-lg border border-border/70 bg-card/60 px-3 py-2 shadow-inner",
            loading && "opacity-70"
          )}
        >
          <div className="rounded-md bg-primary/10 p-2 text-primary">
            {item.type ? <ShieldCheck className="h-4 w-4" aria-hidden="true" /> : <FileText className="h-4 w-4" aria-hidden="true" />}
          </div>
          <div className="flex min-w-0 flex-1 flex-col">
            <span className="truncate text-sm font-semibold text-foreground">{item.name}</span>
            {item.meta ? <span className="truncate text-xs text-muted-foreground">{item.meta}</span> : null}
          </div>
          {item.status ? (
            <Badge variant="info" className="text-[11px]">
              {item.status}
            </Badge>
          ) : null}
        </div>
      ))}
    </div>
  );
}
