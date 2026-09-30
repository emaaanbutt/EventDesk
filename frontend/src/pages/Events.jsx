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

function parseLocalDate(value, withTime = false) {
  const match = withTime
    ? /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(value)
    : /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return null;
  const [, year, month, day, hour = 0, minute = 0] = match.map(Number);
  if (year < 1000) return null;
  const date = new Date(year, month - 1, day, hour, minute);
  const matches = date.getFullYear() === year &&
    date.getMonth() === month - 1 && date.getDate() === day &&
    date.getHours() === hour && date.getMinutes() === minute;
  return matches ? date : null;
}

function eventInputErrors(form) {
  const titleValue = form.elements.title.value.trim();
  const venueValue = form.elements.venue.value.trim();
  const descriptionValue = form.elements.description.value.trim();
  const startValue = form.elements.starts_at.value;
  const endValue = form.elements.ends_at.value;
  const priceValue = form.elements.ticket_price.value;
  const ticketsValue = form.elements.total_tickets.value;
  const start = parseLocalDate(startValue, true);
  const end = parseLocalDate(endValue, true);
  const price = Number(priceValue);
  const tickets = Number(ticketsValue);
  let starts_at = "";
  let ends_at = "";
  let ticket_price = "";
  let total_tickets = "";

  if (form.elements.starts_at.validity?.badInput) starts_at = "Enter a valid start date and time with a four-digit year.";
  else if (!startValue) starts_at = "Choose a start date and time.";
  else if (!start) starts_at = "Enter a valid start date and time with a four-digit year.";
  else if (start <= new Date()) starts_at = "Choose a start date and time in the future.";

  if (form.elements.ends_at.validity?.badInput) ends_at = "Enter a valid end date and time with a four-digit year.";
  else if (!endValue) ends_at = "Choose an end date and time.";
  else if (!end) ends_at = "Enter a valid end date and time with a four-digit year.";
  else if (start && end <= start) ends_at = "End date and time must be later than the start.";

  if (form.elements.ticket_price.validity?.badInput) ticket_price = "Enter a valid ticket price.";
  else if (priceValue === "") ticket_price = "Enter a ticket price.";
  else if (!Number.isFinite(price)) ticket_price = "Enter a valid ticket price.";
  else if (price < 0) ticket_price = "Ticket price cannot be negative.";
  else if (!/^\d+(?:\.\d{1,2})?$/.test(priceValue)) ticket_price = "Use no more than two decimal places.";
  else if (price > 99999999.99) ticket_price = "Ticket price must be below PKR 100,000,000.";

  if (form.elements.total_tickets.validity?.badInput) total_tickets = "Enter a whole number of tickets.";
  else if (ticketsValue === "") total_tickets = "Enter the number of tickets.";
  else if (!Number.isInteger(tickets) || tickets < 1) total_tickets = "Enter at least one whole ticket.";

  return {
    title: titleValue ? "" : "Enter an event title.",
    venue: venueValue ? "" : "Enter a venue.",
    description: descriptionValue ? "" : "Enter a description.",
    starts_at,
    ends_at,
    ticket_price,
    total_tickets,
  };
}

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
  const [refresh, setRefresh] = useState(0);
  const [filterInputError, setFilterInputError] = useState("");
  const dateError = filterInputError ||
    (filters.date_from && !parseLocalDate(filters.date_from) ? "Enter a valid From date with a four-digit year." : "") ||
    (filters.date_to && !parseLocalDate(filters.date_to) ? "Enter a valid To date with a four-digit year." : "") ||
    (filters.date_from && filters.date_to && filters.date_from > filters.date_to ? "From date must be on or before To date." : "");
  const hasFilters = Boolean(filters.search.trim() || filters.category_id || filters.tag_id || filters.date_from || filters.date_to);
  useEffect(() => {
    Promise.all([
      api("/categories", { auth: false }),
      api("/tags", { auth: false }),
    ])
      .then(([categories, tags]) => setCatalog({ categories, tags }))
      .catch((err) => setError(err.message));
  }, []);
  useEffect(() => {
    const timer = window.setInterval(() => setRefresh((value) => value + 1), 60000);
    return () => window.clearInterval(timer);
  }, []);
  useEffect(() => {
    let active = true;
    setError("");
    if (dateError) return;
    const params = {
      ...filters,
      search: filters.search.trim(),
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
  }, [filters, dateError, refresh]);
  const update = (key, value) => {
    setResult(null);
    setFilters((old) => ({ ...old, [key]: value, page: 1 }));
  };
  const clearFilters = () => {
    setFilterInputError("");
    setResult(null);
    setFilters((old) => ({ ...old, search: "", category_id: "", tag_id: "", date_from: "", date_to: "", page: 1 }));
  };
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
          maxLength={100}
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
            aria-invalid={Boolean(dateError)}
            aria-describedby={dateError ? "event-filter-error" : undefined}
            onInput={(e) => setFilterInputError(e.currentTarget.validity.badInput ? "Enter a valid date with a four-digit year." : "")}
            onChange={(e) => update("date_from", e.target.value)}
          />
        </label>
        <label className="date-filter">
          To{" "}
          <input
            type="date"
            value={filters.date_to}
            min={filters.date_from || undefined}
            aria-invalid={Boolean(dateError)}
            aria-describedby={dateError ? "event-filter-error" : undefined}
            onInput={(e) => setFilterInputError(e.currentTarget.validity.badInput ? "Enter a valid date with a four-digit year." : "")}
            onChange={(e) => update("date_to", e.target.value)}
          />
        </label>
      </div>
      {dateError && (
        <p id="event-filter-error" className="filter-error" role="status">
          {dateError}{" "}
          <button type="button" className="text-button" onClick={clearFilters}>Clear filters</button>
        </p>
      )}
      <Alert message={error} />
      {dateError || (!result && error) ? null : !result ? (
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
        <Empty
          title={hasFilters ? "No events match these filters" : "No upcoming events yet"}
          detail={hasFilters ? "Try a different date, category, or search term." : "Check back soon for new events."}
          action={hasFilters && <button className="button secondary" onClick={clearFilters}>Clear filters</button>}
        />
      )}
    </>
  );
}

