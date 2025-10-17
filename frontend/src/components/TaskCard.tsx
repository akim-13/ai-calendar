import React, { useState } from 'react';
import axios from "axios"; // Make sure axios is imported
import { API_BASE_URL } from "../api";

interface TaskCardProps {
  taskID: number,
  title: string;
  priority: number; // backend provides number
  duration: number;
  deadline: string;
  description?: string;
  dropdown?: boolean;
  otherTasks?: string[];
  newFCEvent: any; // TODO: proper type
  setModalTypeLocked: (value: boolean) => void;
  setModalType: (value: string) => void;
  setIsModalOpen: (value: boolean) => void;
  fetchAll: () => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  taskID,
  title,
  priority,
  duration,
  deadline,
  description = '',
  dropdown = false,
  otherTasks = [],
  newFCEvent,
  setModalTypeLocked,
  setModalType,
  setIsModalOpen,
  fetchAll,

}) => {
  const [isChecked, setIsChecked] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCheckboxChange = async () => {
    if (!isChecked){
      console.log(title)
      console.log(taskID)
      try{
        await axios.put<{ message: string }>(`${API_BASE_URL}/complete_task/${taskID}`);
      }
      catch (error) {
      console.error("Error fetching tasks:", error);
      }
    }
    setIsChecked(!isChecked);
  };

  const handleEditClick = () => {
    newFCEvent.current = {
      id: "task-" + taskID.toString(),
      title: title,
      start: deadline,
      extendedProps: {
        type: 'task',
        description: description,
        priority: priority,
        duration: duration,
        isCompleted: isChecked,
      },
    };
    console.log(newFCEvent.current)
    setModalType('task');
    setIsModalOpen(true);
    setModalTypeLocked(true);
  };

  const priorityColor = priority >= 8 ? 'bg-red-600' :
                        priority >= 4 ? 'bg-orange-500' :
                        'bg-green-500';

  return (
    <div className="border p-4 rounded-lg w-full md:max-w-xs bg-gray-100 my-2">
      {/* Title & Buttons (Dropdown + Edit) */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className={`w-4 h-4 rounded ${priorityColor}`}></div>
          <h3 className="text-xl font-semibold text-black">{title}</h3>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleEditClick}
            className="bg-gray-100 text-black p-1 rounded"
          >
            ✏️
          </button>
          {dropdown && (description || otherTasks.length > 0) && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="bg-gray-100 text-black p-1 rounded"
            >
              {isExpanded ? '🔼' : '🔽'}
            </button>
          )}
        </div>
      </div>

      {/* Deadline */}
      <p className="text-black font-semibold">Deadline: {deadline}</p>

      {/* Duration */}
      <p className="text-black">Duration: {duration} minutes</p>

      {/* Checkbox */}
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleCheckboxChange}
        className="mr-2"
      />
      <label className="text-black"> Mark as Completed</label>

      {/* Description & Sub-tasks (only show when expanded) */}
      {dropdown && isExpanded && (
        <div className="mt-2 border-t pt-2">
          {description && <p className="text-black mt-2">{description}</p>}
          {otherTasks.length > 0 && (
            <ul className="mt-2">
              {otherTasks.map((task, index) => (
                <li key={index} className="text-black pl-4 list-disc">
                  {task}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskCard;
