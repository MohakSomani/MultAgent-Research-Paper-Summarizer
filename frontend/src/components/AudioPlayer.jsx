// AudioPlayer.jsx
import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  IconButton,
  Slider,
  CircularProgress,
  Box
} from '@mui/material';
import { PlayArrow, Pause } from '@mui/icons-material';
import { getAudio } from '../api';

export default function AudioPlayer({ paperId }) {
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const audioRef = React.useRef(null);

  useEffect(() => {
    const fetchAudio = async () => {
      setLoading(true);
      try {
        const { data } = await getAudio(paperId);
        setAudioUrl(data.audio_url);
      } catch (error) {
        console.error("Audio error:", error);
      } finally {
        setLoading(false);
      }
    };
    
    if (paperId) fetchAudio();
  }, [paperId]);

  const togglePlay = () => {
    if (!audioUrl) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Audio Summary
        </Typography>
        <Box display="flex" alignItems="center">
          <IconButton 
            onClick={togglePlay} 
            color="secondary"
            disabled={!audioUrl || loading}
          >
            {loading ? (
              <CircularProgress size={24} />
            ) : playing ? (
              <Pause fontSize="large" />
            ) : (
              <PlayArrow fontSize="large" />
            )}
          </IconButton>
          
          {audioUrl && (
            <Slider
              sx={{ ml: 2, flexGrow: 1 }}
              defaultValue={0}
              aria-label="Audio timeline"
              color="secondary"
            />
          )}
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