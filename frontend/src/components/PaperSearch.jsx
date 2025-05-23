// PaperSearch.jsx
import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  CircularProgress,
  Paper,
  Typography 
} from '@mui/material';
import { searchPapers } from '../api';

export default function PaperSearch({ onResults }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const result = await searchPapers(query); // Plain string result
      console.log("Search Results:", result); // Log the result
      onResults(result); // Pass the result to the parent component
    } catch (error) {
      console.error("Error fetching search results:", error);
      onResults(""); // Handle errors gracefully
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Research Paper Search
      </Typography>
      <Box display="flex" gap={2}>
        <TextField
          fullWidth
          label="Search terms (e.g. 'neural networks')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          disabled={!query || loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? "Searching..." : "Search"}
        </Button>
      </Box>
    </Paper>
  );
}