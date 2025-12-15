import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";

interface ConfidenceBadgeProps {
  confidence?: number;
}

// Compact confidence indicator used inside findings cards
export function ConfidenceBadge({ confidence = 0 }: ConfidenceBadgeProps) {
  const safeValue = Number.isFinite(confidence) ? Math.max(0, Math.min(100, confidence)) : 0;
  return (
    <div className="flex w-44 items-center gap-3 rounded-lg border border-border/80 bg-muted/30 px-3 py-2">
      <div className="flex flex-col gap-1">
        <Badge variant="outline" className="text-[11px]">
          Confidence
        </Badge>
        <span className="text-sm font-semibold text-foreground">{safeValue}%</span>
      </div>
      <Progress value={safeValue} className="h-2 flex-1" aria-label="Confidence score" />
    </div>
  );
}
