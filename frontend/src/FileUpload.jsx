import React, { useState } from 'react';
import { TextField, Button, Tabs, Tab } from '@mui/material';

const FileUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [paperUrl, setPaperUrl] = useState('');
  const [tabValue, setTabValue] = useState(0);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handlePaperUrlChange = (event) => {
    setPaperUrl(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleUpload = async () => {
    let response;
    if (tabValue === 0) {
      const formData = new FormData();
      formData.append('file', file);
      response = await fetch('http://localhost:8001/upload-pdf', {
        method: 'POST',
        body: formData,
      });
    } else {
      response = await fetch('http://localhost:8001/summarize-direct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paper_id: paperUrl.trim() }),
      });
    }
    if (!response.ok) {
      throw new Error(`Failed to process: ${response.statusText}`);
    }
    const result = await response.json();
    onUploadComplete(result);
  };

  return (
    <div>
      <Tabs value={tabValue} onChange={handleTabChange}>
        <Tab label="Upload PDF" />
        <Tab label="Summarize by URL" />
      </Tabs>
      {tabValue === 0 ? (
        <div>
          <input type="file" onChange={handleFileChange} />
        </div>
      ) : (
        <div>
          <TextField
            label="Paper URL"
            value={paperUrl}
            onChange={handlePaperUrlChange}
          />
        </div>
      )}
      <Button onClick={handleUpload}>Upload</Button>
    </div>
  );
};

export default FileUpload;