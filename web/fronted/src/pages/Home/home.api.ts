import {http} from '@/api/http';
import {
    AssignmentRaw,
    AssignmentsResponse,
    CompletedAssignmentsResponse,
    RecycleBinResponse,
    ReminderConfig,
    Todo,
    TodosResponse,
    User
} from './home.data';

// Auth
export const getUserInfo = () => http.get<User>('/auth/user-info');
export const logout = () => http.post('/auth/logout', {});

// Assignments
export const getAssignments = () => http.get<AssignmentsResponse | AssignmentRaw[]>('/assignments/standard');
export const getCompletedAssignments = () => http.get<CompletedAssignmentsResponse>('/assignments/completed');
export const getDeletedAssignments = () => http.get<AssignmentRaw[]>('/assignments/deleted');
export const markAssignmentCompleted = (id: string) => http.post(`/assignments/${id}/complete`, {});
export const undoAssignmentCompleted = (id: string) => http.post(`/assignments/${id}/uncomplete`, {});
export const deleteAssignment = (id: string) => http.post(`/assignments/${id}/delete`, {});
export const restoreAssignment = (id: string) => http.post(`/assignments/${id}/restore`, {});
export const permanentDeleteAssignment = (id: string) => http.post(`/recycle-bin/delete/${id}`, {}); // Check endpoint
export const setAssignmentReminder = (id: string, config: ReminderConfig) => http.post(`/assignments/${id}/remind`, {reminderConfig: config});

// Todos
export const getTodos = () => http.get<Todo[] | TodosResponse>('/todos/');
export const addTodo = (todo: Partial<Todo>) => http.post('/todos/', todo);
export const deleteTodo = (id: string) => http.post(`/todos/${id}/delete`, {});
export const markTodoCompleted = (id: string) => http.post(`/todos/${id}/complete`, {});
export const undoTodoCompleted = (id: string) => http.post(`/todos/${id}/uncomplete`, {});
export const setTodoReminder = (id: string, config: ReminderConfig) => http.post(`/todos/${id}/remind`, {reminderConfig: config});

// Recycle Bin
export const getRecycleBinItems = () => http.get<RecycleBinResponse>('/recycle-bin/list');
export const restoreAllAssignments = () => http.post('/recycle-bin/restore-all', {});
export const permanentDeleteAll = () => http.post('/recycle-bin/empty', {});

// Blacklist
export const addToBlacklist = (subject: string) => http.post('/blacklist/add', {subject});

