import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Trash2, Clock, Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface HistoryLibraryProps {
  onLoad: (data: any) => void;
}

export default function HistoryLibrary({ onLoad }: HistoryLibraryProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedHistory, setExpandedHistory] = useState(false);

  // Mock history data
  const mockHistory = [
    {
      id: 1,
      text: "नमस्ते सूर्य",
      chanda: "Anushtubh",
      raga: "Yaman",
      date: new Date(Date.now() - 2 * 60 * 60 * 1000),
      data: { originalText: "नमस्ते सूर्य", canonical_slp1: "namaste surya" }
    },
    {
      id: 2,
      text: "ॐ भूर्भुवः स्वः",
      chanda: "Trishtubh",
      raga: "Bhairav",
      date: new Date(Date.now() - 24 * 60 * 60 * 1000),
      data: { originalText: "ॐ भूर्भुवः स्वः", canonical_slp1: "om bhur bhuvah svah" }
    },
    {
      id: 3,
      text: "यज्ञो वै श्रेष्ठः",
      chanda: "Jagati",
      raga: "Kharaharapriya",
      date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
      data: { originalText: "यज्ञो वै श्रेष्ठः", canonical_slp1: "yajno vai shreshthah" }
    }
  ];

  const filteredHistory = mockHistory.filter(item =>
    item.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.chanda.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <Card className="card-elegant">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Verse Library
        </CardTitle>
        <CardDescription>Your saved analyses</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search verses..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* History List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredHistory.length === 0 ? (
            <p className="text-center text-sm text-muted-foreground py-4">
              {searchQuery ? "No verses found" : "No saved verses yet"}
            </p>
          ) : (
            filteredHistory.map((item) => (
              <div
                key={item.id}
                className="history-item group"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium devanagari-text truncate">
                    {item.text}
                  </p>
                  <div className="flex gap-2 mt-1 flex-wrap">
                    <Badge variant="secondary" className="text-xs">
                      {item.chanda}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {item.raga}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(item.date)}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onLoad(item.data)}
                  >
                    Load
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8 text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Stats */}
        {filteredHistory.length > 0 && (
          <div className="pt-4 border-t border-border text-xs text-muted-foreground">
            <p>Showing {filteredHistory.length} of {mockHistory.length} verses</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
