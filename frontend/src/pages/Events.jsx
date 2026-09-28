import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { api, openSocket, query } from "../lib/api";
import {
  Alert,
  Busy,
  ConfirmButton,
  Empty,
  EventCard,
  Field,
  formatDate,
  formatMoney,
  PageHeading,
  Pagination,
  Status,
} from "../components/UI";
import { Reviews } from "./Reviews";

export function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            EVENTDESK · YOUR NEXT PLAN STARTS HERE
          </span>
          <h1>
            Places to be.
            <br />
            <em>People to meet.</em>
          </h1>
          <p>
            Browse events worth showing up for, book your spot, and stay in the
            loop.
          </p>
          <Link className="button primary" to="/events">
            Explore events <span>↗</span>
          </Link>
        </div>
        <div className="hero-art">
          <div className="art-circle one" />
          <div className="art-circle two" />
          <div className="art-ticket">
            <span>ADMIT ONE</span>
            <strong>
              Good things
              <br />
              happen here.
            </strong>
            <span>EVENTDESK · 2026</span>
          </div>
        </div>
      </section>
      <div className="home-lower">
        <span>Discover something new</span>
        <span>Make a plan that’s worth keeping.</span>
        <Link to="/events">See all events →</Link>
      </div>
    </>
  );
}

