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
  Divider
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

  // Log the updated results for debugging
  useEffect(() => {
    console.log("Updated Results:", results);
  }, [results]);

  const handleResults = (data) => {
    console.log("Raw Results:", data); // Log the raw data
    if (typeof data === "string") {
      const lines = data.split("\n");
      // Only keep lines like "0: Paper Title"
      const relevantLines = lines.filter((line) => {
        if (!line || typeof line !== "string") return false;
        return /^\d+:\s+/.test(line.trim());
      });
      const parsedResults = relevantLines.map((line) => {
        // Split once on ": "
        const [indexPart, titlePart = ""] = line.split(/:\s+/, 2);
        return {
          id: parseInt(indexPart, 10),
          title: titlePart.trim(),
        };
      });
      setResults(parsedResults);
    } else {
      console.error("Unexpected results format:", data);
      setResults([]);
    }
  };

  const handleSummarize = async () => {
    if (results[selectedIndex]) {
      try {
        const response = await fetch(`http://localhost:8000/summarize/${selectedIndex}`);
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

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4, backgroundColor: grey[800] }}>
          <PaperSearch onResults={handleResults} />
        </Paper>

        {/* Display raw parsed results */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6">Parsed Results:</Typography>
          <Paper elevation={3} sx={{ p: 2, mt: 2, backgroundColor: "#f5f5f5", color: "#000" }}>
            {results.length > 0 ? (
              results.map((paper) => (
                <Typography key={paper.id} variant="body2">
                  {paper.id}: {paper.title}
                </Typography>
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
          <FileUpload onUploadComplete={setPaperSummary} />
        </Paper>

        {/* Display direct paper summary */}
        {paperSummary && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6">Paper Summary:</Typography>
            <Paper elevation={3} sx={{ p: 2, mt: 2, backgroundColor: "#f5f5f5", color: "#000" }}>
              <Typography variant="body2">{paperSummary}</Typography>
            </Paper>
          </Box>
        )}
      </Container>
    </ThemeProvider>
  );
}