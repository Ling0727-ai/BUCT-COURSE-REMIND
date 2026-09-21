/**
 * 日期解析工具。
 *
 * 后端返回的截止时间可能是不带时区信息的字符串（如 "2025-11-20 23:59:59"、
 * "2025-11-20T23:59:59" 或 "2025年11月20日 23:59:59"），这些应按北京时间
 * (UTC+8) 解释；带 Z 或 +08:00 的字符串则交给 Date 原生解析。
 */

const BEIJING_OFFSET = '+08:00'

const CN_DATE_RE = /^(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{2}:\d{2}:\d{2})$/

/** 把各种后端日期格式解析为 Date；无法解析时返回 null。 */
export function parseDueDate(value?: string | null): Date | null {
  if (!value) {
    return null
  }

  const text = value.trim()
  if (!text) {
    return null
  }

  // 已带时区信息，直接解析
  if (text.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(text)) {
    const parsed = new Date(text)
    return Number.isNaN(parsed.getTime()) ? null : parsed
  }

  // 2025年11月20日 23:59:59
  const cn = text.match(CN_DATE_RE)
  if (cn) {
    const [, year, month, day, time] = cn
    const parsed = new Date(
      `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${time}${BEIJING_OFFSET}`
    )
    return Number.isNaN(parsed.getTime()) ? null : parsed
  }

  // 2025-11-20 23:59:59 → 需要把空格换成 T
  const normalized = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?$/.test(text)
    ? text.replace(' ', 'T')
    : text

  const parsed = new Date(`${normalized}${BEIJING_OFFSET}`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

/** 距截止时间还有多少天（向上取整）；无效日期返回 null。 */
export function daysUntil(value?: string | null): number | null {
  const due = parseDueDate(value)
  if (!due) {
    return null
  }
  return Math.ceil((due.getTime() - Date.now()) / 86400000)
}

/** 格式化为 YYYY-MM-DDTHH:mm，供 datetime-local 输入框使用。 */
export function toDatetimeLocalValue(value?: string | null): string {
  const date = parseDueDate(value)
  if (!date) {
    return ''
  }

  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}`
}
