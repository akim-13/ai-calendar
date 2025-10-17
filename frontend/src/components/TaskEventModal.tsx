import React, { useState, useRef } from "react";
import { Dialog, DialogTitle } from "@headlessui/react";
import {
  TitleInput,
  StartDateInput,
  EndDateInput,
  DurationInput,
  PrioritySelect,
  DescriptionInput,
  CompletedCheckbox,
  ModeToggleButton,
} from "./TaskEventInputs";
import axios from "axios";

import { API_BASE_URL } from "../api";

const HOST = API_BASE_URL

// interface ExtendedProps {
//   description: string;
//   duration: string;
//   priority: string;
//   isCompleted: boolean;
//   username?: string;
//   taskID?: string;
// }

interface FCEvent {
  id?: string;
  title: string;
  start: string;
  end: string;
//   extendedProps: ExtendedProps;
  extendedProps: any;
}

interface TaskEvent {
  start: string;
  end: string;
  taskID: string;
}

interface TaskEventModalProps {
  isModalOpen: boolean;
  setIsModalOpen: (value: boolean) => void;
  modalTypeLocked: boolean;
  newFCEvent: React.MutableRefObject<FCEvent>;
  modalType: string;
  setModalType: (value: string) => void;
  fetchAll: () => Promise<void>;
  setIsLoading: (value: boolean) => void;
}

export const getFormData = (currentFCEvent: FCEvent, modalType: string) => {
    const formData = new FormData();

    if (modalType === "task") {
        formData.append("title", currentFCEvent.title);
        formData.append("deadline", currentFCEvent.start);
        formData.append("description", currentFCEvent.extendedProps.description);
        formData.append("duration", currentFCEvent.extendedProps.duration);
        formData.append("priority", currentFCEvent.extendedProps.priority);
    } else if (modalType === "standalone_event") {
        formData.append("start", currentFCEvent.start);
        formData.append("end", currentFCEvent.end);
        formData.append("standaloneEventName", currentFCEvent.title);
        formData.append("standaloneEventDescription", currentFCEvent.extendedProps.description);
    } else {
        formData.append("start", currentFCEvent.start);
        formData.append("end", currentFCEvent.end);
    }

    return formData;
};

export const sendAddOrEditRequest = async (formData: FormData, editMode: boolean, modalType: string) => {
    const operation =
        (editMode
            ? ("edit_" + modalType)
            : ("add_" + modalType)
        );
    console.warn([...formData.entries()]);
    const response = await axios.post(`${HOST}/${operation}`, formData);
    console.log(`Add/edit request ${operation} sent successfully:`);
    for (const pair of formData.entries()) { console.log(`${pair[0]}: ${pair[1]}`); }
    return response;
};