export function EventsPage() {
  const [filters, setFilters] = useState({
    search: "",
    category_id: "",
    tag_id: "",
    date_from: "",
    date_to: "",
    sort: "date_asc",
    page: 1,
    page_size: 9,
  });
  const [catalog, setCatalog] = useState({ categories: [], tags: [] });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      api("/categories", { auth: false }),
      api("/tags", { auth: false }),
    ])
      .then(([categories, tags]) => setCatalog({ categories, tags }))
      .catch((err) => setError(err.message));
  }, []);
  useEffect(() => {
    let active = true;
    setError("");
    const params = {
      ...filters,
      date_from: filters.date_from
        ? new Date(`${filters.date_from}T00:00:00`).toISOString()
        : "",
      date_to: filters.date_to
        ? new Date(`${filters.date_to}T23:59:59`).toISOString()
        : "",
    };
    api(query("/events/", params), { auth: false })
      .then((data) => {
        if (active) setResult(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [filters]);
  const update = (key, value) =>
    setFilters((old) => ({ ...old, [key]: value, page: 1 }));
  return (
    <>
      <PageHeading
        eyebrow="DISCOVER"
        title="Explore events"
        description="A little something for every kind of day."
      />
      <div className="filters card">
        <input
          aria-label="Search events"
          placeholder="Search by title or venue…"
          value={filters.search}
          onChange={(e) => update("search", e.target.value)}
        />
        <select
          aria-label="Category"
          value={filters.category_id}
          onChange={(e) => update("category_id", e.target.value)}
        >
          <option value="">All categories</option>
          {catalog.categories.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
        <select
          aria-label="Tag"
          value={filters.tag_id}
          onChange={(e) => update("tag_id", e.target.value)}
        >
          <option value="">All tags</option>
          {catalog.tags.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
        <select
          aria-label="Sort events"
          value={filters.sort}
          onChange={(e) => update("sort", e.target.value)}
        >
          <option value="date_asc">Soonest first</option>
          <option value="date_desc">Latest first</option>
          <option value="price_asc">Lowest price</option>
          <option value="price_desc">Highest price</option>
        </select>
        <label className="date-filter">
          From{" "}
          <input
            type="date"
            value={filters.date_from}
            max={filters.date_to || undefined}
            onChange={(e) => update("date_from", e.target.value)}
          />
        </label>
        <label className="date-filter">
          To{" "}
          <input
            type="date"
            value={filters.date_to}
            min={filters.date_from || undefined}
            onChange={(e) => update("date_to", e.target.value)}
          />
        </label>
      </div>
      <Alert message={error} />
      {!result ? (
        <Busy />
      ) : result.items.length ? (
        <>
          <div className="result-note">
            {result.total} event{result.total === 1 ? "" : "s"} found
          </div>
          <div className="event-grid">
            {result.items.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
          <Pagination
            {...result}
            onPage={(page) => setFilters((old) => ({ ...old, page }))}
          />
        </>
      ) : (
        <Empty title="No events found" detail="Try another search or filter." />
      )}
    </>
  );
}

export function MyEventsPage() {
  const [events, setEvents] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api("/events/mine")
      .then(setEvents)
      .catch((err) => setError(err.message));
  }, []);
  return (
    <>
      <PageHeading
        eyebrow="ORGANIZE"
        title="My events"
        description="Drafts, upcoming events, and everything you’ve hosted."
        actions={
          <Link to="/my-events/new" className="button primary">
            + Create event
          </Link>
        }
      />
      <Alert message={error} />
      {!events && !error ? (
        <Busy />
      ) : events?.length ? (
        <div className="event-grid">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      ) : (
        <Empty
          title="No events yet"
          detail="Start with a draft, then publish when you’re ready."
          action={
            <Link to="/my-events/new" className="button primary">
              Create an event
            </Link>
          }
        />
      )}
    </>
  );
}

function toLocalInput(value) {
  if (!value) return "";
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}

export function EventFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    Promise.all([
      api("/categories", { auth: false }),
      api("/tags", { auth: false }),
      ...(isEdit ? [api(`/events/${id}/manage`)] : []),
    ])
      .then(([cats, allTags, current]) => {
        setCategories(cats);
        setTags(allTags);
        if (current) {
          setEvent(current);
          setSelectedTags(current.tags.map((tag) => tag.id));
        }
      })
      .catch((err) => setError(err.message));
  }, [id, isEdit]);
  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const form = new FormData(e.currentTarget);
    const body = {
      title: form.get("title"),
      description: form.get("description"),
      venue: form.get("venue"),
      starts_at: new Date(form.get("starts_at")).toISOString(),
      ends_at: new Date(form.get("ends_at")).toISOString(),
      ticket_price: form.get("ticket_price"),
      total_tickets: Number(form.get("total_tickets")),
      category_id: form.get("category_id") || null,
      tag_ids: selectedTags,
    };
    if (new Date(body.ends_at) <= new Date(body.starts_at)) {
      setError("End time must be after start time.");
      setBusy(false);
      return;
    }
    try {
      const saved = await api(isEdit ? `/events/${id}` : "/events/", {
        method: isEdit ? "PATCH" : "POST",
        body,
      });
      navigate(`/events/${saved.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="page-narrow">
      <PageHeading
        eyebrow="ORGANIZE"
        title={isEdit ? "Edit event" : "Create an event"}
        description="Start with the details. New events are saved as drafts."
      />
      <Alert message={error} />
      {isEdit && !event && !error ? (
        <Busy />
      ) : (
        <form
          className="card form-card"
          onSubmit={submit}
          key={event?.id || "new"}
        >
          <div className="form-grid">
            <Field label="Title">
              <input
                name="title"
                defaultValue={event?.title}
                required
                maxLength="255"
              />
            </Field>
            <Field label="Venue">
              <input
                name="venue"
                defaultValue={event?.venue}
                required
                maxLength="255"
              />
            </Field>
            <Field label="Starts at">
              <input
                type="datetime-local"
                name="starts_at"
                defaultValue={toLocalInput(event?.starts_at)}
                required
              />
            </Field>
            <Field label="Ends at">
              <input
                type="datetime-local"
                name="ends_at"
                defaultValue={toLocalInput(event?.ends_at)}
                required
              />
            </Field>
            <Field label="Ticket price (PKR)">
              <input
                type="number"
                name="ticket_price"
                defaultValue={event?.ticket_price || 0}
                min="0"
                step="0.01"
                required
              />
            </Field>
            <Field label="Total tickets">
              <input
                type="number"
                name="total_tickets"
                defaultValue={event?.total_tickets || 1}
                min="1"
                step="1"
                required
              />
            </Field>
            <Field label="Category">
              <select
                name="category_id"
                defaultValue={event?.category_id || ""}
              >
                <option value="">None</option>
                {categories.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <Field label="Description">
            <textarea
              name="description"
              defaultValue={event?.description}
              rows="5"
              required
            />
          </Field>
          <div className="field">
            <span>Tags</span>
            <div className="tag-picker">
              {tags.length ? (
                tags.map((tag) => (
                  <label key={tag.id}>
                    <input
                      type="checkbox"
                      checked={selectedTags.includes(tag.id)}
                      onChange={(e) =>
                        setSelectedTags((old) =>
                          e.target.checked
                            ? [...old, tag.id]
                            : old.filter((tagId) => tagId !== tag.id),
                        )
                      }
                    />
                    {tag.name}
                  </label>
                ))
              ) : (
                <small>No tags yet.</small>
              )}
            </div>
          </div>
          <div className="form-actions">
            <button className="button primary" disabled={busy}>
              {busy ? "Saving…" : isEdit ? "Save changes" : "Create draft"}
            </button>
            <Link
              to={isEdit ? `/events/${id}` : "/my-events"}
              className="button secondary"
            >
              Cancel
            </Link>
          </div>
        </form>
      )}
    </div>
  );
}

export function EventDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [availability, setAvailability] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [notice, setNotice] = useState("");
  useEffect(() => {
    let active = true;
    setError("");
    api(`/events/${id}`, { auth: false })
      .catch(async (err) => {
        if (!user || err.status !== 404) throw err;
        try {
          return await api(`/events/${id}/attended`);
        } catch (attendedError) {
          if (
            ["organizer", "admin"].includes(user.role) &&
            [403, 404].includes(attendedError.status)
          ) {
            return api(`/events/${id}/manage`);
          }
          throw attendedError;
        }
      })
      .then((data) => {
        if (active) setEvent(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [id, user?.id]);
  useEffect(() => {
    if (!event || !["published", "completed", "cancelled"].includes(event.status)) return;
    let active = true;
    if (event.status === "published") {
      api(`/events/${id}/availability`, { auth: false })
        .then((data) => {
          if (active) setAvailability(data);
        })
        .catch(() => {});
    }
    const socket = openSocket(`/ws/events/${id}`);
    socket.onmessage = (message) => {
      const update = JSON.parse(message.data);
      if (active && update.type === "event.availability")
        setAvailability(update.data);
      if (active && update.type === "event.unavailable")
        setNotice("This event is no longer available.");
      if (active && update.type === "review.reply.created")
        window.dispatchEvent(
          new CustomEvent("eventdesk:review-reply", {
            detail: update.data.review_id,
          }),
        );
    };
    return () => {
      active = false;
      socket.close();
    };
  }, [id, event?.status]);
  async function act(path, message) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await api(`/events/${id}/${path}`, { method: "POST" });
      setEvent(updated);
      setNotice(message);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  async function deleteEvent() {
    setBusy(true);
    setError("");
    try {
      await api(`/events/${id}`, { method: "DELETE" });
      navigate(user?.role === "admin" ? "/admin" : "/my-events");
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }
  async function book(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/bookings", {
        method: "POST",
        body: { event_id: id, quantity: Number(quantity) },
      });
      setNotice("Booking confirmed. You can find it under My bookings.");
      const next = await api(`/events/${id}/availability`, { auth: false });
      setAvailability(next);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  if (!event)
    return (
      <>
        <Alert message={error} />
        {!error && <Busy />}
      </>
    );
  const canManage =
    user && (user.id === event.organizer_id || user.role === "admin");
  const isOwnEvent = user?.id === event.organizer_id;
  const canBook =
    event.status === "published" &&
    user &&
    !isOwnEvent &&
    new Date(event.starts_at) > new Date();
  return (
    <div className="detail-page">
      <Link to="/events" className="back-link">
        ← All events
      </Link>
      <div className="detail-top">
        <div>
          <span className="eyebrow">
            {event.category?.name || "EVENT"} ·{" "}
            {event.tags.map((tag) => tag.name).join(" / ")}
          </span>
          <h1>{event.title}</h1>
          <div className="detail-sub">
            <Status value={event.status} />
            <span>
              Hosted by{" "}
              {user?.id === event.organizer_id ? "you" : "an organizer"}
            </span>
          </div>
        </div>
        {canManage && (
          <div className="heading-actions">
            {["draft", "published"].includes(event.status) && (
              <Link className="button secondary" to={`/my-events/${id}/edit`}>
                Edit event
              </Link>
            )}
            {event.status === "draft" && (
              <button
                className="button primary"
                disabled={busy}
                onClick={() => act("publish", "Event published.")}
              >
                Publish
              </button>
            )}
            {event.status === "published" && (
              <ConfirmButton
                disabled={busy}
                message="Cancel this event? Booked attendees will be notified."
                onConfirm={() => act("cancel", "Event cancelled.")}
              >
                Cancel event
              </ConfirmButton>
            )}
            {event.status === "published" &&
              new Date(event.ends_at) <= new Date() && (
                <button
                  className="button secondary"
                  disabled={busy}
                  onClick={() => act("complete", "Event completed.")}
                >
                  Mark completed
                </button>
              )}
            <ConfirmButton
              className="button subtle danger-text"
              disabled={busy}
              message="Delete this event? It will be hidden, and active bookings will be cancelled."
              onConfirm={deleteEvent}
            >
              Delete event
            </ConfirmButton>
          </div>
        )}
      </div>
      <Alert message={error} />
      <Alert message={notice} kind="success" />
      <div className="detail-columns">
        <div className="detail-main">
          <div className="detail-banner">
            <span>EVENTDESK</span>
            <strong>{event.title}</strong>
            <span>{formatDate(event.starts_at)}</span>
          </div>
          <section className="card detail-section">
            <h2>About this event</h2>
            <p>{event.description}</p>
          </section>
          <Reviews eventId={id} event={event} />
        </div>
        <aside>
          <div className="card booking-panel">
            <span className="eyebrow">THE DETAILS</span>
            <h2>
              {formatMoney(event.ticket_price)} <small>/ ticket</small>
            </h2>
            <dl>
              <div>
                <dt>When</dt>
                <dd>{formatDate(event.starts_at)}</dd>
              </div>
              <div>
                <dt>Until</dt>
                <dd>{formatDate(event.ends_at)}</dd>
              </div>
              <div>
                <dt>Where</dt>
                <dd>{event.venue}</dd>
              </div>
              <div>
                <dt>Availability</dt>
                <dd>
                  {availability
                    ? `${availability.remaining_tickets} of ${availability.total_tickets} left`
                    : event.status === "published"
                      ? "Checking…"
                      : "Not on sale"}
                </dd>
              </div>
            </dl>
            {canBook && (availability?.remaining_tickets ?? 1) > 0 && (
              <form onSubmit={book}>
                <Field label="Tickets">
                  <input
                    type="number"
                    min="1"
                    max={availability?.remaining_tickets || undefined}
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    required
                  />
                </Field>
                <button className="button primary full" disabled={busy}>
                  Book {quantity} ticket{Number(quantity) === 1 ? "" : "s"}
                </button>
              </form>
            )}
            {isOwnEvent && event.status === "published" && (
              <p className="muted">You can't book your own event.</p>
            )}
            {!user && event.status === "published" && (
              <Link className="button primary full" to="/login">
                Sign in to book
              </Link>
            )}
            {availability?.remaining_tickets === 0 && (
              <p className="muted">Sold out for now.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
