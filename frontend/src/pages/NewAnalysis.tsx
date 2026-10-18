import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  File,
  AlertCircle,
  CheckCircle,
  Film,
  Mic,
  Image as ImageIcon,
  X,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import { uploadMedia } from '../services/api';

export const NewAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileType, setFileType] = useState<'image' | 'video' | 'audio' | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelection = (file: File) => {
    setError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();

    let detectedType: 'image' | 'video' | 'audio' | null = null;
    if (['jpg', 'jpeg', 'png', 'webp'].includes(ext || '')) {
      detectedType = 'image';
    } else if (['mp4', 'avi', 'mov', 'mkv', 'webm'].includes(ext || '')) {
      detectedType = 'video';
    } else if (['wav', 'mp3', 'flac', 'ogg', 'm4a'].includes(ext || '')) {
      detectedType = 'audio';
    } else {
      setError(`Unsupported extension '.${ext}'. Supported formats: JPG, PNG, WEBP, MP4, AVI, MOV, WAV, MP3, FLAC.`);
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds 50 MB limit.`);
      return;
    }

    setSelectedFile(file);
    setFileType(detectedType);

    // Create object URL for preview
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const res = await uploadMedia(selectedFile, (percent) => {
        setUploadProgress(percent);
      });

      // Redirect directly to the analysis details page
      navigate(`/analyses/${res.id}`);
    } catch (err: any) {
      setError(err.message || 'Media upload failed. Please try again.');
      setIsUploading(false);
    }
  };

  const clearSelection = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileType(null);
    setUploadProgress(0);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Initiate Deepfake Analysis
        </h1>
        <p className="mt-1 text-sm text-cyber-muted">
          Upload suspicious media for multi-stage visual facial analysis, frame aggregation, and acoustic speech forensics.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold block mb-0.5">Validation Error</span>
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Drag & Drop Zone */}
      {!selectedFile ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-cyber-accent bg-cyber-accent/5 scale-[1.01]'
              : 'border-cyber-border hover:border-cyber-blue/60 bg-cyber-card/40 hover:bg-cyber-card/70'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*,video/*,audio/*,.mp4,.avi,.mov,.mkv,.wav,.mp3,.flac,.webp"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
              }
            }}
          />

          <div className="max-w-md mx-auto space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-cyber-card border border-cyber-border flex items-center justify-center text-cyber-accent">
              <UploadCloud className="w-8 h-8" />
            </div>

            <div>
              <p className="text-base font-semibold text-white">
                Drag and drop your media file here, or{' '}
                <span className="text-cyber-accent underline underline-offset-4">browse</span>
              </p>
              <p className="text-xs text-cyber-muted mt-1">
                Supports Images, Videos, and Audio up to 50 MB
              </p>
            </div>

            <div className="pt-4 grid grid-cols-3 gap-3 text-[11px] text-cyber-muted border-t border-cyber-border/60">
              <div className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-cyber-surface/50 border border-cyber-border/40">
                <ImageIcon className="w-3.5 h-3.5 text-sky-400" />
                <span>JPG, PNG, WEBP</span>
              </div>
              <div className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-cyber-surface/50 border border-cyber-border/40">
                <Film className="w-3.5 h-3.5 text-purple-400" />
                <span>MP4, AVI, MOV</span>
              </div>
              <div className="flex items-center justify-center space-x-1.5 p-2 rounded-lg bg-cyber-surface/50 border border-cyber-border/40">
                <Mic className="w-3.5 h-3.5 text-emerald-400" />
                <span>WAV, MP3, FLAC</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* File Selected & Preview Mode */
        <div className="bg-cyber-card border border-cyber-border rounded-2xl p-6 space-y-6">
          <div className="flex items-start justify-between border-b border-cyber-border pb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-cyber-surface border border-cyber-border">
                {fileType === 'image' && <ImageIcon className="w-6 h-6 text-sky-400" />}
                {fileType === 'video' && <Film className="w-6 h-6 text-purple-400" />}
                {fileType === 'audio' && <Mic className="w-6 h-6 text-emerald-400" />}
              </div>
              <div>
                <h3 className="font-semibold text-white text-base truncate max-w-sm sm:max-w-md">
                  {selectedFile.name}
                </h3>
                <p className="text-xs text-cyber-muted font-mono">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB &bull; {selectedFile.type || 'Custom Media'}
                </p>
              </div>
            </div>

            {!isUploading && (
              <button
                onClick={clearSelection}
                className="p-1.5 rounded-lg text-cyber-muted hover:text-white hover:bg-cyber-surface"
                title="Remove file"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Interactive Media Preview */}
          <div className="rounded-xl overflow-hidden bg-cyber-surface/70 border border-cyber-border flex items-center justify-center p-4 min-h-[220px]">
            {fileType === 'image' && previewUrl && (
              <img
                src={previewUrl}
                alt="Upload preview"
                className="max-h-72 max-w-full rounded-lg object-contain shadow-md"
              />
            )}

            {fileType === 'video' && previewUrl && (
              <video
                src={previewUrl}
                controls
                className="max-h-72 max-w-full rounded-lg shadow-md"
              />
            )}

            {fileType === 'audio' && previewUrl && (
              <div className="w-full max-w-md p-6 text-center space-y-4">
                <Mic className="w-12 h-12 mx-auto text-emerald-400 animate-pulse" />
                <audio src={previewUrl} controls className="w-full" />
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-cyber-muted">Transferring to secure pipeline...</span>
                <span className="text-cyber-accent font-bold">{uploadProgress}%</span>
              </div>
              <div className="w-full h-2 bg-cyber-surface rounded-full overflow-hidden border border-cyber-border">
                <div
                  className="h-full bg-cyber-accent transition-all duration-200"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              onClick={clearSelection}
              disabled={isUploading}
              className="px-4 py-2.5 rounded-xl border border-cyber-border text-slate-300 text-sm hover:text-white hover:bg-cyber-surface transition-all disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-cyber-accent text-cyber-bg font-bold text-sm hover:bg-cyber-accent/90 transition-all shadow-lg shadow-cyber-accent/20 disabled:opacity-50"
            >
              <span>{isUploading ? 'Dispatching...' : 'Start Forensic Scan'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Security and Responsible AI Guidance */}
      <div className="bg-cyber-surface/40 border border-cyber-border/70 rounded-xl p-5 space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-cyber-accent" />
          <span>Security & Data Handling Protocols</span>
        </h4>
        <ul className="text-xs text-cyber-muted space-y-1.5 list-disc list-inside">
          <li>Uploaded media is stored with randomized UUID filenames and isolated from executable paths.</li>
          <li>SHA-256 cryptographic hashes are calculated for non-repudiation and chain of custody.</li>
          <li>Files are automatically purged according to retention limits (default 7 days).</li>
          <li>Predictions are probabilistic indicators and do not replace certified forensic testimony.</li>
        </ul>
      </div>
    </div>
  );
};
