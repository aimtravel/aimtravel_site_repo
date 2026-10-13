import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Demo() {
  const [n, setN] = useState(0);
  
  return (
    <div className={cn("p-4")}>
      <Button onClick={() => setN(n + 1)}>{n}</Button>
    </div>
  );
}
