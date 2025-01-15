import { api } from '$lib/api';

export type VoiceCommandCallback = (command: {
  transcription: string;
  type: string;
  parameters: any;
  response: string;
}) => void;

export class WorkoutVoiceService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private isListening = false;
  private commandCallback: VoiceCommandCallback | null = null;

  constructor() {
    this.setupAudioContext();
  }

  private async setupAudioContext() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000
        } 
      });
      
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        await this.processRecording();
      };
    } catch (error) {
      console.error('Failed to initialize audio:', error);
      throw new Error('Microphone access required for voice commands');
    }
  }

  setCommandCallback(callback: VoiceCommandCallback) {
    this.commandCallback = callback;
  }

  async startListening(): Promise<void> {
    if (!this.mediaRecorder) {
      throw new Error('Voice recording not initialized');
    }

    this.isListening = true;
    this.audioChunks = [];
    this.mediaRecorder.start(100); // Collect data every 100ms
  }

  async stopListening(): Promise<void> {
    if (!this.mediaRecorder || !this.isListening) {
      return;
    }

    this.isListening = false;
    this.mediaRecorder.stop();
  }

  private async processRecording(): Promise<void> {
    if (this.audioChunks.length === 0) return;

    try {
      // Create a blob from all chunks
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      
      // Create FormData and append the blob
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');

      const response = await api.post('/workouts/voice/command', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Handle the response
      const { transcription, command_type, command_parameters, response_text, response_audio } = response.data;

      // Play audio response if available
      if (response_audio) {
        const audioContext = new AudioContext();
        const audioBuffer = await this.base64ToAudioBuffer(response_audio, audioContext);
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.start();
      }

      // Call the callback if set
      if (this.commandCallback) {
        this.commandCallback({
          transcription,
          type: command_type,
          parameters: command_parameters,
          response: response_text
        });
      }
    } catch (error) {
      console.error('Failed to process voice command:', error);
      throw error;
    }
  }

  private async base64ToAudioBuffer(base64: string, context: AudioContext): Promise<AudioBuffer> {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return context.decodeAudioData(bytes.buffer);
  }

  isRecording(): boolean {
    return this.isListening;
  }
}
