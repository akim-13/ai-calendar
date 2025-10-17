import React, { useState, useEffect, useRef} from "react";
import axios from "axios"; // Make sure axios is imported
import Calendar from "./components/Calendar";
import TaskEventModal from "./components/TaskEventModal";
import TaskCard from "./components/TaskCard";
import InputPrompt from "./components/InputPrompt";
import SignIn from "./components/SignIn"; // Import the SignIn component
import "./styles/fullcalendar.css";
import LoadingOverlay from "./components/LoadingOverlay";
import { API_BASE_URL } from "./api";

export interface StandaloneEvent {
  standaloneEventName: string;
  standaloneEventID: number;
  eventBy: string | null;
  start: string;
  end: string;
  standaloneEventDescription: string;
  username: string;
}

export interface TaskEvent {
  start: string;
  end: string;
  eventID: string;
  title: string;
}

export interface Task {
  title: string;
  taskID: number;
  deadline: string;
  priority: number;
  duration: number;
  description: string;
  isCompleted: boolean;
  username: string;
}

const App: React.FC = () => {
  const [modalType, setModalType] = useState('task');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTypeLocked, setModalTypeLocked] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false); // Authentication state
  const username = "joe"; // TODO

  const [standaloneEvents, setStandaloneEvents] = useState<StandaloneEvent[]>([]);
  const [taskEvents, setTaskEvents] = useState<TaskEvent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
      fetchAll();
  }, []);

  const fetchStandaloneEvents = async () => {
      try {
          const standaloneEventsResponse = await axios.get(
              `${API_BASE_URL}/get_standalone_events/${username}`
          );
          setStandaloneEvents(standaloneEventsResponse.data.standalone_events);
      } catch (error) {
          console.error("Error fetching events:", error);
      }
  };

  const fetchTaskEvents = async () => {
      try {
          const eventsResponse = await axios.get(
              `${API_BASE_URL}/get_events_from_user/${username}`
          );
          setTaskEvents(eventsResponse.data.events);
      } catch (error) {
          console.error("Error fetching events:", error);
      }
  };

  const fetchTasks = async () => {
      try {
          const taskResponse = await axios.get(`${API_BASE_URL}/get_user_tasks/${username}`);
          setTasks(taskResponse.data.tasks)
      } catch (error) {
          console.error("Error fetching tasks:", error);
      }
  };

  const fetchAll = async () => {
    await Promise.all([
      fetchStandaloneEvents(),
      fetchTaskEvents(),
      fetchTasks(),
    ]);
  }


  const initialExtendedProps = {
    username: "joe",
    taskID: undefined,
    description: "",
    priority: 0,
    isCompleted: false,
    duration: undefined,
    events: undefined,
  };

  interface FCEvent {
    id?: string;
    title: string;
    start: string;
    end: string;
    extendedProps: any;
  }

  const newFCEvent = useRef<FCEvent>({
    title: "",
    start: "",
    end: "",
    extendedProps: { ...initialExtendedProps },
  });

  const handleSignIn = () => {
    setIsSignedIn(true); // Update authentication state once the user signs in
  };

  return (
    <div className="flex flex-col md:flex-row md:h-screen w-full">
      {/* Show SignIn component if not signed in */}
      {!isSignedIn ? (
        <SignIn onSignIn={handleSignIn} />
      ) : (
        <>
          {/* Task list sidebar (stacks on mobile) */}
          <div className="flex-none w-full md:w-[300px] p-4 md:border-r border-gray-300 order-2 md:order-1">
            {tasks.length > 0 ? (
              tasks.map((task) => (
                <TaskCard
                  key={task.taskID}
                  taskID={task.taskID}
                  title={task.title}
                  priority={task.priority} // Assuming priority is a number
                  duration={task.duration}
                  deadline={task.deadline}
                  description={task.description}
                  dropdown={true} // or false based on your needs
                  otherTasks={[
                  ]}

                  newFCEvent={newFCEvent}
                  setModalTypeLocked={setModalTypeLocked}
                  setModalType={setModalType}
                  setIsModalOpen={setIsModalOpen}
                  fetchAll={fetchAll}
                />
              ))
            ) : (
              <p>No tasks available</p> // Display a message when there are no tasks
            )}
          </div>

          {/* Main content (calendar + input) */}
          <div className="flex-grow flex flex-col p-4 md:p-6 order-1 md:order-2">
            {isModalOpen && (
              <TaskEventModal
                isModalOpen={isModalOpen}
                setIsModalOpen={setIsModalOpen}
                modalTypeLocked={modalTypeLocked}
                newFCEvent={newFCEvent}
                setModalType={setModalType}
                modalType={modalType}
                fetchAll={fetchAll}
                setIsLoading={setIsLoading}
              />
            )}

            <Calendar
              standaloneEvents={standaloneEvents}
              taskEvents={taskEvents}
              tasks={tasks}
              setIsModalOpen={setIsModalOpen}
              setModalTypeLocked={setModalTypeLocked}
              newFCEvent={newFCEvent}
              initialExtendedProps={initialExtendedProps}
              setModalType={setModalType}
              fetchAll={fetchAll}
              setIsLoading={setIsLoading}
            />

            <div className="pt-4">
              <InputPrompt
                setIsModalOpen={setIsModalOpen}
                setModalTypeLocked={setModalTypeLocked}
                initialExtendedProps={initialExtendedProps}
                newFCEvent={newFCEvent}
                setModalType={setModalType}
              />
            </div>
          </div>
        </>
      )}

      <LoadingOverlay isOpen={isLoading} />
    </div>
  );
};

export default App;
