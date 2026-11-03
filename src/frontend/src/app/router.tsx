import { type RouteObject } from "react-router-dom";
import { Layout } from "./Layout";
import { HomePage } from "../features/home/HomePage";
import { LoginPage } from "../features/auth/LoginPage";
import { RegisterPage } from "../features/auth/RegisterPage";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { TaskListPage } from "../features/contribute/TaskListPage";
import { TaskDetailPage } from "../features/contribute/TaskDetailPage";
import { ReviewPage } from "../features/review/ReviewPage";
import { MyContributionsPage } from "../features/my/MyContributionsPage";
import { DictionaryListPage } from "../features/glossary/DictionaryListPage";
import { DictionaryDetailPage } from "../features/glossary/DictionaryDetailPage";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      {
        path: "tasks",
        element: (
          <ProtectedRoute>
            <TaskListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "tasks/:id",
        element: (
          <ProtectedRoute>
            <TaskDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "review",
        element: (
          <ProtectedRoute>
            <ReviewPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "my",
        element: (
          <ProtectedRoute>
            <MyContributionsPage />
          </ProtectedRoute>
        ),
      },
      { path: "dictionary", element: <DictionaryListPage /> },
      { path: "dictionary/:id", element: <DictionaryDetailPage /> },
    ],
  },
];

