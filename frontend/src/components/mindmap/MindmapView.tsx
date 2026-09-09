import { useState, useEffect, useRef, useCallback } from "react";
import mermaid from "mermaid";
import { Loader2, ZoomIn, ZoomOut, Maximize2, Minimize2, RotateCcw, Download, Code2 } from "lucide-react";

export const MindmapView = () => {
  const [topic, setTopic] = useState("Document Summary");
  const [mindmapCode, setMindmapCode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [renderError, setRenderError] = useState<string | null>(null);

  const mermaidContainerRef = useRef<HTMLDivElement>(null);
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const fullscreenRef = useRef<HTMLDivElement>(null);

  // Initialize mermaid with theme-aware config
  useEffect(() => {
    const root = document.documentElement;
    const theme = root.getAttribute("data-theme");
    const isLight = theme === "light-frost";

    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      flowchart: {
        curve: "basis",
        padding: 20,
        nodeSpacing: 40,
        rankSpacing: 60,
        htmlLabels: true,
      },
      themeVariables: {
        primaryColor: isLight ? "#e8f0fe" : "#2d2a5e",
        primaryBorderColor: isLight ? "#3d5af1" : "#a7a9be",
        primaryTextColor: isLight ? "#1a1a1a" : "#fffffe",
        lineColor: isLight ? "#5c5c5c" : "#7c7aae",
        secondaryColor: isLight ? "#f3e8ff" : "#1a1932",
        tertiaryColor: isLight ? "#fef3c7" : "#232145",
        edgeLabelBackground: isLight ? "#ffffff" : "#0f0e17",
        fontSize: "14px",
        fontFamily: "'Space Grotesk', 'Manrope', system-ui, sans-serif",
        clusterBkg: isLight ? "#f8f8f8" : "#1a1932",
        clusterBorder: isLight ? "#cccccc" : "#444",
      },
    });
  }, []);

  // Render mermaid diagram
  useEffect(() => {
    if (mindmapCode && mermaidContainerRef.current) {
      setRenderError(null);
      const renderDiagram = async () => {
        try {
          // Clean up previous render
          mermaidContainerRef.current!.innerHTML = "";
          const id = `mermaid-${Date.now()}`;
          const { svg } = await mermaid.render(id, mindmapCode);
          if (mermaidContainerRef.current) {
            mermaidContainerRef.current.innerHTML = svg;

            // Style the SVG to fill container
            const svgEl = mermaidContainerRef.current.querySelector("svg");
            if (svgEl) {
              svgEl.style.width = "100%";
              svgEl.style.height = "auto";
              svgEl.style.minHeight = "400px";
              svgEl.style.maxHeight = "none";
            }
          }
        } catch (err: any) {
          console.error("Mermaid render error:", err);
          setRenderError(err?.message || "Failed to render mind map");
        }
      };
      renderDiagram();
    }
  }, [mindmapCode]);

  const generateMindmap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || isLoading) return;

    setIsLoading(true);
    setMindmapCode(null);
    setRenderError(null);
    setZoom(1);
    setPan({ x: 0, y: 0 });

    try {
      const res = await fetch("/api/mindmap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, document_id: null }),
      });
      const data = await res.json();
      setMindmapCode(data.code);
    } catch (err) {
      console.error(err);
      alert("Error generating mindmap");
    } finally {
      setIsLoading(false);
    }
  };

  // Zoom controls
  const handleZoomIn = useCallback(() => setZoom((z) => Math.min(z + 0.2, 3)), []);
  const handleZoomOut = useCallback(() => setZoom((z) => Math.max(z - 0.2, 0.3)), []);
  const handleResetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  // Pan handlers
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button === 0) {
        setIsPanning(true);
        setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      }
    },
    [pan]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isPanning) {
        setPan({ x: e.clientX - panStart.x, y: e.clientY - panStart.y });
      }
    },
    [isPanning, panStart]
  );

  const handleMouseUp = useCallback(() => setIsPanning(false), []);

  // Scroll to zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom((z) => Math.min(Math.max(z + delta, 0.3), 3));
  }, []);

  // Fullscreen toggle
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((f) => !f);
    if (!isFullscreen) {
      setZoom(0.9);
      setPan({ x: 0, y: 0 });
    }
  }, [isFullscreen]);

  // Download SVG
  const downloadSVG = useCallback(() => {
    if (!mermaidContainerRef.current) return;
    const svgEl = mermaidContainerRef.current.querySelector("svg");
    if (!svgEl) return;

    const svgData = new XMLSerializer().serializeToString(svgEl);
    const blob = new Blob([svgData], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mindmap-${topic.replace(/\s+/g, "-").toLowerCase()}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  }, [topic]);

  // Keyboard shortcuts for fullscreen
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isFullscreen]);

  const mindmapDisplay = mindmapCode && !isLoading && (
    <div
      ref={fullscreenRef}
      style={
        isFullscreen
          ? {
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 9999,
              background: "var(--bg)",
              display: "flex",
              flexDirection: "column",
              padding: "1rem",
            }
          : {}
      }
    >
      {/* Toolbar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <h3 style={{ margin: 0 }}>🗺️ {topic}</h3>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            className="btn"
            onClick={handleZoomOut}
            title="Zoom Out"
            style={{ padding: "0.5rem" }}
          >
            <ZoomOut size={16} />
          </button>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              padding: "0 0.5rem",
              color: "var(--muted)",
              fontSize: "0.85rem",
              fontWeight: 700,
            }}
          >
            {Math.round(zoom * 100)}%
          </span>
          <button
            className="btn"
            onClick={handleZoomIn}
            title="Zoom In"
            style={{ padding: "0.5rem" }}
          >
            <ZoomIn size={16} />
          </button>
          <button
            className="btn"
            onClick={handleResetView}
            title="Reset View"
            style={{ padding: "0.5rem" }}
          >
            <RotateCcw size={16} />
          </button>
          <button
            className="btn"
            onClick={toggleFullscreen}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            style={{ padding: "0.5rem" }}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
          <button
            className="btn"
            onClick={downloadSVG}
            title="Download SVG"
            style={{ padding: "0.5rem" }}
          >
            <Download size={16} />
          </button>
          <button
            className="btn"
            onClick={() => setShowCode(!showCode)}
            title={showCode ? "Hide Code" : "Show Code"}
            style={{ padding: "0.5rem" }}
          >
            <Code2 size={16} />
          </button>
        </div>
      </div>

      {/* Mind Map Canvas */}
      <div
        ref={svgContainerRef}
        className="card"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{
          flex: isFullscreen ? 1 : undefined,
          overflow: "hidden",
          cursor: isPanning ? "grabbing" : "grab",
          position: "relative",
          minHeight: isFullscreen ? undefined : "500px",
          padding: "2rem",
          userSelect: "none",
        }}
      >
        <div
          ref={mermaidContainerRef}
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: "center center",
            transition: isPanning ? "none" : "transform 0.2s ease",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        />
      </div>

      {/* Render Error */}
      {renderError && (
        <div
          className="card"
          style={{
            marginTop: "1rem",
            background: "var(--danger)",
            color: "#fff",
            padding: "1rem",
          }}
        >
          <strong>Render Error:</strong> {renderError}
        </div>
      )}

      {/* Source Code */}
      {showCode && (
        <pre
          style={{
            marginTop: "1rem",
            padding: "1rem",
            background: "var(--input-bg)",
            borderRadius: "var(--radius)",
            border: "var(--border)",
            overflowX: "auto",
            fontSize: "0.85rem",
            lineHeight: 1.6,
            maxHeight: "300px",
            overflowY: "auto",
          }}
        >
          <code>{mindmapCode}</code>
        </pre>
      )}

      {/* Help text */}
      <p
        style={{
          marginTop: "0.75rem",
          color: "var(--muted)",
          fontSize: "0.8rem",
          textAlign: "center",
        }}
      >
        💡 Click and drag to pan · Scroll to zoom · Press Esc to exit fullscreen
      </p>
    </div>
  );

  return (
    <div style={{ maxWidth: isFullscreen ? "100%" : "960px", margin: "0 auto" }}>
      {!isFullscreen && (
        <>
          <div className="hero">
            <div className="eyebrow">Visualize</div>
            <h1>
              Mind <span className="grad-text">Maps</span>
            </h1>
            <p>
              Generate interactive concept maps from your study material or
              custom topics. Pan, zoom, and explore.
            </p>
          </div>

          <div className="card mb-8">
            <form
              onSubmit={generateMindmap}
              style={{ display: "flex", gap: "1rem", alignItems: "flex-end" }}
            >
              <div style={{ flex: 1 }}>
                <label
                  htmlFor="mindmapTopic"
                  style={{
                    display: "block",
                    marginBottom: "0.5rem",
                    color: "var(--muted)",
                  }}
                >
                  Topic or Concept
                </label>
                <input
                  id="mindmapTopic"
                  name="mindmapTopic"
                  type="text"
                  className="input"
                  placeholder="e.g. Machine Learning, Data Structures, Neural Networks"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  "🧠 Generate Mind Map"
                )}
              </button>
            </form>
          </div>
        </>
      )}

      {isLoading && (
        <div
          className="card"
          style={{ textAlign: "center", padding: "3rem" }}
        >
          <Loader2
            className="animate-spin"
            size={32}
            style={{ margin: "0 auto 1rem", color: "var(--primary)" }}
          />
          <p style={{ fontWeight: 600 }}>
            Generating your mind map...
          </p>
          <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
            The AI is building a structured concept map for &ldquo;{topic}&rdquo;
          </p>
        </div>
      )}

      {mindmapDisplay}
    </div>
  );
};
