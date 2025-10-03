import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import TaskDetailScreen from '@/pages/Task Detail Screen';
import LoginScreen from '@/pages/Login Screen';
import HomeScreen from '@/pages/Home Screen';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <div>Something went wrong!</div>,
    children: [
      {
    path: '/task_detail_screen/:animation_duration:easing:show_success_message:confirm_discard',
    element: <TaskDetailScreen />
  },
  {
    path: '/login_screen/:animation_duration:easing',
    element: <LoginScreen />
  },
  {
    path: '/home_screen/:animation_duration:easing:task_id',
    element: <HomeScreen />
  },
      {
        path: '*',
        element: <Navigate to="/" replace />
      }
    ]
  }
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;