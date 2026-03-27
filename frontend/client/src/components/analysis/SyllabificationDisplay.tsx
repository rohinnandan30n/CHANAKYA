import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface SyllabificationDisplayProps {
  data: any;
}

export default function SyllabificationDisplay({ data }: SyllabificationDisplayProps) {
  if (!data?.syllables) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Syllabification</CardTitle>
          <CardDescription>Laghu-Guru weight marking for each syllable</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Analyze text to see syllable breakdown
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Syllabification</CardTitle>
        <CardDescription>
          Total syllables: {data.syllables.length} • Pattern: {data.syllables.map((s: any) => s.weight).join("")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Syllable Grid */}
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {data.syllables.map((syllable: any, idx: number) => (
              <div
                key={idx}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-all ${
                  syllable.weight === "L"
                    ? "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/30"
                    : "border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-900/30"
                }`}
              >
                <span className="text-sm font-semibold devanagari-text">
                  {syllable.syllable}
                </span>
                <Badge
                  variant={syllable.weight === "L" ? "secondary" : "default"}
                  className="text-xs"
                >
                  {syllable.weight === "L" ? "Laghu" : "Guru"}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded bg-blue-100 dark:bg-blue-900 border border-blue-300 dark:border-blue-700" />
            <span className="text-sm">Laghu (L) - Light syllable</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded bg-amber-100 dark:bg-amber-900 border border-amber-300 dark:border-amber-700" />
            <span className="text-sm">Guru (G) - Heavy syllable</span>
          </div>
        </div>

        {/* Pattern Analysis */}
        <div className="rounded-lg bg-muted p-4">
          <p className="text-sm font-medium mb-2">Metrical Pattern</p>
          <p className="font-mono text-lg tracking-wider">
            {data.syllables.map((s: any) => s.weight).join(" ")}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
