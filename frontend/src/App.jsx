// App.jsx
import React, { useState, useEffect } from 'react';
import { 
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Typography,
  Box,
  Select,
  MenuItem,
  Button,
  Paper,
  Divider,
  CircularProgress
} from '@mui/material';
import { grey, deepOrange, teal } from "@mui/material/colors";
import PaperSearch from './components/PaperSearch';
import SummaryDisplay from './components/SummaryDisplay';
import AudioPlayer from './components/AudioPlayer';
import FileUpload from './components/FileUpload';
import { getSummary } from './api';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: teal,
    secondary: deepOrange,
    background: {
      default: grey[900],
      paper: grey[800],
    },
    text: {
      primary: '#fff',
      secondary: grey[400],
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: grey[800],
          marginBottom: '1rem',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& label': { color: grey[400] },
          '& .MuiOutlinedInput-root': {
            '& fieldset': { borderColor: grey[600] },
          },
        },
      },
    },
  },
});

export default function App() {
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [summary, setSummary] = useState("");
  const [paperSummary, setPaperSummary] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [paperSummaryId, setPaperSummaryId] = useState("");
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);

  // Log the updated results for debugging
  useEffect(() => {
    console.log("Updated Results:", results);
  }, [results]);

  // Improve the results parsing to ensure links are properly captured
  const handleResults = (data) => {
    console.log("Raw Results:", data); // Log raw data to debug
    if (typeof data === "string") {
      const lines = data.split("\n").filter(line => line.trim());
      console.log("Split lines:", lines);
      
      // Parse each line directly without joining multi-lines
      const formattedResults = lines.map((line, index) => {
        console.log(`Processing line ${index}:`, line);
        // Match the index and the rest
        const idMatch = line.match(/^(\d+):/);
        if (!idMatch) return null;
        
        const id = parseInt(idMatch[1], 10);
        // Extract the content after the index
        const content = line.substring(line.indexOf(':') + 1).trim();
        
        // Look for the last occurrence of " - http" which should be the link separator
        const lastHyphenWithUrl = content.lastIndexOf(' - http');
        
        if (lastHyphenWithUrl !== -1) {
          const title = content.substring(0, lastHyphenWithUrl).trim();
          const link = content.substring(lastHyphenWithUrl + 3).trim(); // +3 to remove " - "
          
          console.log(`Parsed ID: ${id}, Title: ${title}, Link: ${link}`);
          
          return {
            id: id,
            title: title,
            link: link,
            fullText: line
          };
        }
        
        // Fallback if no link format found
        return {
          id: id,
          title: content,
          link: "",
          fullText: line
        };
      }).filter(Boolean); // Remove any null results
      
      console.log("Formatted results:", formattedResults);
      setResults(formattedResults);
    } else {
      console.error("Unexpected results format:", data);
      setResults([]);
    }
  };

  const handleSummarize = async () => {
    if (results[selectedIndex]) {
      try {
        // Use consistent port 8000
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/summarize/${selectedIndex}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch summary: ${response.statusText}`);
        }
        const summaryResult = await response.text();
        console.log("Raw Summary Result:", summaryResult);
        const parsedSummary = summaryResult
          .split("\n")
          .filter((line) => line.trim().startsWith("[SUMMARY]") || line.trim() !== "")
          .map((line) => line.replace("[SUMMARY]", "").trim())
          .join("\n");
        setSummary(parsedSummary);
      } catch (error) {
        console.error("Error fetching summary:", error);
        setSummary("Failed to fetch summary.");
      }
    }
  };

  const handleGeneratePodcast = async () => {
    try {
      if (isGeneratingAudio) return; // Prevent multiple simultaneous requests
      
      setAudioUrl(null); // Reset audio URL
      setIsGeneratingAudio(true);
      
      console.log(`Generating podcast for paper index: ${selectedIndex}`);
      
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const audioEndpoint = `${baseUrl}/audio/${selectedIndex}`;
      
      console.log("Requesting audio from:", audioEndpoint);
      
      const response = await fetch(audioEndpoint, {
        method: 'POST', // Change to POST to prevent browser caching/auto-requesting
        headers: { 'Cache-Control': 'no-cache' }
      });
      
      if (response.ok) {
        // Generate a unique timestamp to prevent browser caching
        const timestamp = new Date().getTime();
        setAudioUrl(`${audioEndpoint}?t=${timestamp}`);
        console.log("Audio generated successfully");
      } else {
        // Reset progress on error
        let errorMessage = "Failed to generate audio";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || response.statusText;
        } catch (e) {
          // If not JSON, try text
          try {
            errorMessage = await response.text();
          } catch (e2) {
            errorMessage = response.statusText;
          }
        }
        
        console.error(`Failed to generate audio: ${response.status} ${errorMessage}`);
        alert(`Failed to generate audio: ${errorMessage}`);
      }
    } catch (error) {
      console.error("Error generating podcast:", error);
      alert(`Error connecting to server: ${error.message}`);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleUploadComplete = (data) => {
    // Parse the response format which now includes ID:summary
    const colonIndex = data.indexOf(':');
    if (colonIndex !== -1) {
      const id = data.substring(0, colonIndex);
      const summary = data.substring(colonIndex + 1);
      setPaperSummary(summary);
      setPaperSummaryId(id);
      console.log(`Received summary with ID: ${id}`);
    } else {
      // Fallback to old behavior if response format hasn't changed
      setPaperSummary(data);
      // Create and store a unique ID for this summary
      const uniqueId = `direct-${Date.now()}`;
      setPaperSummaryId(uniqueId);
      
      // Store this in the backend cache too via a fetch call
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      fetch(`${baseUrl}/store-summary/${uniqueId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ summary: data })
      }).catch(err => console.error("Failed to store summary ID:", err));
    }
  };

  const handleGeneratePodcastForUpload = async () => {
    try {
      if (isGeneratingAudio) return; // Prevent multiple simultaneous requests
      
      setAudioUrl(null);
      setIsGeneratingAudio(true);
      
      // Ensure we have a valid ID
      if (!paperSummaryId) {
        console.error("No valid summary ID found");
        alert("Error: Could not find a valid summary. Please try summarizing again.");
        return;
      }
      
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const audioEndpoint = `${baseUrl}/audio/${paperSummaryId}`;
      
      console.log(`Generating podcast for summary ID: ${paperSummaryId}`);
      console.log("Requesting audio from:", audioEndpoint);
      
      const response = await fetch(audioEndpoint, {
        method: 'POST', // Change to POST to prevent browser caching/auto-requesting
        headers: { 'Cache-Control': 'no-cache' }
      });
      
      if (response.ok) {
        // Generate a unique timestamp to prevent browser caching
        const timestamp = new Date().getTime();
        setAudioUrl(`${audioEndpoint}?t=${timestamp}`);
        console.log("Audio generated successfully");
      } else {
        // Handle error response
        let errorText;
        try {
          const errorData = await response.json();
          errorText = errorData.detail || response.statusText;
        } catch (e) {
          errorText = await response.text() || response.statusText;
        }
        
        console.error("Failed to generate audio:", response.status, errorText);
        alert(`Failed to generate audio: ${errorText}`);
        
        // Remove the loading message
        setPaperSummary(prev => prev.replace("\n\nGenerating audio... Please wait.", ""));
      }
    } catch (error) {
      console.error("Error generating podcast:", error);
      alert(`Error connecting to server: ${error.message}`);
      
      // Remove the loading message
      setPaperSummary(prev => prev.replace("\n\nGenerating audio... Please wait.", ""));
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4, backgroundColor: grey[800] }}>
          <PaperSearch onResults={handleResults} />
        </Paper>

        {/* Display parsed results with better link formatting */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6">Search Results:</Typography>
          <Paper elevation={3} sx={{ p: 2, mt: 2, backgroundColor: "#f5f5f5", color: "#000" }}>
            {results.length > 0 ? (
              results.map((paper) => (
                <Box key={paper.id} sx={{ mb: 2, p: 1, borderBottom: '1px solid #ddd' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {paper.id}: {paper.title}
                  </Typography>
                  {paper.link && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Link: <a 
                        href={paper.link.startsWith('http') ? paper.link : `http://${paper.link}`}
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#0066cc', textDecoration: 'underline', overflowWrap: 'break-word' }}
                      >
                        {paper.link}
                      </a>
                    </Typography>
                  )}
                </Box>
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                No results to display.
              </Typography>
            )}
          </Paper>
        </Box>

        {/* Dropdown to select index */}
        {results.length > 0 && (
          <Box sx={{ mt: 4, display: "flex", alignItems: "center", gap: 2 }}>
            <Typography>Select Paper Index:</Typography>
            <Select
              value={selectedIndex}
              onChange={(e) => setSelectedIndex(e.target.value)}
              sx={{ minWidth: 100 }}
            >
              {results.map((_, index) => (
                <MenuItem key={index} value={index}>
                  {index}
                </MenuItem>
              ))}
            </Select>
            <Button variant="contained" onClick={handleSummarize}>
              Summarize
            </Button>
          </Box>
        )}

        {/* Display summary */}
        {summary && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6">Summary:</Typography>
            <Paper elevation={3} sx={{ p: 2, mt: 2, backgroundColor: "#f5f5f5", color: "#000" }}>
              <Typography variant="body2">{summary}</Typography>
            </Paper>
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                onClick={handleGeneratePodcast}
                disabled={isGeneratingAudio}
              >
                {isGeneratingAudio ? "Generating..." : "Generate Podcast"}
              </Button>
              
              {/* Remove progress bar and use simple loading indicator instead */}
              {isGeneratingAudio && (
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ mr: 2 }}>Generating audio...</Typography>
                </Box>
              )}
              
              {audioUrl && (
                <Box sx={{ mt: 2 }}>
                  <audio 
                    controls 
                    src={audioUrl}
                    key={audioUrl} // Force re-render when URL changes
                  />
                </Box>
              )}
            </Box>
          </Box>
        )}

        {/* Divider between search and direct upload */}
        <Box sx={{ mt: 6, mb: 6 }}>
          <Divider>
            <Typography variant="body1" sx={{ px: 2 }}>OR</Typography>
          </Divider>
        </Box>

        {/* Direct paper upload/input section */}
        <Paper elevation={3} sx={{ p: 3, mb: 4, backgroundColor: grey[800] }}>
          <Typography variant="h6" gutterBottom>
            Upload PDF or Enter Paper
          </Typography>
          <FileUpload onUploadComplete={handleUploadComplete} />
        </Paper>

        {/* Display direct paper summary */}
        {paperSummary && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6">Paper Summary:</Typography>
            <Paper elevation={3} sx={{ p: 2, mt: 2, backgroundColor: "#f5f5f5", color: "#000" }}>
              <Typography variant="body2">{paperSummary}</Typography>
            </Paper>
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                onClick={handleGeneratePodcastForUpload}
                disabled={isGeneratingAudio}
              >
                {isGeneratingAudio ? "Generating..." : "Generate Podcast"}
              </Button>
              
              {/* Remove progress bar and use simple loading indicator instead */}
              {isGeneratingAudio && (
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ mr: 2 }}>Generating audio...</Typography>
                </Box>
              )}
              
              {audioUrl && (
                <Box sx={{ mt: 2 }}>
                  <audio 
                    controls 
                    src={audioUrl}
                    key={audioUrl} // Force re-render when URL changes
                  />
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Container>
    </ThemeProvider>
  );
}