import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Divider, 
  Chip,
  Stack 
} from '@mui/material';

export default function SummaryDisplay({ paper }) {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          {paper.title}
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          {paper.authors.map((author) => (
            <Chip key={author} label={author} size="small" />
          ))}
        </Stack>
        <Divider sx={{ my: 2 }} />
        <Typography variant="body1" paragraph>
          {paper.summary}
        </Typography>
      </CardContent>
    </Card>
  );
}