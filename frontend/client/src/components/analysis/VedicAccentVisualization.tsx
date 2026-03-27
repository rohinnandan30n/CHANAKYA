import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface VedicAccentVisualizationProps {
  data: any;
}

export default function VedicAccentVisualization({ data }: VedicAccentVisualizationProps) {
  const mockAccents = data?.syllables?.map((s: any, idx: number) => ({
    ...s,
    accent: idx % 3 === 0 ? "udatta" : idx % 3 === 1 ? "svarita" : "anudatta"
  })) || [];

  if (!data?.syllables) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Vedic Accents</CardTitle>
          <CardDescription>Udātta, Anudātta, and Svarita markings</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Analyze text to visualize Vedic accents
          </p>
        </CardContent>
      </Card>
    );
  }

  const accentColors = {
    udatta: "border-2 bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300",
    svarita: "border-2 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300",
    anudatta: "border-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300"
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Vedic Accents</CardTitle>
        <CardDescription>Pitch accent patterns in Vedic Sanskrit</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Accent Display */}
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {mockAccents.map((syllable: any, idx: number) => (
              <div
                key={idx}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg transition-all ${
                  accentColors[syllable.accent as keyof typeof accentColors]
                }`}
              >
                <span className="text-sm font-semibold devanagari-text">
                  {syllable.syllable}
                </span>
                <Badge variant="outline" className="text-xs">
                  {syllable.accent === "udatta" ? "↑" : syllable.accent === "svarita" ? "→" : "↓"}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="space-y-3 pt-4 border-t border-border">
          <p className="text-sm font-medium">Accent Types</p>
          <div className="grid gap-3">
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-amber-500" />
              <div>
                <p className="text-sm font-medium">Udātta (High)</p>
                <p className="text-xs text-muted-foreground">Raised pitch accent</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-blue-500" />
              <div>
                <p className="text-sm font-medium">Svarita (Mid)</p>
                <p className="text-xs text-muted-foreground">Independent pitch accent</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Anudātta (Low)</p>
                <p className="text-xs text-muted-foreground">Unmarked, low pitch</p>
              </div>
            </div>
          </div>
        </div>

        {/* Accent Pattern */}
        <div className="rounded-lg bg-muted p-4">
          <p className="text-sm font-medium mb-2">Accent Pattern</p>
          <p className="font-mono text-sm tracking-wider">
            {mockAccents.map((s: any) => 
              s.accent === "udatta" ? "↑" : s.accent === "svarita" ? "→" : "↓"
            ).join(" ")}
          </p>
        </div>

        {/* Information */}
        <div className="rounded-lg border border-border p-4 bg-card/50">
          <p className="text-sm text-muted-foreground">
            Vedic accents are pitch-based phonemic distinctions found in Rigvedic Sanskrit. 
            They mark the melodic contour of the chant and are essential for proper recitation.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
