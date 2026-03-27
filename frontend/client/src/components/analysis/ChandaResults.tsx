import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

interface ChandaResultsProps {
  data: any;
}

export default function ChandaResults({ data }: ChandaResultsProps) {
  if (!data?.chanda) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Chanda Identification</CardTitle>
          <CardDescription>Metrical pattern analysis and classification</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Analyze text to identify metrical patterns
          </p>
        </CardContent>
      </Card>
    );
  }

  const chanda = data.chanda;
  const confidence = Math.round((chanda.confidence || 0) * 100);

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Chanda Identification</CardTitle>
        <CardDescription>Identified metrical pattern and classification</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Main Result */}
        <div className="space-y-4">
          <div className="rounded-lg bg-gradient-to-r from-vedic-cream to-muted p-6">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Identified Metre</p>
              <h3 className="text-3xl font-bold text-primary">{chanda.name}</h3>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Confidence Score</span>
              <Badge variant={confidence >= 90 ? "default" : "secondary"}>
                {confidence}%
              </Badge>
            </div>
            <Progress value={confidence} className="h-2" />
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground mb-1">Syllables per Pada</p>
            <p className="text-2xl font-bold">{chanda.syllables_per_pada}</p>
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground mb-1">Total Padas</p>
            <p className="text-2xl font-bold">
              {Math.ceil((data.syllables?.length || 0) / chanda.syllables_per_pada)}
            </p>
          </div>
        </div>

        {/* Gana Pattern */}
        <div className="space-y-3">
          <p className="text-sm font-medium">Gana Pattern</p>
          <div className="rounded-lg bg-muted p-4">
            <p className="font-mono text-sm tracking-widest">
              {chanda.gana_pattern}
            </p>
          </div>
          <p className="text-xs text-muted-foreground">
            Each gana represents three syllables in classical Sanskrit prosody
          </p>
        </div>

        {/* Description */}
        <div className="rounded-lg border border-border p-4 bg-card/50">
          <p className="text-sm text-muted-foreground">
            {chanda.name} is a classical Sanskrit metre commonly used in epic poetry and philosophical texts. 
            It follows a regular pattern of light and heavy syllables across four lines (padas).
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
