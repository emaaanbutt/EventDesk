import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { api, getTokens, openSocket, query } from "../lib/api";

export function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    if (!user) {
      setUnread(0);
      setLatest(null);
      return;
    }
    let stopped = false;
    let socket;
    let retry;
    let hideToast;
    async function loadUnread() {
      try {
        const data = await api(
          query("/notifications/me", { is_read: false, page_size: 1 }),
        );
        if (!stopped) setUnread(data.total);
      } catch {
        // The notifications page shows API errors when opened.
      }
    }
    function connect() {
      if (stopped || !getTokens()) return;
      socket = openSocket("/ws/notifications");
      socket.onopen = () =>
        socket.send(
          JSON.stringify({ type: "auth", token: getTokens()?.access_token }),
        );
      socket.onmessage = (message) => {
        const event = JSON.parse(message.data);
        if (event.type !== "notification.created") return;
        setLatest(event.data);
        clearTimeout(hideToast);
        hideToast = setTimeout(() => setLatest(null), 6000);
        window.dispatchEvent(new Event("eventdesk:notifications-changed"));
      };
      socket.onclose = () => {
        if (!stopped)
          retry = setTimeout(async () => {
            try {
              await api("/auth/me");
              connect();
            } catch {
              /* auth state will update */
            }
          }, 5000);
      };
    }
    loadUnread();
    connect();
    window.addEventListener("eventdesk:notifications-changed", loadUnread);
    return () => {
      stopped = true;
      clearTimeout(retry);
      clearTimeout(hideToast);
      socket?.close();
      window.removeEventListener("eventdesk:notifications-changed", loadUnread);
    };
  }, [user?.id]);
  async function logout() {
    try {
      await signOut();
    } catch {
      /* local session is cleared even if API is unavailable */
    }
    navigate("/");
  }
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-inner">
          <NavLink to="/" className="brand">
            <span className="brand-mark">e.</span>
            <span>EventDesk</span>
          </NavLink>
          <nav className="main-nav" aria-label="Main navigation">
            <NavLink to="/events" end>
              Explore
            </NavLink>
            {user && <NavLink to="/bookings">Bookings</NavLink>}
            {user && (
              <NavLink to="/notifications">
                Notifications{" "}
                {unread > 0 && <span className="unread-count">{unread}</span>}
              </NavLink>
            )}
            {user && ["organizer", "admin"].includes(user.role) && (
              <NavLink to="/my-events">My events</NavLink>
            )}
            {user?.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
          </nav>
          <div className="account-nav">
            {user ? (
              <>
                <NavLink to="/profile" className="account-link">
                  {user.name}
                </NavLink>
                <button className="button subtle" onClick={logout}>
                  Sign out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="account-link">
                  Sign in
                </NavLink>
                <NavLink to="/register" className="button primary small">
                  Join EventDesk
                </NavLink>
              </>
            )}
          </div>
        </div>
      </header>
      {latest && (
        <div className="live-toast" role="status">
          <span className="eyebrow">NEW UPDATE</span>
          <strong>{latest.title}</strong>
          <span>{latest.message}</span>
          <Link to="/notifications" onClick={() => setLatest(null)}>
            View notifications →
          </Link>
        </div>
      )}
      <main className="main-content">
        <Outlet />
      </main>
      <footer className="site-footer">
        <span>EventDesk</span>
        <span>Good events are better together.</span>
      </footer>
    </div>
  );
}
