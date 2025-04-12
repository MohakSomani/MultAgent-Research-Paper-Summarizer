import React, { useState } from 'react';
import { 
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme 
} from '@mui/material';
import PaperSearch from './components/PaperSearch';
import SummaryDisplay from './components/SummaryDisplay';
import AudioPlayer from './components/AudioPlayer';

const theme = createTheme();

export default function App() {
  const [results, setResults] = useState([]);
  const [selectedPaper, setSelectedPaper] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <PaperSearch onResults={setResults} />
        
        {results.map((paper) => (
          <div key={paper.id} onClick={() => setSelectedPaper(paper)}>
            <SummaryDisplay paper={paper} />
          </div>
        ))}

        {selectedPaper && (
          <AudioPlayer audioUrl={`/audio/${selectedPaper.id}.mp3`} />
        )}
      </Container>
    </ThemeProvider>
  );
}