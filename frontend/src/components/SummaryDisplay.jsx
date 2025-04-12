// SummaryDisplay.jsx
import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Divider, 
  Chip,
  Stack,
  CircularProgress,
  Button,
  IconButton,
  Collapse
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { getSummary } from '../api';

export default function SummaryDisplay({ paper, onSelect }) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const handleFetchSummary = async () => {
    setLoading(true);
    try {
      const { data } = await getSummary(paper.id);
      setSummary(data.summary);
      onSelect();
    } catch (error) {
      console.error("Summary error:", error);
      setSummary("Error loading summary");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {paper.title}
          </Typography>
          <IconButton onClick={() => setExpanded(!expanded)}>
            <ExpandMoreIcon sx={{ transform: expanded ? 'rotate(180deg)' : 'none' }} />
          </IconButton>
        </Box>
        
        <Collapse in={expanded}>
          <Stack direction="row" spacing={1} sx={{ my: 2 }}>
            {paper.authors?.map((author) => (
              <Chip 
                key={author} 
                label={author} 
                size="small" 
                sx={{ bgcolor: 'primary.dark' }} 
              />
            ))}
          </Stack>
          
          <Divider sx={{ my: 2 }} />

          {summary ? (
            <Typography variant="body1" paragraph>
              {summary}
            </Typography>
          ) : (
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleFetchSummary}
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Summary'}
            </Button>
          )}
        </Collapse>
      </CardContent>
    </Card>
  );
}