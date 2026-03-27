import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Play, Pause, Download, Volume2 } from "lucide-react";

interface AudioPlayerComponentProps {
  data: any;
  raga: string | null;
}

export default function AudioPlayerComponent({ data, raga }: AudioPlayerComponentProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(70);
  const [speed, setSpeed] = useState(1);

  if (!data?.syllables) {
    return (
      <Card className="card-elegant">
        <CardHeader>
          <CardTitle>Audio Synthesis</CardTitle>
          <CardDescription>Synthesized chant playback and controls</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Analyze text to generate audio
          </p>
        </CardContent>
      </Card>
    );
  }

  const duration = 45; // Mock duration in seconds

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle>Audio Synthesis</CardTitle>
        <CardDescription>
          Synthesized chant {raga && `in ${raga} Raga`}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Waveform Visualization */}
        <div className="rounded-lg border border-border bg-muted p-6 h-32 flex items-center justify-center">
          <div className="flex items-end gap-1 h-full">
            {Array.from({ length: 40 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 bg-primary rounded-t transition-all"
                style={{
                  height: `${Math.sin(i * 0.5) * 30 + 40 + Math.random() * 20}%`,
                  opacity: i / 40 <= progress / 100 ? 1 : 0.4
                }}
              />
            ))}
          </div>
        </div>

        {/* Playback Controls */}
        <div className="audio-player flex-col gap-4">
          <div className="flex items-center gap-4">
            <Button
              size="icon"
              onClick={() => setIsPlaying(!isPlaying)}
              className="h-12 w-12"
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6" />
              )}
            </Button>

            <div className="flex-1 space-y-2">
              <Slider
                value={[progress]}
                onValueChange={(value) => setProgress(value[0])}
                max={100}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{formatTime((progress / 100) * duration)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          </div>

          {/* Volume Control */}
          <div className="flex items-center gap-4">
            <Volume2 className="h-4 w-4 text-muted-foreground" />
            <Slider
              value={[volume]}
              onValueChange={(value) => setVolume(value[0])}
              max={100}
              step={1}
              className="flex-1"
            />
            <span className="text-xs text-muted-foreground w-8 text-right">{volume}%</span>
          </div>
        </div>

        {/* Playback Speed */}
        <div className="space-y-2">
          <p className="text-sm font-medium">Playback Speed</p>
          <div className="flex gap-2">
            {[0.75, 1, 1.25, 1.5].map((s) => (
              <Button
                key={s}
                variant={speed === s ? "default" : "outline"}
                size="sm"
                onClick={() => setSpeed(s)}
              >
                {s}x
              </Button>
            ))}
          </div>
        </div>

        {/* Download Button */}
        <Button className="w-full gap-2" variant="outline">
          <Download className="h-4 w-4" />
          Download Audio (WAV)
        </Button>

        {/* Information */}
        <div className="rounded-lg border border-border p-4 bg-card/50 space-y-2">
          <p className="text-sm font-medium">Audio Details</p>
          <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
            <div>Sample Rate: 22050 Hz</div>
            <div>Bit Depth: 16-bit</div>
            <div>Duration: {formatTime(duration)}</div>
            <div>Format: WAV / MP3</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
