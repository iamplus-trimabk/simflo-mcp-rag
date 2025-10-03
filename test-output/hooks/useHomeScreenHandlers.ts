import { useCallback } from 'react';\nimport { useNavigate } from 'react-router-dom';

export const useHomeScreenHandlers = () => {
  const navigate = useNavigate();

  const handleNavigateToTask_Detail_Screen = useCallback(() => {
    navigate('/task_detail_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out', 'task_id': 'task_1'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToTask_Detail_Screen = useCallback(() => {
    navigate('/task_detail_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out', 'task_id': 'task_2'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToTask_Detail_Screen = useCallback(() => {
    navigate('/task_detail_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out', 'task_id': 'task_3'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToAdd_Task_Screen = useCallback(() => {
    navigate('/add_task_screen'{#if flow.parameters}{{'animation_duration': 300, 'easing': 'ease-in-out'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToTasks_Screen = useCallback(() => {
    navigate('/tasks_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToCalendar_Screen = useCallback(() => {
    navigate('/calendar_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out'}}{/if});
  }, [navigate]);
\n
  const handleNavigateToProfile_Screen = useCallback(() => {
    navigate('/profile_screen'{#if flow.parameters}{{'animation_duration': 250, 'easing': 'ease-out'}}{/if});
  }, [navigate]);

  return {
const handleNavigateToTask_Detail_Screen,const handleNavigateToTask_Detail_Screen,const handleNavigateToTask_Detail_Screen,const handleNavigateToAdd_Task_Screen,const handleNavigateToTasks_Screen,const handleNavigateToCalendar_Screen,const handleNavigateToProfile_Screen
  };
};