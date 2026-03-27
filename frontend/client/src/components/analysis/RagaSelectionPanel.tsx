import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

interface RagaSelectionPanelProps {
  onSelect: (raga: string) => void;
}

const ragas = [
  {
    name: "Yaman",
    arohana: "Sa Re Ga Ma Pa Dha Ni Sa",
    avarohana: "Sa Ni Dha Pa Ma Ga Re Sa",
    vadi: "Pa",
    samvadi: "Sa",
    phrases: ["Pa-Dha-Ni", "Ga-Ma-Pa", "Re-Ga"]
  },
  {
    name: "Bhairav",
    arohana: "Sa Re Ga Ma Pa Dha Ni Sa",
    avarohana: "Sa Ni Dha Pa Ma Ga Re Sa",
    vadi: "Ma",
    samvadi: "Sa",
    phrases: ["Ma-Ga-Re", "Dha-Pa-Ma", "Ni-Sa"]
  },
  {
    name: "Kharaharapriya",
    arohana: "Sa Re Ga Ma Pa Dha Ni Sa",
    avarohana: "Sa Ni Dha Pa Ma Ga Re Sa",
    vadi: "Dha",
    samvadi: "Re",
    phrases: ["Dha-Ni-Sa", "Ga-Ma-Pa", "Re-Ga"]
  }
];

export default function RagaSelectionPanel({ onSelect }: RagaSelectionPanelProps) {
  const [selectedRaga, setSelectedRaga] = useState<string | null>(null);
  const raga = ragas.find(r => r.name === selectedRaga);

  const handleSelect = (ragaName: string) => {
    setSelectedRaga(ragaName);
    onSelect(ragaName);
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Raga Selection</CardTitle>
        <CardDescription>Choose melodic framework</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Select value={selectedRaga || ""} onValueChange={handleSelect}>
          <SelectTrigger>
            <SelectValue placeholder="Select a Raga..." />
          </SelectTrigger>
          <SelectContent>
            {ragas.map((r) => (
              <SelectItem key={r.name} value={r.name}>
                {r.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {raga && (
          <div className="space-y-4 pt-4 border-t border-border">
            {/* Raga Details */}
            <div className="space-y-3">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Arohana (Ascending)</p>
                <p className="text-sm font-medium">{raga.arohana}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Avarohana (Descending)</p>
                <p className="text-sm font-medium">{raga.avarohana}</p>
              </div>
            </div>

            {/* Vadi & Samvadi */}
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-lg bg-muted p-3">
                <p className="text-xs text-muted-foreground mb-1">Vadi (Dominant)</p>
                <p className="text-lg font-bold" style={{ color: 'oklch(0.65 0.22 40)' }}>{raga.vadi}</p>
              </div>
              <div className="rounded-lg bg-muted p-3">
                <p className="text-xs text-muted-foreground mb-1">Samvadi (Subdominant)</p>
                <p className="text-lg font-bold" style={{ color: 'oklch(0.55 0.18 250)' }}>{raga.samvadi}</p>
              </div>
            </div>

            {/* Characteristic Phrases */}
            <div>
              <p className="text-xs text-muted-foreground mb-2">Characteristic Phrases</p>
              <div className="flex flex-wrap gap-2">
                {raga.phrases.map((phrase, idx) => (
                  <Badge key={idx} variant="secondary">
                    {phrase}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
