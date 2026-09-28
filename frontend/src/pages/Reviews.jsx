import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { api, query } from "../lib/api";
import {
  Alert,
  Busy,
  ConfirmButton,
  Empty,
  Field,
  formatDate,
  Pagination,
} from "../components/UI";

function ReviewItem({ review, canReply, user, eventOrganizerId, onChanged }) {
  const [replies, setReplies] = useState([]);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [replying, setReplying] = useState(false);
  const [busy, setBusy] = useState(false);
  const loadReplies = useCallback(
    () =>
      api(`/reviews/${review.id}/replies`, { auth: false })
        .then(setReplies)
        .catch((err) => setError(err.message)),
    [review.id],
  );
  useEffect(() => {
    loadReplies();
  }, [loadReplies]);
  useEffect(() => {
    const onReply = (event) => {
      if (event.detail === review.id) loadReplies();
    };
    window.addEventListener("eventdesk:review-reply", onReply);
    return () => window.removeEventListener("eventdesk:review-reply", onReply);
  }, [review.id, loadReplies]);
  async function saveEdit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      await api(`/reviews/${review.id}`, {
        method: "PATCH",
        body: {
          rating: Number(form.get("rating")),
          comment: form.get("comment"),
        },
      });
      setEditing(false);
      onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  async function addReply(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = e.currentTarget;
    try {
      const reply = await api(`/reviews/${review.id}/replies`, {
        method: "POST",
        body: { comment: new FormData(form).get("comment") },
      });
      form.reset();
      setReplying(false);
      setReplies((current) =>
        current.some((item) => item.id === reply.id)
          ? current
          : [...current, reply],
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  async function deleteReview() {
    setBusy(true);
    setError("");
    try {
      await api(`/reviews/${review.id}`, { method: "DELETE" });
      onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  const canChange =
    user && (user.id === review.author_id || user.role === "admin");
  return (
    <article className="review">
      <div className="review-head">
        <span className="avatar">
          {(review.author_name || "?").slice(0, 1).toUpperCase()}
        </span>
        <div>
          <strong>
            {user?.id === review.author_id
              ? "You"
              : review.author_name || "Former member"}
          </strong>
          <span className="muted">{formatDate(review.created_at)}</span>
        </div>
        <span className="stars">
          {"★".repeat(review.rating)}
          {"☆".repeat(5 - review.rating)}
        </span>
      </div>
      <p>{review.comment}</p>
      <Alert message={error} />
      {editing && (
        <form onSubmit={saveEdit} className="inline-form">
          <Field label="Rating">
            <select name="rating" defaultValue={review.rating}>
              {[1, 2, 3, 4, 5].map((number) => (
                <option key={number} value={number}>
                  {number} star{number > 1 ? "s" : ""}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Comment">
            <textarea
              name="comment"
              defaultValue={review.comment}
              maxLength="500"
              required
            />
          </Field>
          <div className="form-actions">
            <button disabled={busy} className="button primary small">
              Save review
            </button>
            <button
              type="button"
              className="button subtle small"
              onClick={() => setEditing(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
      {!editing && canChange && (
        <div className="inline-actions">
          {user.id !== eventOrganizerId && (
            <button className="text-button" onClick={() => setEditing(true)}>
              Edit
            </button>
          )}
          <ConfirmButton
            className="text-button danger-text"
            disabled={busy}
            message="Delete this review?"
            onConfirm={deleteReview}
          >
            Delete
          </ConfirmButton>
        </div>
      )}
      {replies.map((reply) => (
        <div className="reply" key={reply.id}>
          <strong>
            {user?.id === reply.author_id
              ? "You"
              : reply.author_name || "Former member"}
          </strong>
          <span className="muted"> · {formatDate(reply.created_at)}</span>
          <p>{reply.comment}</p>
        </div>
      ))}
      {canReply && !replies.some((reply) => reply.author_id === user.id) && (
        <>
          {!replying ? (
            <button className="text-button" onClick={() => setReplying(true)}>
              Reply to this review
            </button>
          ) : (
            <form onSubmit={addReply} className="inline-form">
              <Field label="Your reply">
                <textarea name="comment" maxLength="500" required />
              </Field>
              <div className="form-actions">
                <button disabled={busy} className="button primary small">
                  Post reply
                </button>
                <button
                  type="button"
                  className="button subtle small"
                  onClick={() => setReplying(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </>
      )}
    </article>
  );
}

export function Reviews({ eventId, event }) {
  const { user } = useAuth();
  const [result, setResult] = useState(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [version, setVersion] = useState(0);
  useEffect(() => {
    let active = true;
    api(query("/reviews", { event_id: eventId, page, page_size: 5 }), {
      auth: false,
    })
      .then((data) => {
        if (active) setResult(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [eventId, page, version]);
  async function addReview(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = e.currentTarget;
    const data = new FormData(form);
    try {
      await api("/reviews", {
        method: "POST",
        body: {
          event_id: eventId,
          rating: Number(data.get("rating")),
          comment: data.get("comment"),
        },
      });
      form.reset();
      setPage(1);
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  const canReply =
    user && (user.id === event.organizer_id || user.role === "admin");
  return (
    <section className="card detail-section reviews-section">
      <div className="section-title">
        <div>
          <span className="eyebrow">FROM THE COMMUNITY</span>
          <h2>Reviews {result ? `(${result.total})` : ""}</h2>
        </div>
      </div>
      <Alert message={error} />
      {user && user.id !== event.organizer_id && event.status !== "cancelled" && (
        <form onSubmit={addReview} className="review-compose">
          <h3>Leave a review</h3>
          <p className="muted">
            You need a confirmed booking for this event to review it.
          </p>
          <div className="compose-fields">
            <Field label="Rating">
              <select name="rating" defaultValue="5">
                {[5, 4, 3, 2, 1].map((number) => (
                  <option key={number} value={number}>
                    {number} star{number > 1 ? "s" : ""}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Comment">
              <textarea
                name="comment"
                maxLength="500"
                rows="2"
                required
                placeholder="How was it?"
              />
            </Field>
          </div>
          <button className="button secondary small" disabled={busy}>
            Post review
          </button>
        </form>
      )}
      {!result && !error ? (
        <Busy />
      ) : result?.items.length ? (
        <>
          <div className="review-list">
            {result.items.map((review) => (
              <ReviewItem
                key={review.id}
                review={review}
                user={user}
                canReply={canReply}
                eventOrganizerId={event.organizer_id}
                onChanged={() => setVersion((value) => value + 1)}
              />
            ))}
          </div>
          <Pagination {...result} onPage={setPage} />
        </>
      ) : (
        <Empty
          title="No reviews yet"
          detail="Be the first to share your experience."
        />
      )}
    </section>
  );
}
