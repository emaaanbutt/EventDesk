import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { api, query } from "../lib/api";
import {
  Alert,
  Busy,
  ConfirmButton,
  Empty,
  formatDate,
  formatMoney,
  PageHeading,
  Pagination,
  Status,
} from "../components/UI";

export function BookingsPage() {
  const { user } = useAuth();
  const [all, setAll] = useState(false);
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [version, setVersion] = useState(0);
  useEffect(() => {
    let active = true;
    setResult(null);
    setError("");
    api(query(all ? "/bookings" : "/bookings/me", { page, page_size: 10 }))
      .then((data) => {
        if (active) setResult(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [page, all, version]);
  async function cancel(id) {
    setError("");
    setNotice("");
    try {
      await api(`/bookings/${id}/cancel`, { method: "POST" });
      setNotice("Booking cancelled. The tickets are available again.");
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    }
  }
  async function remove(id) {
    setError("");
    setNotice("");
    try {
      await api(`/bookings/${id}`, { method: "DELETE" });
      setNotice("Booking removed from your list.");
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="YOUR PLANS"
        title="Bookings"
        description="All your event plans in one place."
        actions={
          user?.role === "admin" && (
            <select
              aria-label="Booking view"
              value={all ? "all" : "mine"}
              onChange={(e) => {
                setAll(e.target.value === "all");
                setPage(1);
              }}
            >
              <option value="mine">My bookings</option>
              <option value="all">All bookings</option>
            </select>
          )
        }
      />
      <Alert message={error} />
      <Alert message={notice} kind="success" />
      {!result && !error ? (
        <Busy />
      ) : !result ? null : result.items.length ? (
        <>
          <div className="card table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Event</th>
                  {all && <th>Attendee</th>}
                  <th>Tickets</th>
                  <th>Total</th>
                  <th>Booked</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {result.items.map((booking) => (
                  <tr key={booking.id}>
                    <td>
                      {!booking.event_deleted ? (
                        <Link
                          to={`/events/${booking.event_id}`}
                          className="text-link"
                        >
                          {booking.event_title}
                        </Link>
                      ) : (
                        <span>{booking.event_title || "Deleted event"}</span>
                      )}
                    </td>
                    {all && (
                      <td>{booking.attendee_name || "Deleted user"}</td>
                    )}
                    <td>{booking.quantity}</td>
                    <td>{formatMoney(booking.total_amount)}</td>
                    <td>{formatDate(booking.booked_at)}</td>
                    <td className="row-actions">
                      <Status value={booking.status} />
                    </td>
                    <td>
                      {booking.status === "confirmed" && (
                        <ConfirmButton
                          className="button subtle small"
                          message="Cancel this booking and return its tickets?"
                          onConfirm={() => cancel(booking.id)}
                        >
                          Cancel
                        </ConfirmButton>
                      )}
                      <ConfirmButton
                        className="button subtle small danger-text"
                        message={
                          booking.status === "confirmed"
                            ? "Delete this booking? Its tickets will be released."
                            : "Remove this booking from your list?"
                        }
                        onConfirm={() => remove(booking.id)}
                      >
                        Delete
                      </ConfirmButton>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination {...result} onPage={setPage} />
        </>
      ) : (
        <Empty
          title={all ? "No bookings found" : "No bookings yet"}
          detail={all ? "Bookings will appear here once someone reserves a ticket." : "Find an event you like and book your spot."}
          action={!all &&
            <Link to="/events" className="button primary">
              Explore events
            </Link>
          }
        />
      )}
    </>
  );
}