export function MyEventsPage() {
  const [events, setEvents] = useState(null);
  const [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const timer = window.setInterval(() => setRefresh((value) => value + 1), 60000);
    return () => window.clearInterval(timer);
  }, []);
  useEffect(() => {
    api("/events/mine")
      .then((data) => { setEvents(data); setError(""); })
      .catch((err) => setError(err.message));
  }, [refresh]);
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
      ) : !events ? null : events.length ? (
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
  if (Number.isNaN(date.getTime())) return "";
  const pad = (number) => String(number).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
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
  const [fieldErrors, setFieldErrors] = useState({});
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
          setFieldErrors({});
        }
      })
      .catch((err) => setError(err.message));
  }, [id, isEdit]);
  function updateFieldFeedback(e) {
    const form = e.currentTarget;
    const name = e.target.name;
    setError("");
    if (name === "category_id") {
      setFieldErrors((current) => ({ ...current, category_id: "" }));
      return;
    }
    if (!["title", "venue", "description", "starts_at", "ends_at", "ticket_price", "total_tickets"].includes(name)) return;
    const next = eventInputErrors(form);
    setFieldErrors((current) => ({
      ...current,
      [name]: next[name],
      ...(name === "starts_at" && form.elements.ends_at.value ? { ends_at: next.ends_at } : {}),
      ...(name === "ends_at" && form.elements.starts_at.value ? { starts_at: next.starts_at } : {}),
    }));
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    const element = e.currentTarget;
    const validation = eventInputErrors(element);
    setFieldErrors(validation);
    const firstInvalid = Object.keys(validation).find((name) => validation[name]);
    if (firstInvalid) {
      element.elements[firstInvalid].focus();
      return;
    }
    const form = new FormData(element);
    const start = parseLocalDate(form.get("starts_at"), true);
    const end = parseLocalDate(form.get("ends_at"), true);
    setBusy(true);
    const body = {
      title: form.get("title"),
      description: form.get("description"),
      venue: form.get("venue"),
      starts_at: start.toISOString(),
      ends_at: end.toISOString(),
      ticket_price: form.get("ticket_price"),
      total_tickets: Number(form.get("total_tickets")),
      category_id: form.get("category_id") || null,
      tag_ids: selectedTags,
    };
    try {
      const saved = await api(isEdit ? `/events/${id}` : "/events/", {
        method: isEdit ? "PATCH" : "POST",
        body,
      });
      navigate(`/events/${saved.id}`);
    } catch (err) {
      if (err.fieldErrors && Object.keys(err.fieldErrors).length) {
        setFieldErrors((current) => ({ ...current, ...err.fieldErrors }));
        setError("Please check the highlighted fields and try again.");
      } else {
        setError(err.message);
      }
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
      {isEdit && !event ? (
        !error && <Busy />
      ) : (
        <form
          className="card form-card"
          onSubmit={submit}
          onInput={updateFieldFeedback}
          key={event?.id || "new"}
        >
          <div className="form-grid">
            <Field label="Title" error={fieldErrors.title}>
              <input
                name="title"
                defaultValue={event?.title}
                required
                maxLength="255"
              />
            </Field>
            <Field label="Venue" error={fieldErrors.venue}>
              <input
                name="venue"
                defaultValue={event?.venue}
                required
                maxLength="255"
              />
            </Field>
            <Field label="Starts at" error={fieldErrors.starts_at}>
              <input
                type="datetime-local"
                name="starts_at"
                defaultValue={toLocalInput(event?.starts_at)}
                required
              />
            </Field>
            <Field label="Ends at" error={fieldErrors.ends_at}>
              <input
                type="datetime-local"
                name="ends_at"
                defaultValue={toLocalInput(event?.ends_at)}
                required
              />
            </Field>
            <Field label="Ticket price (PKR)" error={fieldErrors.ticket_price}>
              <input
                type="number"
                name="ticket_price"
                defaultValue={event?.ticket_price || 0}
                min="0"
                step="0.01"
                required
              />
            </Field>
            <Field label="Total tickets" error={fieldErrors.total_tickets}>
              <input
                type="number"
                name="total_tickets"
                defaultValue={event?.total_tickets || 1}
                min="1"
                step="1"
                required
              />
            </Field>
            <Field label="Category" error={fieldErrors.category_id}>
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
          <Field label="Description" error={fieldErrors.description}>
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
                      onChange={(e) => {
                        setError("");
                        setFieldErrors((current) => ({ ...current, tag_ids: "" }));
                        setSelectedTags((old) =>
                          e.target.checked
                            ? [...old, tag.id]
                            : old.filter((tagId) => tagId !== tag.id),
                        );
                      }}
                    />
                    {tag.name}
                  </label>
                ))
              ) : (
                <small>No tags yet.</small>
              )}
            </div>
            {fieldErrors.tag_ids && <small className="field-error" role="status">{fieldErrors.tag_ids}</small>}
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
  const [availabilityError, setAvailabilityError] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [quantityBadInput, setQuantityBadInput] = useState(false);
  const [notice, setNotice] = useState("");
  const [reload, setReload] = useState(0);
  const [now, setNow] = useState(Date.now());
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
        if (active) {
          if (err.status === 404) setEvent(null);
          setError(err.message);
        }
      });
    return () => {
      active = false;
    };
  }, [id, user?.id, reload]);
  useEffect(() => {
    if (!event || !["published", "completed", "cancelled"].includes(event.status)) return;
    let active = true;
    setAvailability(null);
    setAvailabilityError("");
    if (["published", "completed"].includes(event.status)) {
      api(`/events/${id}/availability`, { auth: false })
        .then((data) => {
          if (active) setAvailability(data);
        })
        .catch(() => {
          if (active) setAvailabilityError("Ticket information is unavailable. Please try again later.");
        });
    }
    const socket = openSocket(`/ws/events/${id}`);
    socket.onmessage = (message) => {
      const update = JSON.parse(message.data);
      if (active && update.type === "event.availability")
        setAvailability(update.data);
      if (active && update.type === "event.unavailable")
        setReload((value) => value + 1);
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
  useEffect(() => {
    if (event?.status !== "published") return;
    const timer = window.setInterval(() => {
      setNow(Date.now());
      if (new Date(event.ends_at) <= new Date())
        setReload((value) => value + 1);
    }, 30000);
    return () => window.clearInterval(timer);
  }, [event?.status, event?.ends_at]);
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
    if (quantityError) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/bookings", {
        method: "POST",
        body: { event_id: id, quantity: Number(quantity) },
      });
      setNotice("Booking confirmed. You can find it under My bookings.");
      try {
        const next = await api(`/events/${id}/availability`, { auth: false });
        setAvailability(next);
      } catch {
        setReload((value) => value + 1);
      }
    } catch (err) {
      setError(err.message);
      if (err.status === 409) {
        api(`/events/${id}/availability`, { auth: false })
          .then(setAvailability)
          .catch(() => setReload((value) => value + 1));
      }
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
  const bookingClosed = new Date(event.starts_at).getTime() <= now;
  const quantityNumber = Number(quantity);
  const quantityError = quantityBadInput ? "Enter a whole number of tickets." : quantity === "" ? "Enter how many tickets you want." :
    !Number.isInteger(quantityNumber) || quantityNumber < 1 ? "Enter at least one whole ticket." :
    availability && quantityNumber > availability.remaining_tickets ? `Only ${availability.remaining_tickets} ticket${availability.remaining_tickets === 1 ? " is" : "s are"} left.` : "";
  const canBook =
    event.status === "published" &&
    user &&
    !isOwnEvent &&
    !bookingClosed;
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
                <dt>{event.status === "completed" ? "Tickets booked" : "Availability"}</dt>
                <dd>
                  {event.status === "completed"
                    ? availability ? `${availability.booked_tickets} ticket${availability.booked_tickets === 1 ? "" : "s"}` : availabilityError || "Checking…"
                    : event.status === "published" && bookingClosed
                      ? "Booking closed"
                      : availability && event.status === "published"
                        ? `${availability.remaining_tickets} of ${availability.total_tickets} left`
                        : event.status === "published"
                          ? availabilityError || "Checking…"
                          : "Not on sale"}
                </dd>
              </div>
            </dl>
            {canBook && availability?.remaining_tickets > 0 && (
              <form onSubmit={book}>
                <Field label="Tickets" error={quantityError}>
                  <input
                    type="number"
                    min="1"
                    max={availability?.remaining_tickets || undefined}
                    value={quantity}
                    onChange={(e) => { setQuantity(e.target.value); setQuantityBadInput(e.currentTarget.validity.badInput); setError(""); }}
                    required
                  />
                </Field>
                <button className="button primary full" disabled={busy}>
                  Book {quantity} ticket{Number(quantity) === 1 ? "" : "s"}
                </button>
              </form>
            )}
            {event.status === "completed" && (
              <p className="muted">This event has ended. Booking is closed.</p>
            )}
            {event.status === "published" && bookingClosed && (
              <p className="muted">Booking has closed for this event.</p>
            )}
            {isOwnEvent && event.status === "published" && !bookingClosed && (
              <p className="muted">You can't book your own event.</p>
            )}
            {!user && event.status === "published" && !bookingClosed && availability?.remaining_tickets > 0 && (
              <Link className="button primary full" to="/login">
                Sign in to book
              </Link>
            )}
            {event.status === "published" && !bookingClosed && availability?.remaining_tickets === 0 && (
              <p className="muted">Sold out for now.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
