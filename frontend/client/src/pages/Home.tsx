import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Music, BookOpen, Zap, BarChart3, Lightbulb, Library } from "lucide-react";
import { useLocation } from "wouter";
import { getLoginUrl } from "@/const";
import DivineSpaceHero from "@/components/3d/DivineSpaceHero";

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();

  const features = [
    {
      icon: BookOpen,
      title: "Sanskrit Text Analysis",
      description: "Input Sanskrit verses in Devanagari, IAST, or Harvard-Kyoto transliteration schemes"
    },
    {
      icon: Zap,
      title: "Metrical Identification",
      description: "Automatically identify Chanda (metrical patterns) with syllable counting and gana sequences"
    },
    {
      icon: Music,
      title: "Vedic Accents",
      description: "Visualize udātta, anudātta, and svarita accent patterns on each syllable"
    },
    {
      icon: BarChart3,
      title: "Pitch Contours",
      description: "View F0 frequency graphs mapped to syllables with Raga-based melodic rules"
    },
    {
      icon: Lightbulb,
      title: "Explainable AI",
      description: "Understand melodic choices and Raga rule applications with natural language explanations"
    },
    {
      icon: Library,
      title: "Verse Library",
      description: "Save and manage your analyzed verses with complete metadata and analysis history"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-sm">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Music className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold">Svara Chanda</h1>
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-muted-foreground">Welcome, {user?.name}</span>
                <Button onClick={() => setLocation("/analysis")} className="gap-2">
                  Open Analysis <ArrowRight className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <Button asChild>
                <a href={getLoginUrl()}>Sign In</a>
              </Button>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative container py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <DivineSpaceHero />
        </div>
        <div className="mx-auto max-w-3xl text-center relative z-10">
          <h2 className="mb-6 text-5xl font-bold leading-tight text-foreground">
            Analyze Sanskrit Chants with <span style={{ color: 'oklch(0.65 0.22 40)' }}>Precision & Elegance</span>
          </h2>
          <p className="mb-8 text-xl text-muted-foreground backdrop-blur-sm bg-background/50 rounded-lg p-4">
            Svara Chanda combines ancient Sanskrit prosody with modern AI to analyze metrical patterns, identify Vedic accents, and synthesize melodic chants following classical Raga rules.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center backdrop-blur-sm bg-background/30 rounded-lg p-4 inline-block mx-auto">
            {isAuthenticated ? (
              <Button size="lg" onClick={() => setLocation("/analysis")} className="gap-2">
                Start Analyzing <ArrowRight className="h-5 w-5" />
              </Button>
            ) : (
              <>
                <Button size="lg" asChild>
                  <a href={getLoginUrl()}>Get Started</a>
                </Button>
                <Button size="lg" variant="outline">
                  Learn More
                </Button>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container py-16 md:py-24">
        <div className="mb-12 text-center">
          <h3 className="text-3xl font-bold">Powerful Features</h3>
          <p className="mt-2 text-muted-foreground">Everything you need to master Sanskrit prosody and melodic synthesis</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <Card key={idx} className="card-elegant">
                <CardHeader>
                  <Icon className="mb-2 h-8 w-8 text-primary" />
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-border bg-card py-16 md:py-24">
        <div className="container text-center">
          <h3 className="mb-6 text-3xl font-bold">Ready to Explore Sanskrit Prosody?</h3>
          <p className="mb-8 text-lg text-muted-foreground">
            Join scholars and enthusiasts in analyzing the mathematical beauty of Sanskrit verse.
          </p>
          {isAuthenticated ? (
            <Button size="lg" onClick={() => setLocation("/analysis")} className="gap-2">
              Open Analysis Tool <ArrowRight className="h-5 w-5" />
            </Button>
          ) : (
            <Button size="lg" asChild>
              <a href={getLoginUrl()}>Sign In to Begin</a>
            </Button>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background py-8">
        <div className="container text-center text-sm text-muted-foreground">
          <p>Svara Chanda © 2026 • Sanskrit Metrical & Melodic Synthesis Platform</p>
        </div>
      </footer>
    </div>
  );
}
