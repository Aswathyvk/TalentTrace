import React, { useState } from 'react';
import axios from 'axios';
import { RadialBarChart, RadialBar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import './App.css';

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!resume || !jobDescription) {
      setError('Please upload a resume and enter a job description.');
      return;
    }
    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', resume);
    formData.append('job_description', jobDescription);

    try {
      const response = await axios.post('http://127.0.0.1:8000/match', formData);
      setResult(response.data);
    } catch (err) {
      setError('Something went wrong. Make sure the backend is running.');
    }
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#22c55e';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  const chartData = result ? [
    { name: 'Skill Score', score: result.skill_score },
    { name: 'Semantic Score', score: result.semantic_score },
    { name: 'ATS Score', score: result.ats_score },
  ] : [];

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🎯 TalentTrace</h1>
        <p>AI-Powered Resume Screener & Job Match Analyzer</p>
      </header>

      {/* Upload Section */}
      <div className="container">
        <div className="card">
          <h2>📄 Upload Resume</h2>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setResume(e.target.files[0])}
            className="file-input"
          />
          {resume && <p className="file-name">✅ {resume.name}</p>}
        </div>

        <div className="card">
          <h2>📋 Job Description</h2>
          <textarea
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="textarea"
            rows={8}
          />
        </div>

        {error && <p className="error">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="submit-btn"
        >
          {loading ? '⏳ Analyzing...' : '🔍 Analyze Resume'}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="results">
          {/* Match Score */}
          <div className="score-card">
            <h2>Overall Match Score</h2>
            <div
              className="score-circle"
              style={{ borderColor: getScoreColor(result.match_score) }}
            >
              <span style={{ color: getScoreColor(result.match_score) }}>
                {result.match_score}%
              </span>
            </div>
            <p className="experience-badge">{result.experience_level}</p>
          </div>

          {/* Score Breakdown Chart */}
          <div className="card">
            <h2>📊 Score Breakdown</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Skills */}
          <div className="skills-grid">
            <div className="card">
              <h2>✅ Matched Skills ({result.matched_skills.length})</h2>
              <div className="tags">
                {result.matched_skills.map((skill, i) => (
                  <span key={i} className="tag matched">{skill}</span>
                ))}
              </div>
            </div>

            <div className="card">
              <h2>❌ Missing Skills ({result.missing_skills.length})</h2>
              <div className="tags">
                {result.missing_skills.map((skill, i) => (
                  <span key={i} className="tag missing">{skill}</span>
                ))}
              </div>
            </div>
          </div>

          {/* ATS Score */}
          <div className="card">
            <h2>🤖 ATS Score: {result.ats_score}%</h2>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${result.ats_score}%`,
                  backgroundColor: getScoreColor(result.ats_score)
                }}
              />
            </div>
          </div>

          {/* Suggestions */}
          <div className="card">
            <h2>💡 Suggestions</h2>
            <ul className="suggestions">
              {result.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;