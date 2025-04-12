import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  CircularProgress,
  Typography,
  Tabs,
  Tab,
  Alert
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import LinkIcon from '@mui/icons-material/Link';

export default function FileUpload({ onUploadComplete }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tabValue, setTabValue] = useState(0);
  const [file, setFile] = useState(null);
  const [paperUrl, setPaperUrl] = useState("");
  
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type !== 'application/pdf') {
      setError("Only PDF files are accepted");
      setFile(null);
    } else {
      setError("");
      setFile(selectedFile);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError("");
  };
  
  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    
    try {
      let response;
      
      if (tabValue === 0) { // File upload
        if (!file) {
          throw new Error("Please select a PDF file");
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        response = await fetch('http://localhost:8000/upload-pdf', {
          method: 'POST',
          body: formData,
        });
      } else { // Paper URL/ID
        if (!paperUrl.trim()) {
          throw new Error("Please enter a paper URL or ID");
        }
        
        response = await fetch(`http://localhost:8000/summarize-direct`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ paper_id: paperUrl.trim() }),
        });
      }
      
      if (!response.ok) {
        throw new Error(`Failed to process: ${response.statusText}`);
      }
      
      const result = await response.text();
      onUploadComplete(result);
    } catch (error) {
      console.error("Error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box>
      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab icon={<UploadFileIcon />} label="Upload PDF" />
        <Tab icon={<LinkIcon />} label="Enter Paper URL/ID" />
      </Tabs>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {tabValue === 0 ? (
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            component="label"
            sx={{ mb: 1 }}
            fullWidth
          >
            {file ? file.name : "Choose PDF File"}
            <input
              type="file"
              hidden
              accept="application/pdf"
              onChange={handleFileChange}
            />
          </Button>
          {file && (
            <Typography variant="body2" color="textSecondary">
              Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
          )}
        </Box>
      ) : (
        <TextField
          fullWidth
          label="Enter paper URL or arXiv ID"
          value={paperUrl}
          onChange={(e) => setPaperUrl(e.target.value)}
          placeholder="https://arxiv.org/abs/2106.09685 or 2106.09685"
          sx={{ mb: 2 }}
        />
      )}
      
      <Button
        variant="contained"
        disabled={loading || (tabValue === 0 && !file) || (tabValue === 1 && !paperUrl.trim())}
        onClick={handleSubmit}
        startIcon={loading && <CircularProgress size={20} />}
      >
        {loading ? "Processing..." : "Summarize"}
      </Button>
    </Box>
  );
}
