// src/components/ResourcesUpload.jsx
import { useState, useCallback, useRef } from 'react';
import { apiFetch } from '../utils/api';

export default function ResourcesUpload({
  resources,
  onFileAdded,
  onUrlAdded,
  onResourceRemoved,
  isDisabled = false
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [uploadingFiles, setUploadingFiles] = useState(new Set());
  const [urlError, setUrlError] = useState('');
  const fileInputRef = useRef(null);

  const isValidUrl = (string) => {
    try {
      const url = new URL(string);
      return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const uploadFile = async (file) => {
    const tempId = `uploading_${Date.now()}_${file.name}`;
    setUploadingFiles(prev => new Set(prev).add(tempId));

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Используем apiFetch, который автоматически добавит credentials: 'include'
      const data = await apiFetch('/upload/file', {
        method: 'POST',
        body: formData,
      });

      onFileAdded(data.file_path, file.name);
    } catch (err) {
      console.error('Upload error:', err);
      setUrlError(err.message);
    } finally {
      setUploadingFiles(prev => {
        const next = new Set(prev);
        next.delete(tempId);
        return next;
      });
    }
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => uploadFile(file));
  }, []);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => uploadFile(file));
    e.target.value = '';
  };

  const handleAddUrl = async () => {
    const url = urlInput.trim();
    if (!url) {
      setUrlError('Введите URL');
      return;
    }
    if (!isValidUrl(url)) {
      setUrlError('Неверный формат URL');
      return;
    }

    setUrlError('');
    try {
      // Бэкенд сам вернет URL как идентификатор ресурса
      await apiFetch('/upload/from-url', {
        method: 'POST',
        body: JSON.stringify({ url }),
      });
      onUrlAdded(url);
      setUrlInput('');
    } catch (err) {
      console.error('URL upload error:', err);
      setUrlError(err.message);
    }
  };

  const handleUrlKeyDown = (e) => {
    if (e.key === 'Enter' && !isDisabled) {
      handleAddUrl();
    }
  };

  const handleRemoveResource = (id) => {
    onResourceRemoved(id);
  };

  return (
    <div
      className={`
        relative border-2 border-dashed rounded-lg p-4 
        transition-all duration-200 bg-white
        ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'}
        ${isDisabled ? 'opacity-60 pointer-events-none' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isDisabled}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50
                   disabled:cursor-not-allowed rounded-lg font-medium text-gray-700
                   transition-all border border-gray-300 flex items-center gap-2 whitespace-nowrap"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Загрузить файл
        </button>

        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".txt,.md,.csv,.json,.yaml,.yml,.html,.xml,.docx,.xlsx,.pptx,.pdf,.jpg,.jpeg,.png,.gif,.tiff,.bmp,.py,.js,.ts,.java,.kt,.scala,.cs,.cpp,.go,.php,.swift,.r,.pl,.sql,.sh,.zsh,.bash"
          onChange={handleFileSelect}
          disabled={isDisabled}
          multiple
        />

        <div className="flex-1 flex gap-2">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => {
              setUrlInput(e.target.value);
              if (urlError) setUrlError('');
            }}
            onKeyDown={handleUrlKeyDown}
            placeholder="URL ресурса"
            disabled={isDisabled}
            className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg
                     focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                     transition placeholder-gray-400 text-gray-900 text-sm"
          />
          <button
            type="button"
            onClick={handleAddUrl}
            disabled={isDisabled || !urlInput.trim()}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50
                     disabled:cursor-not-allowed rounded-lg font-medium text-gray-700
                     transition-all border border-gray-300 whitespace-nowrap"
          >
            Добавить
          </button>
        </div>
      </div>

      {urlError && (
        <div className="text-xs text-red-600 mb-2 flex items-center gap-1">
          <span>⚠️</span> {urlError}
        </div>
      )}

      <div className="border-t border-gray-200 pt-3">
        <div className="text-xs font-medium text-gray-500 mb-2">
          Выбранные ресурсы ({resources.length + uploadingFiles.size})
        </div>

        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
          {Array.from(uploadingFiles).map(id => (
            <div key={id} className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg text-sm">
              <span className="w-4 h-4 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"/>
              <span className="text-gray-500 truncate flex-1">Загрузка...</span>
            </div>
          ))}

          {resources.map(resource => (
            <div key={resource.id} className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg text-sm group">
              <button
                type="button"
                onClick={() => handleRemoveResource(resource.id)}
                disabled={isDisabled}
                className="w-5 h-5 flex items-center justify-center text-red-500
                         hover:text-red-700 hover:bg-red-50 rounded transition
                         disabled:opacity-40 disabled:cursor-not-allowed"
                title="Удалить из списка"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <span className="text-gray-700 truncate flex-1" title={resource.name}>
                {resource.name}
              </span>
              <span className="text-xs text-gray-400" title={resource.type === 'file' ? 'Файл' : 'URL'}>
                {resource.type === 'file' ? '📄' : '🌐'}
              </span>
            </div>
          ))}

          {resources.length === 0 && uploadingFiles.size === 0 && (
            <div className="text-xs text-gray-400 text-center py-4">
              Список пуст. Загрузите файл или добавьте URL
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 text-xs text-gray-400 text-center">
        или перетащите файлы в эту область
      </div>
    </div>
  );
}