import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { api, setTokens } from "../lib/api";
import { Alert, Field, PageHeading } from "../components/UI";

export function LoginPage() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/events" replace />;
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      await signIn(data.get("email"), data.get("password"));
      navigate("/events");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-layout">
      <div className="auth-aside">
        <span className="eyebrow">WELCOME BACK</span>
        <h1>
          Find your next
          <br />
          <em>good moment.</em>
        </h1>
        <p>
          Explore events, keep your bookings close, and never miss an update.
        </p>
      </div>
      <form className="card auth-card" onSubmit={submit}>
        <h2>Sign in</h2>
        <p className="muted">Welcome back to EventDesk.</p>
        <Alert message={error} />
        <Alert message={location.state?.notice} kind="success" />
        <Field label="Email">
          <input type="email" name="email" required autoComplete="email" />
        </Field>
        <Field label="Password">
          <input
            type="password"
            name="password"
            required
            autoComplete="current-password"
          />
        </Field>
        <button className="button primary full" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="form-foot">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </form>
    </div>
  );
}

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/events" replace />;
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const data = new FormData(event.currentTarget);
    const password = data.get("password");
    if (password !== data.get("confirm_password")) {
      setError("Passwords do not match.");
      setBusy(false);
      return;
    }
    try {
      await register({
        name: data.get("name"),
        email: data.get("email"),
        password,
        role: data.get("role"),
      });
      navigate("/events");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-layout">
      <div className="auth-aside">
        <span className="eyebrow">COME ON IN</span>
        <h1>
          Make room for
          <br />
          <em>new experiences.</em>
        </h1>
        <p>
          Join as an attendee to discover events, or as an organizer to host
          your own.
        </p>
      </div>
      <form className="card auth-card" onSubmit={submit}>
        <h2>Create account</h2>
        <p className="muted">A few details and you’re ready to go.</p>
        <Alert message={error} />
        <Field label="Name">
          <input name="name" maxLength="100" required autoComplete="name" />
        </Field>
        <Field label="Email">
          <input type="email" name="email" required autoComplete="email" />
        </Field>
        <Field label="I want to">
          <select name="role" defaultValue="" required>
            <option value="" disabled>
              Choose one
            </option>
            <option value="attendee">Attend events</option>
            <option value="organizer">Organize events</option>
          </select>
        </Field>
        <Field
          label="Password"
          hint="At least 8 characters, an uppercase letter, a number, and a special character."
        >
          <input
            type="password"
            name="password"
            minLength="8"
            maxLength="72"
            required
            autoComplete="new-password"
          />
        </Field>
        <Field label="Confirm password">
          <input
            type="password"
            name="confirm_password"
            required
            autoComplete="new-password"
          />
        </Field>
        <button className="button primary full" disabled={busy}>
          {busy ? "Creating account…" : "Create account"}
        </button>
        <p className="form-foot">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}

export function ProfilePage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  async function saveProfile(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    const data = new FormData(event.currentTarget);
    try {
      const updated = await api("/users/me", {
        method: "PATCH",
        body: { name: data.get("name"), email: data.get("email") },
      });
      setUser(updated);
      setSuccess("Profile updated.");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  async function changePassword(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    const form = event.currentTarget;
    const data = new FormData(form);
    if (data.get("new_password") !== data.get("confirm_password")) {
      setError("New passwords do not match.");
      setBusy(false);
      return;
    }
    try {
      await api("/users/me/password", {
        method: "PATCH",
        body: {
          current_password: data.get("current_password"),
          new_password: data.get("new_password"),
        },
      });
      form.reset();
      setTokens(null);
      navigate("/login", {
        state: { notice: "Password changed. Sign in with your new password." },
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="page-narrow">
      <PageHeading
        eyebrow="YOUR ACCOUNT"
        title="Profile & security"
        description={`Signed in as ${user.role}.`}
      />
      <Alert message={error} />
      <Alert message={success} kind="success" />
      <div className="stack">
        <form className="card form-card" onSubmit={saveProfile}>
          <h2>Your details</h2>
          <Field label="Name">
            <input
              name="name"
              defaultValue={user.name}
              required
              maxLength="100"
            />
          </Field>
          <Field label="Email">
            <input
              type="email"
              name="email"
              defaultValue={user.email}
              required
            />
          </Field>
          <button className="button primary" disabled={busy}>
            Save changes
          </button>
        </form>
        <form className="card form-card" onSubmit={changePassword}>
          <h2>Change password</h2>
          <Field label="Current password">
            <input type="password" name="current_password" required />
          </Field>
          <Field
            label="New password"
            hint="8+ characters, uppercase, number, special character."
          >
            <input
              type="password"
              name="new_password"
              required
              minLength="8"
              maxLength="72"
            />
          </Field>
          <Field label="Confirm new password">
            <input type="password" name="confirm_password" required />
          </Field>
          <button className="button secondary" disabled={busy}>
            Update password
          </button>
        </form>
      </div>
    </div>
  );
}
