import React, { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "../api";

interface Achievement {
  achievementID: number;
  title: string;
  description: string;
  requiredPoints: number;
  image_path: string;
}

interface AchievementModalProps {
  isOpen: boolean;
  onClose: () => void;
  username?: string;
}

const AchievementModal: React.FC<AchievementModalProps> = ({
  isOpen,
  onClose,
  username = "joe"
}) => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [userPoints, setUserPoints] = useState<number>(0);
  const [filter, setFilter] = useState<"all" | "completed" | "locked">("all");
  const [loading, setLoading] = useState(true);

  // Detect dark mode using window.matchMedia
  const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  // Define dynamic styles based on dark mode
  const modalContainerStyle = {
    backgroundColor: isDarkMode ? "#333" : "white",
    padding: "20px",
    borderRadius: "10px",
    width: "100%",
    maxWidth: "500px",
    maxHeight: "80vh",
    overflow: "auto",
    color: isDarkMode ? "#fff" : "#000"
  };

  const cardStyle = (completed: boolean) => ({
    border: "1px solid #ccc",
    borderRadius: "10px",
    padding: "12px",
    marginBottom: "10px",
    backgroundColor: completed ? (isDarkMode ? "#444" : "#f8f8f8") : (isDarkMode ? "#555" : "#f0f0f0"),
    display: "flex",
    alignItems: "center"
  });

  const buttonStyle = (active: boolean) => ({
    marginRight: "10px",
    padding: "5px 10px",
    background: active ? (isDarkMode ? "#555" : "#ddd") : (isDarkMode ? "#444" : "#f0f0f0"),
    border: "1px solid #ccc",
    borderRadius: "8px",
    cursor: "pointer"
  });

  useEffect(() => {
    if (isOpen) {
      const fetchData = async () => {
        await Promise.all([fetchAchievements(), fetchUserPoints()]);
        setLoading(false);
      };
      fetchData();
    }
  }, [isOpen, username]);

  const fetchAchievements = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/check_achievements`);
      setAchievements(response.data);
    } catch (error) {
      console.error("Error fetching achievements:", error);
    }
  };

  const fetchUserPoints = async () => {
    try {
      console.log("Fetching points for user:", username);
      const response = await axios.get(`${API_BASE_URL}/get_user_points/${username}`);
      setUserPoints(response.data.points);
    } catch (error) {
      console.error("Error fetching user points:", error);
    }
  };

  const computedAchievements = achievements.map(achievement => ({
    ...achievement,
    completed: userPoints >= achievement.requiredPoints
  }));

  const filteredAchievements = computedAchievements.filter(achievement => {
    if (filter === "all") return true;
    if (filter === "completed") return achievement.completed;
    if (filter === "locked") return !achievement.completed;
    return true;
  });

  if (!isOpen) return null;

  if (loading) {
    return (
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000
      }}>
        <div>Loading achievements...</div>
      </div>
    );
  }

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0,0,0,0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000
    }}>
      <div style={modalContainerStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
          <h2 style={{ margin: 0 }}>Achievements</h2>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              fontSize: "16px",
              color: isDarkMode ? "#fff" : "#000"
            }}
          >
            ✕
          </button>
        </div>

        <div style={{ marginBottom: "15px", fontWeight: "bold" }}>
          Your Points: {userPoints}
        </div>

        <div style={{ marginBottom: "15px" }}>
          <button
            onClick={() => setFilter("all")}
            style={buttonStyle(filter === "all")}
          >
            All
          </button>
          <button
            onClick={() => setFilter("completed")}
            style={buttonStyle(filter === "completed")}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter("locked")}
            style={buttonStyle(filter === "locked")}
          >
            Locked
          </button>
        </div>

        <div>
          {filteredAchievements.map(achievement => (
            <div
              key={achievement.achievementID}
              style={cardStyle(achievement.completed)}
            >
              {achievement.image_path && (
                <img
                  src={`/static/${achievement.image_path}`}
                  alt={achievement.title}
                  style={{
                    width: "50px",
                    height: "50px",
                    marginRight: "15px",
                    opacity: achievement.completed ? 1 : 0.3
                  }}
                />
              )}
              <div>
                <div style={{ fontWeight: "bold" }}>
                  {achievement.title}
                  {achievement.completed ? " (Completed)" : ` (Locked - requires ${achievement.requiredPoints} points)`}
                </div>
                <div style={{ marginTop: "5px" }}>
                  {achievement.description}
                  <br />
                  <small>Progress: {userPoints} / {achievement.requiredPoints}</small>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <div>
            {filteredAchievements.filter(a => a.completed).length} of {filteredAchievements.length} achievements completed
          </div>
        </div>
      </div>
    </div>
  );
};

export default AchievementModal;
