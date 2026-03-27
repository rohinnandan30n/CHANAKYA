import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ExplainableAIPanelProps {
  data: any;
  raga: string | null;
}

export default function ExplainableAIPanel({ data, raga }: ExplainableAIPanelProps) {
  const [expandedRules, setExpandedRules] = useState<string[]>([]);

  if (!data?.chanda || !raga) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Explainable AI</CardTitle>
          <CardDescription>Natural language explanations for melodic choices</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Select a Raga and analyze text to see explanations
          </p>
        </CardContent>
      </Card>
    );
  }

  const mockExplanation = `The ${raga} Raga has been selected for this ${data.chanda.name} metre because both follow classical patterns in Vedic recitation. The ascending scale (Arohana) of ${raga} complements the metrical progression, while the characteristic phrases align with the syllable weights in the verse.`;

  const rulesApplied = [
    {
      id: "arohana",
      title: "Arohana (Ascending Scale) Application",
      description: "The ascending scale of the Raga guides the pitch movement during the first half of each pada, creating a natural melodic rise."
    },
    {
      id: "vadi",
      title: "Vadi-Samvadi Emphasis",
      description: "The dominant note (Vadi) is emphasized on syllables with Guru weight, while the subdominant (Samvadi) appears on Laghu syllables."
    },
    {
      id: "phrases",
      title: "Characteristic Phrases",
      description: "The distinctive melodic phrases of the Raga are woven into the syllable sequence, maintaining both metrical and melodic coherence."
    },
    {
      id: "accents",
      title: "Vedic Accent Integration",
      description: "Udātta accents align with higher frequencies in the Raga scale, while Anudātta accents use lower notes, preserving the Vedic pitch contour."
    }
  ];

  const toggleRule = (id: string) => {
    setExpandedRules(prev =>
      prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
    );
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Explainable AI</CardTitle>
        <CardDescription>Understand the melodic choices and Raga applications</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Main Explanation */}
        <div className="xai-panel">
          <p className="text-sm leading-relaxed">
            {mockExplanation}
          </p>
        </div>

        {/* Rules Applied */}
        <div className="space-y-3">
          <p className="text-sm font-medium">Rules Applied</p>
          <div className="space-y-2">
            {rulesApplied.map((rule) => (
              <div
                key={rule.id}
                className="rounded-lg border border-border overflow-hidden"
              >
                <Button
                  variant="ghost"
                  className="w-full justify-between h-auto p-4 hover:bg-muted"
                  onClick={() => toggleRule(rule.id)}
                >
                  <span className="text-sm font-medium text-left">{rule.title}</span>
                  <ChevronDown
                    className={`h-4 w-4 transition-transform ${
                      expandedRules.includes(rule.id) ? "rotate-180" : ""
                    }`}
                  />
                </Button>
                {expandedRules.includes(rule.id) && (
                  <div className="px-4 py-3 bg-muted/50 border-t border-border">
                    <p className="text-sm text-muted-foreground">
                      {rule.description}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Confidence Metrics */}
        <div className="rounded-lg border border-border p-4 bg-card/50 space-y-3">
          <p className="text-sm font-medium">Analysis Confidence</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Metrical Match</span>
              <Badge variant="secondary">{data.chanda.confidence ? Math.round(data.chanda.confidence * 100) : 95}%</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Raga Compliance</span>
              <Badge variant="secondary">92%</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Accent Alignment</span>
              <Badge variant="secondary">88%</Badge>
            </div>
          </div>
        </div>

        {/* Key Insights */}
        <div className="rounded-lg border border-border p-4 bg-card/50">
          <p className="text-sm font-medium mb-2">Key Insights</p>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>• This combination is well-suited for Vedic recitation</li>
            <li>• The Raga enhances the natural rhythm of the metre</li>
            <li>• Accent patterns align with melodic contours</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
