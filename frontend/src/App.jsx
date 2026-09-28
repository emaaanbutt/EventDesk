import { Link, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { Layout } from "./components/Layout";
import { Busy } from "./components/UI";
import { LoginPage, ProfilePage, RegisterPage } from "./pages/AuthPages";
import { AdminPage } from "./pages/Admin";
import { BookingsPage } from "./pages/Bookings";
import {
  EventDetailPage,
  EventFormPage,
  EventsPage,
  HomePage,
  MyEventsPage,
} from "./pages/Events";
import { NotificationsPage } from "./pages/Notifications";

function Protected({ roles, children }) {
  const { user, loading } = useAuth();
  if (loading) return <Busy />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role))
    return (
      <div className="page-narrow">
        <h1>Access denied</h1>
        <p>Your account cannot open this page.</p>
        <Link to="/events">Back to events</Link>
      </div>
    );
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="events" element={<EventsPage />} />
        <Route path="events/:id" element={<EventDetailPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route
          path="profile"
          element={
            <Protected>
              <ProfilePage />
            </Protected>
          }
        />
        <Route
          path="bookings"
          element={
            <Protected>
              <BookingsPage />
            </Protected>
          }
        />
        <Route
          path="notifications"
          element={
            <Protected>
              <NotificationsPage />
            </Protected>
          }
        />
        <Route
          path="my-events"
          element={
            <Protected roles={["organizer", "admin"]}>
              <MyEventsPage />
            </Protected>
          }
        />
        <Route
          path="my-events/new"
          element={
            <Protected roles={["organizer", "admin"]}>
              <EventFormPage />
            </Protected>
          }
        />
        <Route
          path="my-events/:id/edit"
          element={
            <Protected roles={["organizer", "admin"]}>
              <EventFormPage />
            </Protected>
          }
        />
        <Route
          path="admin"
          element={
            <Protected roles={["admin"]}>
              <AdminPage />
            </Protected>
          }
        />
        <Route
          path="*"
          element={
            <div className="page-narrow">
              <h1>Page not found</h1>
              <Link to="/events">Explore events →</Link>
            </div>
          }
        />
      </Route>
    </Routes>
  );
}
