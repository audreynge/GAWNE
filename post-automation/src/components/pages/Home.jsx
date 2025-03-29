import { useState, useEffect } from 'react';
import { createClient } from "@supabase/supabase-js";
import PostModal from '../ui/PostModal';

const supabase = createClient(import.meta.env.VITE_SUPABASE_PROJECT_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);

const Home = () => {
  const [showModal, setShowModal] = useState(false);
  const [songs, setSongs] = useState([]);

  useEffect(() => {
    getSongs();
  }, []);

  async function getSongs() {
    const { data } = await supabase.from("songs").select();
    setSongs(data);
  }

  const handleUploadClick = () => {
    setShowModal(true);
  };

  return (
    <div className="p-4">
      <div className="m-4 text-3xl font-bold">GAWNE</div>
      <button
        onClick={handleUploadClick}
        className="m-4 bg-blue-500 text-white rounded p-2"
      >
        Upload Post
      </button>
      {showModal && <PostModal onClose={() => setShowModal(false)} />}
      <ul>
        {songs.map((song) => (
          <li key={song.song_title}>{song.song_title}</li>
        ))}
      </ul>
    </div>
  );
};

export default Home;
export { supabase };
