import * as React from "react";

import { cn } from "../../lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

// Simple skeleton shimmer used while loading
export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-gradient-to-r from-muted/60 via-muted/40 to-muted/60",
        className
      )}
      {...props}
    />
  );
}
