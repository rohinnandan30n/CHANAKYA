import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { RotateCcw, Send } from "lucide-react";

interface TextInputPanelProps {
  onAnalysis: (data: any) => void;
}

export default function TextInputPanel({ onAnalysis }: TextInputPanelProps) {
  const [text, setText] = useState("");
  const [scheme, setScheme] = useState("devanagari");
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    setIsLoading(true);
    try {
      // Mock analysis - replace with actual API call
      const mockData = {
        originalText: text,
        canonical_slp1: text,
        syllables: text.split(" ").map((word, idx) => ({
          syllable: word,
          weight: idx % 2 === 0 ? "L" : "G",
          index: idx
        })),
        chanda: {
          name: "Anushtubh",
          syllables_per_pada: 8,
          gana_pattern: "LLGL LLGL",
          confidence: 0.95
        }
      };
      onAnalysis(mockData);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Sanskrit Text Input</CardTitle>
        <CardDescription>Enter or paste your Sanskrit verse</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Transliteration Scheme</label>
          <Select value={scheme} onValueChange={setScheme}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="devanagari">Devanagari</SelectItem>
              <SelectItem value="iast">IAST</SelectItem>
              <SelectItem value="harvard-kyoto">Harvard-Kyoto</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Verse Text</label>
          <Textarea
            placeholder="Enter Sanskrit text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="min-h-32 resize-none font-devanagari"
          />
          <p className="text-xs text-muted-foreground">
            Supports multiple lines and word boundaries
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleAnalyze}
            disabled={!text.trim() || isLoading}
            className="flex-1 gap-2"
          >
            <Send className="h-4 w-4" />
            {isLoading ? "Analyzing..." : "Analyze"}
          </Button>
          <Button
            onClick={handleClear}
            variant="outline"
            size="icon"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
