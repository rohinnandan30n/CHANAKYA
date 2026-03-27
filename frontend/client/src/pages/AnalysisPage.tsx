import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Save, Download, Trash2 } from "lucide-react";
import { useLocation } from "wouter";
import { useState } from "react";
import TextInputPanel from "@/components/analysis/TextInputPanel";
import SyllabificationDisplay from "@/components/analysis/SyllabificationDisplay";
import ChandaResults from "@/components/analysis/ChandaResults";
import VedicAccentVisualization from "@/components/analysis/VedicAccentVisualization";
import RagaSelectionPanel from "@/components/analysis/RagaSelectionPanel";
import PitchContourVisualization from "@/components/analysis/PitchContourVisualization";
import AudioPlayerComponent from "@/components/analysis/AudioPlayerComponent";
import ExplainableAIPanel from "@/components/analysis/ExplainableAIPanel";
import HistoryLibrary from "@/components/analysis/HistoryLibrary";
import RagaNoteSphere from "@/components/3d/RagaNoteSphere";
import SyllableBlock3D from "@/components/3d/SyllableBlock3D";
import AnimatedWaveform3D from "@/components/3d/AnimatedWaveform3D";
import MantraVisualization from "@/components/analysis/MantraVisualization";

export default function AnalysisPage() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();
  const [activeTab, setActiveTab] = useState("input");
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [selectedRaga, setSelectedRaga] = useState<string | null>(null);

  if (!isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>Please sign in to access the analysis tool</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setLocation("/")} className="w-full">
              Return to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-card/80 backdrop-blur-sm">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setLocation("/")}
              className="gap-2"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-xl font-semibold">Sanskrit Analysis Studio</h1>
              <p className="text-sm text-muted-foreground">Welcome, {user?.name}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Save className="h-4 w-4" />
              Save
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Export
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Left Panel - Input & Controls */}
          <div className="lg:col-span-1 space-y-6">
            <TextInputPanel onAnalysis={setAnalysisData} />
            <RagaSelectionPanel onSelect={setSelectedRaga} />
            <HistoryLibrary onLoad={setAnalysisData} />
          </div>

          {/* Right Panel - Analysis Results */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-4 lg:grid-cols-4 mb-6 overflow-x-auto">
                <TabsTrigger value="input" className="text-xs sm:text-sm">Input</TabsTrigger>
                <TabsTrigger value="mantras" className="text-xs sm:text-sm">Mantras</TabsTrigger>
                <TabsTrigger value="syllables" className="text-xs sm:text-sm">Syllables</TabsTrigger>
                <TabsTrigger value="chanda" className="text-xs sm:text-sm">Chanda</TabsTrigger>
                <TabsTrigger value="accents" className="text-xs sm:text-sm">Accents</TabsTrigger>
                <TabsTrigger value="pitch" className="text-xs sm:text-sm">Pitch</TabsTrigger>
                <TabsTrigger value="audio" className="text-xs sm:text-sm">Audio</TabsTrigger>
                <TabsTrigger value="xai" className="text-xs sm:text-sm">XAI</TabsTrigger>
              </TabsList>

              <TabsContent value="input" className="space-y-4">
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle>Input Text</CardTitle>
                    <CardDescription>Your Sanskrit verse for analysis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {analysisData?.originalText ? (
                      <div className="space-y-4">
                        <div className="rounded-lg bg-muted p-4">
                          <p className="devanagari-text text-lg">{analysisData.originalText}</p>
                        </div>
                        <div className="rounded-lg bg-muted p-4">
                          <p className="sanskrit-serif text-sm text-muted-foreground">
                            Canonical SLP1: {analysisData.canonical_slp1}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-center text-muted-foreground py-8">
                        Enter text in the left panel to begin analysis
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="mantras" className="space-y-4">
                <MantraVisualization />
              </TabsContent>

              <TabsContent value="syllables" className="space-y-4">
                <SyllabificationDisplay data={analysisData} />
                {analysisData?.syllables && (
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle>3D Syllable Visualization</CardTitle>
                      <CardDescription>Interactive 3D representation of syllables with Laghu-Guru weights</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <SyllableBlock3D syllables={analysisData.syllables} />
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="chanda" className="space-y-4">
                <ChandaResults data={analysisData} />
              </TabsContent>

              <TabsContent value="accents" className="space-y-4">
                <VedicAccentVisualization data={analysisData} />
              </TabsContent>

              <TabsContent value="pitch" className="space-y-4">
                <PitchContourVisualization data={analysisData} raga={selectedRaga} />
                {selectedRaga && (
                  <Card className="card-elegant">
                    <CardHeader>
                      <CardTitle>3D Raga Note Sphere</CardTitle>
                      <CardDescription>Interactive 3D visualization of Raga notes in orbital space</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <RagaNoteSphere raga={selectedRaga} />
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="audio" className="space-y-4">
                <AudioPlayerComponent data={analysisData} raga={selectedRaga} />
                <Card className="card-elegant">
                  <CardHeader>
                    <CardTitle>3D Waveform Visualization</CardTitle>
                    <CardDescription>Animated 3D waveform that responds to audio playback</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <AnimatedWaveform3D isPlaying={false} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="xai" className="space-y-4">
                <ExplainableAIPanel data={analysisData} raga={selectedRaga} />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  );
}
