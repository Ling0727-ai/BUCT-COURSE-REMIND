export type AssignmentType = '作业' | '测试' | '待办'
export type AssignmentStatus = 'completed' | 'urgent' | 'warning' | 'normal'

export interface Assignment {
  id: string
  title: string
  subject: string
  description?: string
  dueDate?: string
  completed: boolean
  type: AssignmentType
  url?: string
  publisher?: string
  priority?: string
  estimatedHours?: number
  completing?: boolean
  undoing?: boolean
  _todoId?: string
}

export interface AssignmentWithStatus extends Assignment {
  status: AssignmentStatus
}

export interface Todo {
  _id: string
  title: string
  description?: string
  due_date?: string
  completed: boolean
  priority?: string
  estimated_hours?: number
  timeInput?: string
  hours?: number
}

/** ReminderModal 提交的提醒配置，字段与后端 /remind 接口载荷一致。 */
export interface ReminderConfig {
  type: string
  /** 'now' 表示立即提醒。 */
  when?: string
  /** 相对小时数（配合 timing 使用）。 */
  hours?: number
  /** 'before' 截止前，'after' 从现在起。 */
  timing?: string
  /** 具体提醒时间（type 为 custom-datetime 时）。 */
  datetime?: string
}

/** 黑名单条目，对应 /api/blacklist 返回结构。 */
export interface BlacklistEntry {
  subject_id: string
  subject_name?: string
}

export interface User {
  id?: string | number
  username?: string
  email?: string
  is_admin?: boolean
}

export interface AssignmentDetailsRaw {
  task?: string
  deadline?: string
  details_content?: string
  url?: string
}

export interface AssignmentRaw {
  id: string
  title?: string
  subject?: string
  type?: string
  completed?: boolean
  deadline?: string
  details?: AssignmentDetailsRaw
  url?: string
}

export interface AssignmentsResponse {
  success?: boolean
  tasks?: AssignmentRaw[]
}

export interface CompletedAssignmentsResponse {
  completed_assignments?: string[]
}

export interface TodosResponse {
  success?: boolean
  data?: Todo[]
}

export interface RecycleBinItem {
  /** 作业用 task_id，待办用 _id */
  id: string
  title: string
  /** 显示用类型：作业 / 测试 / 待办 */
  type: string
  subject?: string
  content?: string
  dueDate?: string
  deletedAt?: string
  /** 决定调用哪一组恢复/永久删除接口 */
  source: 'assignment' | 'todo'
}

/** GET /assignments/deleted 的条目 */
export interface DeletedAssignmentRaw {
  task_id: string
  subject?: string
  title?: string
  deadline?: string
  details?: string
  url?: string
  type?: string
  delete_time?: string
}

export interface DeletedAssignmentsResponse {
  success?: boolean
  deleted_assignments?: DeletedAssignmentRaw[]
  count?: number
}

/** GET /todos/deleted 的条目（Todo 字段平铺 + todo_id） */
export interface DeletedTodoRaw {
  _id: string
  todo_id?: string
  title?: string
  description?: string
  due_date?: string
  delete_time?: string
}

export interface DeletedTodosResponse {
  success?: boolean
  deleted_todos?: DeletedTodoRaw[]
  count?: number
}

export interface RecycleBinResponse {
  success?: boolean
  items?: RecycleBinItem[]
}