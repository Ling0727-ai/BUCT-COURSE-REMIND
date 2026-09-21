/**
 * 从 vue-cli 构建产物中提取某个 scoped 组件（按 data-v-* 作用域）的全部 CSS。
 * 用途：源文件样式块意外丢失时，从 dist CSS 精确恢复原始样式。
 *
 * 用法：node scripts/extract-scoped-css.js <dist.css> <data-v-hash>
 */
const fs = require('fs')

const [, , cssPath, hash] = process.argv
if (!cssPath || !hash) {
  console.error('用法: node scripts/extract-scoped-css.js <dist.css> <data-v-hash>')
  process.exit(2)
}

const css = fs.readFileSync(cssPath, 'utf8')

// 逐条扫描顶层规则（含 @media 等嵌套块）
function walk(source, collect) {
  let i = 0
  while (i < source.length) {
    const braceIndex = source.indexOf('{', i)
    if (braceIndex === -1) break

    const selector = source.slice(i, braceIndex).trim()

    // 找到匹配的右括号
    let depth = 0
    let j = braceIndex
    for (; j < source.length; j++) {
      if (source[j] === '{') depth++
      else if (source[j] === '}') {
        depth--
        if (depth === 0) break
      }
    }

    const body = source.slice(braceIndex + 1, j)

    if (selector.startsWith('@')) {
      walk(body, collect)
    } else if (selector.includes(hash)) {
      collect(selector, body)
    }

    i = j + 1
  }
}

const rules = []
walk(css, (selector, body) => {
  rules.push(`${selector} {${body}}`)
})

console.log(rules.join('\n\n'))
console.error(`[extract-scoped-css] ${rules.length} 条规则, hash=${hash}`)
