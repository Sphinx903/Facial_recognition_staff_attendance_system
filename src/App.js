import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const videoRef = useRef(null);
  const [recognized, setRecognized] = useState([]);

  useEffect(() => {
    startVideo();
  }, []);

  const startVideo = () => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      })
      .catch(err => {
        console.error("Error accessing webcam: ", err);
      });
  };

  const captureImage = () => {
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/jpeg');
    return dataURL.split(',')[1]; // Get base64 data
  };

  const sendFrame = async () => {
    const image = captureImage();
    try {
      const response = await axios.post('http://localhost:5000/recognize', { image });
      setRecognized(response.data.recognized);
    } catch (error) {
      console.error("Error recognizing face: ", error);
    }
  };

  return (
    <div>
      <h1>Face Recognition Attendance</h1>
      <video ref={videoRef} style={{ width: '100%' }} />
      <button onClick={sendFrame}>Capture & Recognize</button>
      <div>
        {recognized.length > 0 ? (
          <div>
            <h2>Recognized:</h2>
            <ul>
              {recognized.map((name, index) => <li key={index}>{name}</li>)}
            </ul>
          </div>
        ) : (
          <h2>No one recognized</h2>
        )}
      </div>
    </div>
  );
};

export default App;
