/**
 * 快速校验 SFC：解析 + 编译 script/template/style。
 * vue-cli 的 thread-loader 会把真实语法错误吞成
 * "Cannot read properties of null (reading 'content')"，用这个脚本能看到原始报错。
 *
 * 用法：node scripts/check-sfc.js src/pages/Home/Home.vue [更多文件...]
 */
const fs = require('fs')
const sfc = require('@vue/compiler-sfc')

const files = process.argv.slice(2)
if (files.length === 0) {
  console.error('用法: node scripts/check-sfc.js <file.vue> [...]')
  process.exit(2)
}

let failed = 0

for (const file of files) {
  const source = fs.readFileSync(file, 'utf8')
  const { descriptor, errors } = sfc.parse(source, { filename: file })

  const problems = []
  for (const e of errors) {
    problems.push(e.message)
  }

  try {
    sfc.compileScript(descriptor, { id: 'check' })
  } catch (err) {
    problems.push(`script: ${err.message.split('\n')[0]}`)
  }

  if (descriptor.template) {
    try {
      const tpl = sfc.compileTemplate({
        source: descriptor.template.content,
        filename: file,
        id: 'check'
      })
      for (const e of tpl.errors) {
        problems.push(`template: ${typeof e === 'string' ? e : e.message}`)
      }
    } catch (err) {
      problems.push(`template: ${err.message}`)
    }
  }

  for (const style of descriptor.styles) {
    try {
      sfc.compileStyle({
        source: style.content,
        filename: file,
        id: 'check',
        scoped: style.scoped
      })
    } catch (err) {
      problems.push(`style: ${err.message}`)
    }
  }

  if (problems.length === 0) {
    console.log(`OK   ${file}`)
  } else {
    failed += 1
    console.log(`FAIL ${file}`)
    for (const p of problems) {
      console.log(`       ${p}`)
    }
  }
}

process.exit(failed === 0 ? 0 : 1)
