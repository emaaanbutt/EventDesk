import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, query } from "../lib/api";
import {
  Alert,
  Busy,
  Empty,
  formatDate,
  PageHeading,
  Pagination,
} from "../components/UI";

export function NotificationsPage() {
  const [filters, setFilters] = useState({
    type: "",
    is_read: "",
    page: 1,
    page_size: 10,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);
  useEffect(() => {
    let active = true;
    setError("");
    api(query("/notifications/me", filters))
      .then((data) => {
        if (active) setResult(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [filters, version]);
  useEffect(() => {
    const refresh = () => setVersion((value) => value + 1);
    window.addEventListener("eventdesk:notifications-changed", refresh);
    return () =>
      window.removeEventListener("eventdesk:notifications-changed", refresh);
  }, []);
  async function setRead(notification) {
    setError("");
    try {
      await api(`/notifications/${notification.id}/read-state`, {
        method: "PATCH",
        body: { is_read: !notification.is_read },
      });
      window.dispatchEvent(new Event("eventdesk:notifications-changed"));
    } catch (err) {
      setError(err.message);
    }
  }
  function change(key, value) {
    setFilters((old) => ({ ...old, [key]: value, page: 1 }));
  }
  return (
    <>
      <PageHeading
        eyebrow="IN THE LOOP"
        title="Notifications"
        description="Updates on your bookings, events, and reviews."
      />
      <div className="filters slim card">
        <select
          aria-label="Notification type"
          value={filters.type}
          onChange={(e) => change("type", e.target.value)}
        >
          <option value="">All types</option>
          <option value="booking">Bookings</option>
          <option value="event">Events</option>
          <option value="review">Reviews</option>
        </select>
        <select
          aria-label="Read status"
          value={filters.is_read}
          onChange={(e) => change("is_read", e.target.value)}
        >
          <option value="">All updates</option>
          <option value="false">Unread</option>
          <option value="true">Read</option>
        </select>
      </div>
      <Alert message={error} />
      {!result && !error ? (
        <Busy />
      ) : !result ? null : result.items.length ? (
        <>
          <div className="notification-list">
            {result.items.map((item) => (
              <article
                key={item.id}
                className={`card notification ${item.is_read ? "" : "unread"}`}
              >
                <span className="notification-dot" />
                <div>
                  <span className="eyebrow">
                    {item.type} · {formatDate(item.created_at)}
                  </span>
                  <h3>{item.title}</h3>
                  <p>{item.message}</p>
                  {item.type === "booking" && (
                    <Link to="/bookings" className="text-link">
                      View bookings →
                    </Link>
                  )}
                  {item.type === "review" && item.event_id && (
                    <Link to={`/events/${item.event_id}`} className="text-link">
                      View reviews →
                    </Link>
                  )}
                </div>
                <button
                  className="button subtle small"
                  onClick={() => setRead(item)}
                >
                  {item.is_read ? "Mark unread" : "Mark read"}
                </button>
              </article>
            ))}
          </div>
          <Pagination
            {...result}
            onPage={(page) => setFilters((old) => ({ ...old, page }))}
          />
        </>
      ) : (
        <Empty title="All caught up" detail="Your updates will appear here." />
      )}
    </>
  );
}