const TaskEventModal: React.FC<TaskEventModalProps> = ({
    isModalOpen, setIsModalOpen,
    modalTypeLocked,
    newFCEvent,
    modalType, setModalType,
    fetchAll,
    setIsLoading
}) => {
    const [, forceUpdate] = useState(0);

    const handleInputChange = async (
      event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
    ) => {
        const { name, type } = event.target;
        const value = type === "checkbox" ? (event.target as HTMLInputElement).checked : event.target.value;

        const isMainProp = name === "title" || name === "start" || name === "end"

        if (isMainProp) {
            newFCEvent.current[name as keyof Pick<FCEvent, "title" | "start" | "end">] = value as string;
        } else {
            newFCEvent.current.extendedProps = {
                ...newFCEvent.current.extendedProps,
                [name]: value
            };
        }

        forceUpdate(x => x+1);

        const id = newFCEvent.current["id"] ?? -1;
        try {
            if (type === "checkbox" && (event.target as HTMLInputElement).checked) {
                await axios.put(`${HOST}/complete_task/${id}`);
                console.log(`Task "${id}" completed successfully`);
            } else {
                await axios.put(`${HOST}/incomplete_task/${id}`);
                console.log(`Task "${id}" uncompleted successfully`);
            }
        } catch (error) {
            console.error("Error completing a task", error);
        }
    };

    const handleDelete = async () => {
        const currentFCEvent = newFCEvent.current;
        if (!currentFCEvent.id) {
            console.log("Nothing to delete");
            return;
        }

        try {
            const numericId = currentFCEvent.id.split("-")[1];
            if (modalType === "task") {
                await axios.delete(`${HOST}/delete_events_from_task/${numericId}`);
                console.log(`Events of task "${numericId}" deleted successfully.`);
                await axios.delete(`${HOST}/delete_task/${numericId}`);
                console.log(`Task "${numericId}" deleted successfully.`);
            } else if (modalType === "standalone_event") {
                await axios.delete(`${HOST}/delete_standalone_event/${numericId}`);
                console.log(`Event "${numericId}" deleted successfully.`);
            } else if (modalType === "task_event") {
                await axios.delete(`${HOST}/delete_task_event/${numericId}`);
                console.log(`Task event "${numericId}" deleted successfully.`);
            }
        } catch (e) {
            console.error("Error deleting task or event", e);
        }

        setIsModalOpen(false);
        fetchAll();
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = getFormData(newFCEvent.current, modalType);

        let edit = false;
        if (newFCEvent.current.id) {
            edit = true;
            formData.append("editID", newFCEvent.current.id.split("-")[1]);
        }

        setIsLoading(true);
        await sendAddOrEditRequest(formData, edit, modalType);
        await fetchAll();
        setIsModalOpen(false);
        setIsLoading(false);
    };

    return (
      <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} className="fixed inset-0 flex z-[10000] items-center justify-center px-4">
        <div className="fixed bg-gray-200 p-4 md:p-6 rounded-lg shadow-lg w-full max-w-md min-h-[505px] flex flex-col">

          <DialogTitle className="text-lg font-bold text-black">
            {modalType === "task" ? "Manage Task" : "Manage Event"}
          </DialogTitle>

          {/* Toggle Mode Buttons */}
          {!modalTypeLocked && (
            <div className="flex space-x-4 mt-2">
                <ModeToggleButton mode="task" isActive={modalType === 'task'} setModalType={setModalType} />
                <ModeToggleButton mode="standalone_event" isActive={modalType !== 'task'} setModalType={setModalType} />
            </div>
          )}

          {/* Form */}
          <form role="form" onSubmit={handleSubmit} className="mt-4 flex-1 flex flex-col justify-between">

            {/* Shared Fields */}
            <TitleInput value={newFCEvent.current.title} onChange={handleInputChange} modalType={modalType} readonly={modalType === "task_event"} />
            <StartDateInput value={newFCEvent.current.start} onChange={handleInputChange} modalType={modalType} />

            {/* Specific Fields */}
            <div className="min-h-[150px]">
                {modalType === "task" ? (
                    <>
                        {/* Task-Specific Fields */}
                        <DurationInput value={newFCEvent.current.extendedProps.duration} onChange={handleInputChange} />
                        <PrioritySelect value={newFCEvent.current.extendedProps.priority} onChange={handleInputChange} />
                        <DescriptionInput value={newFCEvent.current.extendedProps.description} onChange={handleInputChange} />
                        <CompletedCheckbox checked={newFCEvent.current.extendedProps.isCompleted} onChange={handleInputChange} />
                    </>
                ) : (
                    <>
                        {/* Event-Specific Fields */}
                        <EndDateInput value={newFCEvent.current.end} onChange={handleInputChange} />
                        {modalType !== "task_event" && (
                            <DescriptionInput value={newFCEvent.current.extendedProps.description} onChange={handleInputChange} />
                        )}
                    </>
                )}
            </div>

            {/* Buttons */}
            <div className="flex flex-wrap justify-center gap-2">
                <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 bg-gray-300 text-black rounded-md hover:bg-gray-400"
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                    {newFCEvent.current.id ? "Update" : "Create"}
                </button>
                <button
                    type="button"
                    onClick={handleDelete}
                    className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                >
                    Delete
                </button>
            </div>
          </form>
        </div>
      </Dialog>
    );
};

export default TaskEventModal;
