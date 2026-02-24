import { useEffect, useState } from "react";
import { getNotifications, markAsRead } from "../services/notificationService";

interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
}

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    const data = await getNotifications();
    setNotifications(data);
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div style={{ position: "relative" }}>
      <button onClick={() => setOpen(!open)}>
        🔔 {unreadCount > 0 && `(${unreadCount})`}
      </button>

      {open && (
        <div style={{
          position: "absolute",
          right: 0,
          background: "white",
          border: "1px solid #ccc",
          width: "300px",
          maxHeight: "400px",
          overflowY: "auto",
          zIndex: 1000
        }}>
          {notifications.map(n => (
            <div
              key={n.id}
              style={{ padding: "10px", cursor: "pointer", borderBottom: "1px solid #eee" }}
              onClick={async () => {
                await markAsRead(n.id);
                fetchNotifications();
              }}
            >
              <strong>{n.title}</strong>
              <p style={{ margin: 0 }}>{n.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
