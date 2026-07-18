"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Users, Heart, Plus, Loader2 } from "lucide-react";
import { socialApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

interface Challenge { id: string; title: string; description: string; participants: number; days_left: number; reward_points: number; your_status: string; }
interface Post { _id: string; username: string; content: string; post_type: string; likes: number; created_at: string; }
type Tab = "challenges" | "feed";

export default function SocialPage() {
  const [tab, setTab] = useState<Tab>("challenges");
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [newPostContent, setNewPostContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [cRes, fRes] = await Promise.allSettled([socialApi.getChallenges(), socialApi.getFeed()]);
        if (cRes.status === "fulfilled") { const d = cRes.value.data; setChallenges(Array.isArray(d) ? d as Challenge[] : (d as { challenges?: Challenge[] }).challenges || []); }
        if (fRes.status === "fulfilled") { const d = fRes.value.data; setPosts(Array.isArray(d) ? d as Post[] : (d as { posts?: Post[] }).posts || []); }
      } catch { toast.error("Failed to load community"); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  const handleCreatePost = async () => { if (!newPostContent.trim()) return; setPosting(true); try { await socialApi.createPost({ content: newPostContent.trim() }); toast.success("Post shared!"); setNewPostContent(""); const res = await socialApi.getFeed(); const d = res.data; setPosts(Array.isArray(d) ? d as Post[] : (d as { posts?: Post[] }).posts || []); } catch { toast.error("Failed to post"); } finally { setPosting(false); } };
  const handleLikePost = async (postId: string) => { try { await socialApi.likePost(postId); setPosts((prev) => prev.map((p) => p._id === postId ? { ...p, likes: p.likes + 1 } : p)); } catch { toast.error("Failed to like"); } };
  const getTimeAgo = (dateStr: string) => { const diffMs = Date.now() - new Date(dateStr).getTime(); const mins = Math.floor(diffMs / 60000); if (mins < 60) return `${mins}m ago`; const hrs = Math.floor(mins / 60); if (hrs < 24) return `${hrs}h ago`; return `${Math.floor(hrs / 24)}d ago`; };

  if (loading) return <AppShell><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" /></div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><Users className="w-7 h-7 text-brand-500" /> Community</h1>
          <p className="text-gray-500 text-sm mt-1">Join challenges and connect with health enthusiasts</p>
        </div>

        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
          {([{ key: "challenges", label: "Challenges" }, { key: "feed", label: "Feed" }] as { key: Tab; label: string }[]).map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.key ? "bg-white text-brand-600 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>{t.label}</button>
          ))}
        </div>

        {tab === "challenges" && (
          <div className="space-y-4">
            {challenges.length === 0 ? (
              <div className="glass-card p-8 text-center"><Users className="w-12 h-12 text-gray-200 mx-auto mb-4" /><p className="text-gray-500">No challenges available right now</p></div>
            ) : (
              challenges.map((challenge) => (
                <div key={challenge.id} className="glass-card p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div><h3 className="text-gray-800 font-bold">{challenge.title}</h3><p className="text-sm text-gray-500 mt-1">{challenge.description}</p></div>
                    {challenge.your_status === "joined" ? <span className="text-xs bg-brand-50 text-brand-600 px-3 py-1 rounded-full font-medium">Joined</span> : <button className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-4 py-2 rounded-xl text-xs transition-all flex items-center gap-1"><Plus className="w-3 h-3" /> Join</button>}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {challenge.participants} participants</span>
                    <span>⏱ {challenge.days_left} days left</span>
                    <span className="text-yellow-500 font-medium">🏆 {challenge.reward_points} pts</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {tab === "feed" && (
          <div className="space-y-4">
            <div className="glass-card p-4">
              <textarea value={newPostContent} onChange={(e) => setNewPostContent(e.target.value)} placeholder="Share your progress or health tip..." className="w-full bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300 px-4 py-3 text-sm resize-none h-24" />
              <div className="flex justify-end mt-3">
                <button onClick={handleCreatePost} disabled={posting || !newPostContent.trim()} className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-5 py-2 rounded-xl text-sm transition-all disabled:opacity-50 flex items-center gap-2">
                  {posting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />} Post
                </button>
              </div>
            </div>
            {posts.length === 0 ? <div className="glass-card p-8 text-center"><p className="text-gray-500">No posts yet. Be the first to share!</p></div> : (
              posts.map((post) => (
                <div key={post._id} className="glass-card p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-full bg-brand-50 flex items-center justify-center flex-shrink-0"><span className="text-sm font-bold text-brand-600">{post.username.charAt(0).toUpperCase()}</span></div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-800">{post.username}</span>
                        <span className="text-xs text-gray-400">{getTimeAgo(post.created_at)}</span>
                        {post.post_type && post.post_type !== "general" && <span className="text-xs bg-brand-50 text-brand-600 px-2 py-0.5 rounded-full">{post.post_type}</span>}
                      </div>
                      <p className="text-sm text-gray-600">{post.content}</p>
                      <button onClick={() => handleLikePost(post._id)} className="flex items-center gap-1 mt-3 text-xs text-gray-400 hover:text-red-500 transition-colors"><Heart className="w-4 h-4" /><span>{post.likes}</span></button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
