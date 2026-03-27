import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface PitchContourVisualizationProps {
  data: any;
  raga: string | null;
}

export default function PitchContourVisualization({ data, raga }: PitchContourVisualizationProps) {
  // Mock pitch data
  const mockPitchData = data?.syllables?.map((s: any, idx: number) => ({
    syllable: s.syllable,
    f0: 150 + Math.sin(idx * 0.5) * 80 + Math.random() * 20,
    duration: 200 + (s.weight === "G" ? 100 : 0)
  })) || [];

  if (!data?.syllables) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Pitch Contour</CardTitle>
          <CardDescription>F0 frequency visualization over syllables</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Analyze text to visualize pitch contour
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Pitch Contour</CardTitle>
        <CardDescription>
          F0 frequency mapping {raga && `with ${raga} Raga rules`}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Chart */}
        <div className="pitch-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockPitchData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="syllable"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                label={{ value: "F0 (Hz)", angle: -90, position: "insideLeft" }}
                domain={[100, 300]}
              />
              <Tooltip
                formatter={(value) => `${Math.round(value as number)} Hz`}
                labelFormatter={(label) => `Syllable: ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="f0"
                stroke="hsl(var(--primary))"
                dot={{ fill: "hsl(var(--primary))", r: 4 }}
                activeDot={{ r: 6 }}
                name="Frequency (Hz)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground mb-1">Min F0</p>
            <p className="text-2xl font-bold">
              {Math.round(Math.min(...mockPitchData.map((d: any) => d.f0)))} Hz
            </p>
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground mb-1">Max F0</p>
            <p className="text-2xl font-bold">
              {Math.round(Math.max(...mockPitchData.map((d: any) => d.f0)))} Hz
            </p>
          </div>
          <div className="rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground mb-1">Avg F0</p>
            <p className="text-2xl font-bold">
              {Math.round(mockPitchData.reduce((a: number, d: any) => a + d.f0, 0) / mockPitchData.length)} Hz
            </p>
          </div>
        </div>

        {/* Information */}
        <div className="rounded-lg border border-border p-4 bg-card/50">
          <p className="text-sm text-muted-foreground">
            The pitch contour shows the fundamental frequency (F0) progression across syllables. 
            Higher frequencies correspond to raised pitch accents (udātta), while lower frequencies indicate anudātta.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
