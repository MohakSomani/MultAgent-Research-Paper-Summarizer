import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  IconButton,
  Slider 
} from '@mui/material';
import { PlayArrow, Pause } from '@mui/icons-material';

export default function AudioPlayer({ audioUrl }) {
  const [playing, setPlaying] = React.useState(false);
  const audioRef = React.useRef(null);

  const togglePlay = () => {
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Audio Summary
        </Typography>
        <Box display="flex" alignItems="center">
          <IconButton onClick={togglePlay}>
            {playing ? <Pause /> : <PlayArrow />}
          </IconButton>
          <Slider
            sx={{ ml: 2, flexGrow: 1 }}
            defaultValue={0}
            aria-label="Audio timeline"
          />
        </Box>
        <audio
          ref={audioRef}
          src={audioUrl}
          onEnded={() => setPlaying(false)}
          hidden
        />
      </CardContent>
    </Card>
  );
}