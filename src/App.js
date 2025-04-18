import { useState } from 'react';

function App() {
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    const res = await fetch("http://localhost:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    setVideoUrl(data.video_url);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto" }}>
      <h1>🎓 Professor Avatar</h1>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type something your professor might say..."
        style={{ width: "100%", height: "100px", padding: "10px" }}
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate Speech"}
      </button>
      {videoUrl && (
        <video src={videoUrl} controls autoPlay style={{ marginTop: "20px", width: "100%" }} />
      )}
    </div>
  );
}

export default App;
