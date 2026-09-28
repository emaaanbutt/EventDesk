import { useEffect, useState } from "react";
import { api, query } from "../lib/api";
import {
  Alert,
  Busy,
  ConfirmButton,
  Empty,
  Field,
  formatDate,
  PageHeading,
  Pagination,
  Status,
} from "../components/UI";

export function AdminPage() {
  const [tab, setTab] = useState("users");
  return (
    <>
      <PageHeading
        eyebrow="ADMINISTRATION"
        title="Manage EventDesk"
        description="People, catalog, and activity in one place."
      />
      <div className="tabs" role="tablist" aria-label="Admin sections">
        {[
          ["users", "Users"],
          ["catalog", "Categories & tags"],
          ["audit", "Audit logs"],
        ].map(([key, title]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
          >
            {title}
          </button>
        ))}
      </div>
      {tab === "users" && <UsersAdmin />}
      {tab === "catalog" && <CatalogAdmin />}
      {tab === "audit" && <AuditAdmin />}
    </>
  );
}

function UsersAdmin() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [version, setVersion] = useState(0);
  useEffect(() => {
    api("/users/")
      .then(setUsers)
      .catch((err) => setError(err.message));
  }, [version]);
  async function update(id, path, body, message) {
    setError("");
    setNotice("");
    try {
      await api(`/users/${id}/${path}`, { method: "PATCH", body });
      setNotice(message);
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    }
  }
  async function remove(id) {
    setError("");
    setNotice("");
    try {
      await api(`/users/${id}`, { method: "DELETE" });
      setNotice("User deleted.");
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <>
      <Alert message={error} />
      <Alert message={notice} kind="success" />
      {!users && !error ? (
        <Busy />
      ) : users?.length ? (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((person) => (
                <tr key={person.id}>
                  <td>
                    <strong>{person.name}</strong>
                  </td>
                  <td>{person.email}</td>
                  <td>
                    <select
                      aria-label={`Role for ${person.name}`}
                      value={person.role}
                      onChange={(e) =>
                        update(
                          person.id,
                          "role",
                          { new_role: e.target.value },
                          "Role updated.",
                        )
                      }
                    >
                      <option value="attendee">Attendee</option>
                      <option value="organizer">Organizer</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td>
                    <Status value={person.is_active ? "active" : "inactive"} />
                  </td>
                  <td className="row-actions">
                    <button
                      className="button subtle small"
                      onClick={() =>
                        update(
                          person.id,
                          "active",
                          { is_active: !person.is_active },
                          "Account status updated.",
                        )
                      }
                    >
                      {person.is_active ? "Deactivate" : "Activate"}
                    </button>
                    <ConfirmButton
                      className="button subtle small danger-text"
                      message={`Delete ${person.name}? This is a soft delete.`}
                      onConfirm={() => remove(person.id)}
                    >
                      Delete
                    </ConfirmButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Empty title="No users" detail="Registered users will appear here." />
      )}
    </>
  );
}

function CatalogAdmin() {
  const [categories, setCategories] = useState(null);
  const [tags, setTags] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [version, setVersion] = useState(0);
  useEffect(() => {
    Promise.all([
      api("/categories", { auth: false }),
      api("/tags", { auth: false }),
    ])
      .then(([cats, allTags]) => {
        setCategories(cats);
        setTags(allTags);
      })
      .catch((err) => setError(err.message));
  }, [version]);
  async function create(event, kind) {
    event.preventDefault();
    setError("");
    setNotice("");
    const form = event.currentTarget;
    const name = new FormData(form).get("name");
    try {
      await api(`/${kind}`, { method: "POST", body: { name } });
      form.reset();
      setNotice(`${kind === "tags" ? "Tag" : "Category"} added.`);
      setVersion((value) => value + 1);
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <>
      <Alert message={error} />
      <Alert message={notice} kind="success" />
      <div className="two-cards">
        {[
          ["Categories", "categories", categories],
          ["Tags", "tags", tags],
        ].map(([title, kind, items]) => (
          <section key={kind} className="card form-card">
            <h2>{title}</h2>
            <p className="muted">Used to help people find events.</p>
            <form
              onSubmit={(event) => create(event, kind)}
              className="catalog-form"
            >
              <Field label={`New ${kind === "tags" ? "tag" : "category"}`}>
                <input name="name" maxLength="255" required />
              </Field>
              <button className="button primary small">Add</button>
            </form>
            {items ? (
              <div className="pill-list">
                {items.map((item) => (
                  <span key={item.id} className="pill">
                    {item.name}
                  </span>
                ))}
                {!items.length && <p className="muted">None yet.</p>}
              </div>
            ) : (
              <Busy />
            )}
          </section>
        ))}
      </div>
    </>
  );
}

const auditActions = {
  "profile.update": "Updated profile",
  "password.change": "Changed password",
  "users.role.change": "Changed a user's role",
  "users.active.change": "Changed account status",
  "users.delete": "Deleted a user",
  "events.create": "Created an event",
  "events.edit": "Updated an event",
  "events.publish": "Published an event",
  "events.complete": "Completed an event",
  "events.cancel": "Cancelled an event",
  "bookings.create": "Booked tickets",
  "bookings.cancel": "Cancelled a booking",
};

const auditFields = {
  name: "name",
  email: "email address",
  title: "title",
  description: "description",
  venue: "venue",
  starts_at: "start time",
  ends_at: "end time",
  ticket_price: "ticket price",
  total_tickets: "ticket quantity",
  category_id: "category",
  tag_ids: "tags",
};

function auditEntity(item) {
  if (item.entity_type === "user") return item.entity_name || "Deleted user";
  if (item.entity_type === "event") return item.entity_name || "Deleted event";
  if (item.entity_type === "booking")
    return item.entity_name ? `Booking for ${item.entity_name}` : "Booking";
  return item.entity_type.replaceAll("_", " ");
}

function auditDetails(item) {
  const details = item.details;
  if (!details) return "—";
  if (details.old_role && details.new_role)
    return `${details.old_role} → ${details.new_role}`;
  if (typeof details.is_active === "boolean")
    return details.is_active ? "Account activated" : "Account deactivated";
  if (details.fields?.length)
    return `Changed ${details.fields.map((field) => auditFields[field] || field.replaceAll("_", " ")).join(", ")}`;
  if (typeof details.quantity === "number")
    return `${details.quantity} ticket${details.quantity === 1 ? "" : "s"}`;
  if (details.source === "scheduler") return "Completed automatically";
  return "—";
}

function AuditAdmin() {
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    api(query("/audit-logs", { page, page_size: 15 }))
      .then((data) => {
        if (active) setResult(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [page]);
  return (
    <>
      <Alert message={error} />
      {!result && !error ? (
        <Busy />
      ) : result?.items.length ? (
        <>
          <div className="card table-wrap">
            <table>
              <thead>
                <tr>
                  <th>When</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {result.items.map((item) => (
                  <tr key={item.id}>
                    <td>{formatDate(item.created_at)}</td>
                    <td>{item.actor?.name || "System"}</td>
                    <td>
                      {auditActions[item.action] ||
                        item.action.replaceAll(".", " ")}
                    </td>
                    <td>{auditEntity(item)}</td>
                    <td>{auditDetails(item)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination {...result} onPage={setPage} />
        </>
      ) : (
        <Empty
          title="No activity yet"
          detail="Important actions will show up here."
        />
      )}
    </>
  );
}
