import { useState, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import axios from "axios";
import AchievementModal from "./AchievementModal";
import SettingsModal from "./SettingsModal";
import { StandaloneEvent, Task, TaskEvent } from "../App";
import { getFormData, sendAddOrEditRequest } from "./TaskEventModal";

const formatDate = (date: Date): string => {
    // Time zones/daylight saving time
    const adjusted = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return adjusted.toISOString().slice(0, 16);
};

// TODO: This is not clean code
function convEvent(event: any) {
    const startTime = event.start ? formatDate(event.start) : "";
    const endTime = event.end ? formatDate(event.end) : "";
    const extendedProps = event.extendedProps;

    const obj: any = {};
    obj.id = event.id
    obj.title = event.title || "";
    obj.start = startTime;
    obj.end = endTime;
    obj.extendedProps = extendedProps;

    return obj;
}

const Calendar: React.FC<any> = ({ standaloneEvents, taskEvents, tasks, setIsModalOpen, setModalTypeLocked, newFCEvent, initialExtendedProps, setModalType, fetchAll, setIsLoading }) => {
    const [isAchievementModalOpen, setIsAchievementModalOpen] = useState(false);
    const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
    const username = "joe";

    const handleEventClick = (info: any) => {
        newFCEvent.current = convEvent(info.event);

        setModalType(newFCEvent.current.extendedProps.type);
        setIsModalOpen(true);
        setModalTypeLocked(true);
        console.warn(JSON.parse(JSON.stringify(newFCEvent.current)))
    };

    // TODO: Duplication from TaskEventModal
    const handleEventChange = async (info: any) => {
        const convertedEvent = convEvent(info.event);
        const formData = getFormData(convertedEvent, info.event.extendedProps.type);
        formData.append("editID", info.event.id.split("-")[1]);

        setIsLoading(true);
        await sendAddOrEditRequest(formData, true, info.event.extendedProps.type);
        await fetchAll();
        setIsLoading(false);
    }

    let processedEvents = [
        ...taskEvents.map((event: TaskEvent) => ({
            id: "taskev-" + event.eventID.toString(),
            title: event.title,
            start: event.start,
            end: event.end,
            extendedProps: {
                type: "task_event",
            },
            color: "blue",  // Task events
        })),
        ...tasks.map((task: Task) => ({
            id: "task-" + task.taskID.toString(),
            title: task.title,
            start: task.deadline,
            // end: task.deadline,
            extendedProps: {
                type: "task",
                description: task.description,
                priority: task.priority,
                duration: task.duration,
                isCompleted: task.isCompleted,
            },
            color: "rgb(144,238,144)",  // Light green for tasks
            textColor: "black",
        })),
        ...standaloneEvents.map((event: StandaloneEvent) => ({
            id: "standalone-" + event.standaloneEventID.toString(),
            title: event.standaloneEventName,
            start: event.start,
            end: event.end,
            extendedProps: {
                type: "standalone_event",
                description: event.standaloneEventDescription
            },
            color: "rgb(255,99,132)",  // Red for standalone events
            textColor: "black",
        })),
    ]

    return (
        <div className="relative">
            <FullCalendar
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
                initialView={'timeGridWeek'}
                editable={true}
                selectable={true}
                height="auto"
                expandRows={true}
                contentHeight="auto"
                slotMinTime="00:00:00"
                slotMaxTime="24:00:00"
                slotDuration="01:00:00"
                slotLabelFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
                timeZone="local"
                headerToolbar={typeof window !== 'undefined' && window.innerWidth < 768 ? {
                    left: 'prev,next,today',
                    center: 'title',
                    right: '',
                } : {
                    left: 'prev,next,today,title',
                    center: '',
                    right: 'achievements,settings',
                }}
                titleFormat={{ month: "short", day: "numeric", year: "numeric" }}
                customButtons={{
                    achievements: {
                        text: "Achievements",
                        click: () => setIsAchievementModalOpen(true),
                    },
                    settings: {
                        text: "Settings",
                        click: () => setIsSettingsModalOpen(true),
                    },
                }}

                events={processedEvents}

                eventClick={handleEventClick}

                eventDrop={handleEventChange}
                eventResize={handleEventChange}
            />

            <AchievementModal
                isOpen={isAchievementModalOpen}
                onClose={() => setIsAchievementModalOpen(false)}
            />
            <SettingsModal
                open={isSettingsModalOpen}
                onClose={() => setIsSettingsModalOpen(false)}
             />
        </div>
    );
};

export default Calendar;
