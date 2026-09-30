import { cloneElement, isValidElement, useId, useState } from "react";
import { Link } from "react-router-dom";

export function Alert({ message, kind = "error" }) {
  return message ? (
    <div role={kind === "error" ? "alert" : "status"} className={`alert ${kind}`}>
      <span className="alert-icon" aria-hidden="true">{kind === "error" ? "!" : "✓"}</span>
      <div>
        <strong>{kind === "error" ? "Something needs attention" : "All set"}</strong>
        <span>{message}</span>
      </div>
    </div>
  ) : null;
}

export function Busy({ label = "Loading…" }) {
  return <div className="busy">{label}</div>;
}

export function Empty({ title, detail, action }) {
  return (
    <div className="empty">
      <span className="empty-icon" aria-hidden="true">✦</span>
      <h3>{title}</h3>
      <p>{detail}</p>
      {action}
    </div>
  );
}

export function PageHeading({ eyebrow, title, description, actions }) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="heading-actions">{actions}</div>}
    </div>
  );
}

export function Pagination({ page, page_size: pageSize, total, onPage }) {
  if (!total || total <= pageSize) return null;
  const pages = Math.ceil(total / pageSize);
  return (
    <div className="pagination">
      <span>
        {total} total · page {page} of {pages}
      </span>
      <div>
        <button
          className="button secondary"
          disabled={page <= 1}
          onClick={() => onPage(page - 1)}
        >
          Previous
        </button>
        <button
          className="button secondary"
          disabled={page >= pages}
          onClick={() => onPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export function Status({ value }) {
  return (
    <span className={`status status-${value}`}>
      {value?.replaceAll("_", " ")}
    </span>
  );
}

export function ConfirmButton({
  children,
  message,
  onConfirm,
  className = "button danger",
  disabled,
}) {
  return (
    <button
      type="button"
      className={className}
      disabled={disabled}
      onClick={() => {
        if (window.confirm(message)) onConfirm();
      }}
    >
      {children}
    </button>
  );
}

function nativeMessage(input, label) {
  const { validity, min, max, minLength, maxLength, type } = input;
  if (validity.valueMissing) {
    if (type === "select-one") return "Choose an option.";
    if (label.toLowerCase().startsWith("confirm")) return "Confirm your password.";
    return `Enter ${label.toLowerCase()}.`;
  }
  if (validity.badInput || validity.typeMismatch)
    return type === "email" ? "Enter a valid email address." : `Enter a valid ${label.toLowerCase()}.`;
  if (validity.rangeUnderflow)
    return Number(min) === 0 ? `${label} cannot be negative.` : `${label} must be at least ${min}.`;
  if (validity.rangeOverflow) return `${label} must be ${max} or less.`;
  if (validity.stepMismatch)
    return Number(input.step) === 1 ? `${label} must be a whole number.` : `${label} can have up to two decimal places.`;
  if (validity.tooShort) return `${label} must be at least ${minLength} characters.`;
  if (validity.tooLong) return `${label} must be ${maxLength} characters or fewer.`;
  if (validity.patternMismatch) return `Enter a valid ${label.toLowerCase()}.`;
  return "";
}

export function Field({ label, children, hint, error, validate }) {
  const errorId = useId();
  const [nativeError, setNativeError] = useState("");
  const message = error === undefined ? nativeError : error;
  const isControl = isValidElement(children) && ["input", "select", "textarea"].includes(children.type);
  const control = isControl ? cloneElement(children, {
    "aria-invalid": Boolean(message),
    "aria-describedby": [children.props["aria-describedby"], message ? errorId : null].filter(Boolean).join(" ") || undefined,
    onInput: (event) => {
      setNativeError(validate?.(event.currentTarget.value, event.currentTarget) || nativeMessage(event.currentTarget, label));
      children.props.onInput?.(event);
    },
    onInvalid: (event) => {
      event.preventDefault();
      setNativeError(validate?.(event.currentTarget.value, event.currentTarget) || nativeMessage(event.currentTarget, label));
      children.props.onInvalid?.(event);
    },
  }) : children;
  return (
    <label className={`field${message ? " field-invalid" : ""}`}>
      <span>{label}</span>
      {control}
      {message ? <small id={errorId} className="field-error">{message}</small> : hint && <small>{hint}</small>}
    </label>
  );
}

export function EventCard({ event }) {
  return (
    <article className="event-card">
      <div className="event-card-top">
        <span className="eyebrow">{event.category?.name || "EVENT"}</span>
        <Status value={event.status} />
      </div>
      <h3>
        <Link to={`/events/${event.id}`}>{event.title}</Link>
      </h3>
      <p className="muted clamp">{event.description}</p>
      <div className="event-meta">
        <span>{formatDate(event.starts_at)}</span>
        <span>{event.venue}</span>
      </div>
      <div className="event-card-bottom">
        <strong>{formatMoney(event.ticket_price)}</strong>
        <Link to={`/events/${event.id}`} className="text-link">
          View details →
        </Link>
      </div>
    </article>
  );
}

export function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatMoney(value) {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

export function shortId(value) {
  return value ? `${value.slice(0, 8)}…` : "—";
}
