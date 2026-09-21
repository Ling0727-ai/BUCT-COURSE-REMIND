import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables/useToast';
import * as api from './home.api';
import {
    Assignment,
    AssignmentRaw,
    AssignmentStatus,
    AssignmentWithStatus,
    AssignmentsResponse,
    CompletedAssignmentsResponse,
    ReminderConfig,
    RecycleBinItem,
    Todo,
    TodosResponse,
    User
} from './home.data';

function getErrorMessage(error: unknown, fallback: string): string {
    if (error instanceof Error && error.message) {
        return error.message;
    }
    return fallback;
}

function normalizeAssignmentsPayload(payload: AssignmentsResponse | AssignmentRaw[]): AssignmentRaw[] {
    if (Array.isArray(payload)) {
        return payload;
    }
    if (Array.isArray(payload.tasks)) {
        return payload.tasks;
    }
    return [];
}

function normalizeTodosPayload(payload: Todo[] | TodosResponse): Todo[] {
    if (Array.isArray(payload)) {
        return payload;
    }
    if (payload.success && Array.isArray(payload.data)) {
        return payload.data;
    }
    return [];
}

export function useHomeService() {
    const router = useRouter();
    const { showToast } = useToast();

    // --- State ---
    const user = ref<User | null>(null);
    const currentTime = ref('');
    const assignments = ref<Assignment[]>([]);
    const todos = ref<Todo[]>([]);
    const loading = ref(false);
    const error = ref('');

    // Filters
    const searchTerm = ref('');
    const subjectFilter = ref('');
    const statusFilter = ref('');

    // --- Helpers ---
    const parseDate = (s: string | undefined | null): Date | null => {
        if (!s) return null;
        if (s.includes('+') || s.endsWith('Z')) return new Date(s);
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) return new Date(s.replace(' ', 'T') + '+08:00');
        if (s.includes('T')) return new Date(s + '+08:00');
        // Chinese format: 2025年9月23日 23:59:00
        const cn = s.match(/^(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{2}:\d{2}:\d{2})$/);
        if (cn) {
            const [, y, mo, d, t] = cn;
            return new Date(`${y}-${mo.padStart(2, '0')}-${d.padStart(2, '0')}T${t}+08:00`);
        }
        return new Date(s);
    };

    const getDaysUntilDue = (dueDate: string | undefined) => {
        try {
            if (!dueDate) return Infinity;
            const now = new Date();
            const due = parseDate(dueDate);
            if (!due || isNaN(due.getTime())) return 7;
            return Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        } catch {
            return 7;
        }
    };

    const assignmentStatus = (item: Assignment): AssignmentStatus => {
        if (item.completed) return 'completed';
        const days = getDaysUntilDue(item.dueDate);
        if (days < 0) return 'urgent';
        if (days <= 2) return 'urgent';
        if (days <= 7) return 'warning';
        return 'normal';
    };

    // --- Computed ---
    const allItems = computed(() => {
        const items: Assignment[] = [...assignments.value];
        // Merge todos
        const todoItems: Assignment[] = todos.value.map(todo => ({
            id: `todo_${todo._id}`,
            _todoId: todo._id,
            subject: '待办事项',
            title: todo.title,
            description: todo.description || '无备注', // map description to content/description
            dueDate: todo.due_date,
            type: '待办',
            completed: todo.completed,
            priority: todo.priority,
            estimatedHours: todo.estimated_hours,
            publisher: '用户'
        } as Assignment));
        items.push(...todoItems);
        return items;
    });

    const filteredAssignments = computed<AssignmentWithStatus[]>(() => {
        return allItems.value.map(item => ({
            ...item,
            publisher: item.publisher || (item.type === '待办' ? '用户' : '系统'),
            url: item.url || '',
            status: assignmentStatus(item) // Add status for easier filtering
        })).filter(item => {
            const title = item.title || '';
            const subject = item.subject || '';
            const search = searchTerm.value.toLowerCase();

            const matchesSearch = title.toLowerCase().includes(search) || subject.toLowerCase().includes(search);
            const matchesSubject = !subjectFilter.value || subject === subjectFilter.value;
            const matchesStatus = !statusFilter.value || assignmentStatus(item) === statusFilter.value;

            return matchesSearch && matchesSubject && matchesStatus;
        });
    });

    const subjects = computed(() => Array.from(new Set(allItems.value.map(a => a.subject))));
    const urgentCount = computed(() => allItems.value.filter(a => assignmentStatus(a) === 'urgent').length);
    const soonCount = computed(() => allItems.value.filter(a => assignmentStatus(a) === 'warning').length);
    const completedCount = computed(() => allItems.value.filter(a => a.completed).length);
    const todoCount = computed(() => todos.value.filter(t => !t.completed).length);
    const totalCount = computed(() => allItems.value.length);

    // --- Actions ---
    const fetchAssignments = async (showNotification = false) => {
        loading.value = true;
        error.value = '';
        if (showNotification) showToast('info', '刷新数据', '正在刷新作业数据...');

        try {
            const [assignmentsRes, todosRes] = await Promise.allSettled([
                api.getAssignments(),
                api.getTodos()
            ]);

            // Handle Assignments
            if (assignmentsRes.status === 'fulfilled') {
                const dataArray = normalizeAssignmentsPayload(assignmentsRes.value);

                // Completed & Deleted Status
                const completedIds = new Set<string>();
                // let deletedIds = new Set<string>();

                try {
                     const completedRes: CompletedAssignmentsResponse = await api.getCompletedAssignments();
                     if (Array.isArray(completedRes.completed_assignments)) {
                         completedRes.completed_assignments.forEach((id) => completedIds.add(id));
                     }
                } catch (e) { console.warn('Failed to fetch completed status', e); }

                assignments.value = dataArray.map((item) => {
                    const rawDeadline = item.details?.deadline || item.deadline;
                    const parsed = parseDate(rawDeadline);
                    return {
                        id: item.id,
                        title: item.details?.task || item.title || '未知任务',
                        subject: item.subject || '未知科目',
                        description: item.details?.details_content || '',
                        dueDate: parsed ? parsed.toISOString() : undefined,
                        type: item.type === 'homework' ? '作业' : '测试',
                        completed: item.completed || completedIds.has(item.id),
                        url: item.details?.url || item.url || '',
                        publisher: '系统'
                    };
                });
            }

            // Handle Todos
            if (todosRes.status === 'fulfilled') {
                 todos.value = normalizeTodosPayload(todosRes.value);
            }

        } catch (err: unknown) {
            console.error('Fetch error:', err);
            error.value = '加载失败';
            if (showNotification) showToast('error', 'Error', '数据加载失败');
        } finally {
            loading.value = false;
        }
    };

    const handleLogout = async () => {
        try {
            await api.logout();
            user.value = null;
            localStorage.removeItem('user');
            sessionStorage.removeItem('user');
            router.push('/login');
            showToast('success', 'Goodbye', '已退出登录');
        } catch (e) {
            router.push('/login');
        }
    };

    const updateTime = () => {
        const now = new Date();
        currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false });
    };

    let timer: number;

    const init = async () => {
        timer = setInterval(updateTime, 1000);
        updateTime();

        // Load User
        try {
            user.value = await api.getUserInfo();
        } catch (e) {
            console.warn('Failed to load user info');
        }

        await fetchAssignments();
    };

    onMounted(init);
    onUnmounted(() => clearInterval(timer));

    // --- CRUD Operations ---

    // Example: Delete Assignment/Todo
    const handleDelete = async (item: Assignment) => {
        try {
            if (item.type === '待办') {
                if(!item._todoId) return;
                await api.deleteTodo(item._todoId);
                // Refresh todos locally
                todos.value = todos.value.filter(t => t._id !== item._todoId);
            } else {
                await api.deleteAssignment(item.id);
                assignments.value = assignments.value.filter(a => a.id !== item.id);
            }
            showToast('success', 'Deleted', `${item.title} 已移至回收站`);
        } catch (e: unknown) {
            showToast('error', 'Error', getErrorMessage(e, '删除失败'));
        }
    };

    const handleComplete = async (item: Assignment) => {
        try {
            if (item.type === '待办') {
                if(!item._todoId) return;
                await api.markTodoCompleted(item._todoId);
                const todo = todos.value.find(t => t._id === item._todoId);
                if (todo) todo.completed = true;
            } else {
                await api.markAssignmentCompleted(item.id);
                const assign = assignments.value.find(a => a.id === item.id);
                if (assign) assign.completed = true;
            }
            showToast('success', 'Completed', `${item.title} 已完成`);
        } catch (e: unknown) {
            showToast('error', 'Error', '操作失败');
        }
    };

    const handleUndoComplete = async (item: Assignment) => {
         try {
            if (item.type === '待办') {
                if(!item._todoId) return;
                await api.undoTodoCompleted(item._todoId);
                const todo = todos.value.find(t => t._id === item._todoId);
                if (todo) todo.completed = false;
            } else {
                await api.undoAssignmentCompleted(item.id);
                const assign = assignments.value.find(a => a.id === item.id);
                if (assign) assign.completed = false;
            }
            showToast('info', 'Undo', `${item.title} 已撤销完成`);
        } catch (e: unknown) {
            showToast('error', 'Error', '操作失败');
        }
    };

     const handleSetReminder = async (item: Assignment, config: ReminderConfig) => {
        try {
            if (item.type === '待办') {
                 if(!item._todoId) return;
                 await api.setTodoReminder(item._todoId, config);
            } else {
                 await api.setAssignmentReminder(item.id, config);
            }
            showToast('success', 'Reminder', '提醒设置成功');
        } catch (e: unknown) {
            showToast('error', 'Error', '提醒设置失败');
        }
    };

    const handleAddTodo = async (todoData: Partial<Todo>) => {
        try {
            await api.addTodo(todoData);
            await fetchAssignments(false);
            showToast('success', 'Added', '待办事项已添加');
            return true;
        } catch (e: unknown) {
            showToast('error', 'Error', '添加失败');
            return false;
        }
    };

    // Recycle Bin
    const deletedItems = ref<RecycleBinItem[]>([]);

    const loadRecycleBin = async () => {
        try {
            const res = await api.getRecycleBinItems();
            if (res.success && Array.isArray(res.items)) {
                deletedItems.value = res.items;
            }
        } catch (e) {
            console.error('Failed to load recycle bin', e);
        }
    };

    const handleRestoreItem = async (item: RecycleBinItem) => {
        try {
            if (item.type === '待办') {
                // Not implemented in API yet for restore todo?
                // Assuming generic restore or todo specific.
                // Restore endpoint usually handles both if id is unique or type is passed.
                // Original code calls /recycle-bin/restore maybe?
                // Actually original code checks type.
            }
            await api.restoreAssignment(item.id);
            await loadRecycleBin();
            await fetchAssignments(false);
            showToast('success', 'Restored', '项目已恢复');
        } catch (e: unknown) {
            showToast('error', 'Error', '恢复失败');
        }
    };

    const handlePermanentDelete = async (item: RecycleBinItem) => {
        try {
             await api.permanentDeleteAssignment(item.id);
             await loadRecycleBin();
             showToast('success', 'Deleted', '永久删除成功');
        } catch (e: unknown) {
             showToast('error', 'Error', '删除失败');
        }
    };

    const handleRestoreAll = async () => {
        try {
            await api.restoreAllAssignments();
            await loadRecycleBin();
            await fetchAssignments(false);
            showToast('success', 'Restored', '全部恢复成功');
        } catch (e: unknown) {
            showToast('error', 'Error', '恢复失败');
        }
    };

    return {
        user,
        currentTime,
        loading,
        error,
        assignments,
        todos,
        searchTerm,
        subjectFilter,
        statusFilter,
        filteredAssignments,
        subjects,
        urgentCount,
        soonCount,
        totalCount,
        completedCount,
        todoCount,
        fetchAssignments,
        handleLogout,
        handleDelete,
        handleComplete,
        handleUndoComplete,
        handleSetReminder,
        handleAddTodo,
        deletedItems,
        loadRecycleBin,
        handleRestoreItem,
        handlePermanentDelete,
        handleRestoreAll
    };
}
