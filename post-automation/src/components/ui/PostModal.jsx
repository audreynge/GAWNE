import { useState, useEffect } from 'react';
import { supabase } from '../pages/Home';

const PostModal = ({ onClose }) => {
  const [songTitle, setSongTitle] = useState('');
  const [showGenerate, setShowGenerate] = useState(false);

  useEffect(() => {
    if (songTitle) {
      setShowGenerate(true);
    } else {
      setShowGenerate(false);
    }
  }, [songTitle]);

  const handleGenerateCaption = () => {
    
  };

  const handleSubmit = async () => {
    if (!songTitle) {
      alert("Song title is required.");
      return;
    }

    const { error } = await supabase
      .from('songs')
      .insert([
        {
          song_title: songTitle,
        },
      ]);

    if (error) {
      console.error('Error inserting song title into songs table:', error.message);
      alert('Failed to create post');
    } else {
      console.log(`Song successfully added: ${songTitle}`);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/70 z-50 text-black">
      <div className="bg-white rounded p-6 w-96 relative">
        {/* Cancel Button */}
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white hover:text-gray-500"
        >
          Cancel
        </button>
        <h3 className="text-xl font-semibold mb-4">Create Post</h3>

        {/* Song Name Input */}
        <div className="mb-4">
          <label className="block mb-1">Song Name:</label>
          <input
            type="text"
            value={songTitle}
            onChange={(e) => setSongTitle(e.target.value)}
            className="border p-2 rounded w-full"
            placeholder="Enter song name"
          />
        </div>

        {/* Generate Caption */}
        {showGenerate && (
          <button
            onClick={handleGenerateCaption}
            className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
          >
            Generate Caption
          </button>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          className="mt-4 bg-green-500 text-white px-4 py-2 rounded"
        >
          Submit
        </button>
      </div>
    </div>
  );
};

export default PostModal;
