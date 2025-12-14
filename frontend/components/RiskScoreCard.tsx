import { AlertTriangle, ShieldHalf, ShieldQuestion } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";

interface RiskScoreCardProps {
  score?: number;
  timestamp?: string;
  vendorName?: string;
}

function getRiskVariant(score: number) {
  if (score >= 70) return { label: "High", variant: "destructive", icon: AlertTriangle };
  if (score >= 40) return { label: "Medium", variant: "warning", icon: ShieldHalf };
  return { label: "Low", variant: "success", icon: ShieldQuestion };
}

// Vendor risk overview card used in report view
export function RiskScoreCard({ score = 0, timestamp, vendorName }: RiskScoreCardProps) {
  const { label, variant, icon: Icon } = getRiskVariant(score);

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/10 via-card/90 to-background">
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <div>
          <CardTitle className="text-base text-muted-foreground">Vendor Risk Score</CardTitle>
          <p className="text-lg font-semibold text-foreground">{vendorName || "Vendor"}</p>
        </div>
        <Badge
          variant={variant as any}
          className={cn(
            "text-xs font-semibold",
            variant === "warning" && "bg-warning/15 text-warning-foreground",
            variant === "destructive" && "bg-destructive/15 text-destructive-foreground",
            variant === "success" && "bg-success/15 text-success-foreground"
          )}
        >
          <Icon className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" /> {label} Risk
        </Badge>
      </CardHeader>
      <CardContent className="flex items-center justify-between gap-4">
        <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary/20 via-primary/10 to-transparent p-1">
          <div className="flex h-full w-full items-center justify-center rounded-full bg-card text-4xl font-bold shadow-inner">
            {Math.round(score)}
          </div>
          <div className="absolute inset-0 rounded-full border border-primary/30" />
        </div>
        <div className="flex flex-1 flex-col gap-2 text-sm text-muted-foreground">
          <p>
            Composite score based on detected controls, gaps, and provided evidence. Lower is safer.
          </p>
          {timestamp ? (
            <p className="text-xs text-muted-foreground/80">Analyzed on {new Date(timestamp).toLocaleString()}</p>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
