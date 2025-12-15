import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";

export type StepState = "pending" | "active" | "done";

export interface StepItem {
  title: string;
  description?: string;
  state: StepState;
}

interface StatusStepperProps {
  steps: StepItem[];
}

// Slim status stepper to show analysis progress stages
export function StatusStepper({ steps }: StatusStepperProps) {
  const completed = steps.filter((s) => s.state === "done").length;
  const progressValue = Math.round((completed / (steps.length || 1)) * 100);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-foreground">Pipeline progress</div>
        <Badge variant="outline" className="text-[11px]">
          {progressValue}% complete
        </Badge>
      </div>
      <Progress value={progressValue} aria-label="Analysis progress" />
      {steps.map((step, index) => {
        const Icon = step.state === "done" ? CheckCircle2 : step.state === "active" ? Loader2 : Circle;
        return (
          <div
            key={step.title}
            className={cn(
              "flex items-start gap-3 rounded-lg border border-border/70 bg-muted/30 px-3 py-2.5",
              step.state === "active" && "border-primary/60 bg-primary/5 shadow-glow",
              step.state === "done" && "border-success/60 bg-success/5"
            )}
          >
            <div className="mt-0.5 text-primary">
              <Icon className={cn("h-5 w-5", step.state === "active" && "animate-spin")}
                aria-hidden="true" />
            </div>
            <div className="flex flex-1 flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-foreground">{step.title}</span>
                <Badge
                  variant={step.state === "done" ? "success" : step.state === "active" ? "info" : "outline"}
                  className="text-[11px]"
                >
                  {step.state === "done" ? "Completed" : step.state === "active" ? "In progress" : "Queued"}
                </Badge>
              </div>
              {step.description ? (
                <p className="text-xs text-muted-foreground">{step.description}</p>
              ) : null}
            </div>
            {index < steps.length - 1 ? <div className="hidden h-full w-px bg-border/60 md:block" /> : null}
          </div>
        );
      })}
    </div>
  );
}
