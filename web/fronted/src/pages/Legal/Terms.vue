<template>
  <div class="legal-container">
    <div class="legal-card">
      <h1>服务条款</h1>
      <p class="update-time">更新日期：2025-11-16</p>

      <section>
        <h2>一、总则</h2>
        <p>
          欢迎使用“作业管理系统”（以下简称“本服务”）。本服务条款（以下简称“本条款”）系您与本服务提供方之间就您使用本服务所订立的法律协议。请您在注册、登录或使用本服务前仔细阅读并充分理解本条款的全部内容。一旦您注册或使用本服务，即视为您已阅读、理解并同意受本条款约束。</p>
      </section>

      <section>
        <h2>二、账户注册与使用</h2>
        <ol>
          <li>您应当使用具有合法来源的邮箱、用户名等信息进行注册，并保证所提交信息的真实性、准确性和完整性。</li>
          <li>
            您���妥善保管账户��密码信息，并对通过您的账户所进行的一切操作承担法律责任。因您保管不善导致的损失由您自行承担。
          </li>
          <li>如您发现账户存在异常登录或安全漏洞，应立即通知我们并采取必要的保护措施。</li>
        </ol>
      </section>

      <section>
        <h2>三、服务说明</h2>
        <ol>
          <li>
            本服务旨在提供学习任务、作业和测试的记录、提醒与管理功能，可能通过您授权的方式访问第三方系统以实现自动化数据同步。
          </li>
          <li>
            您理解并同意，因网络、设备、第三方系统变更或不可抗力等原因导致的服务中断、延迟或数据差异，本服务不承担由此产生的直接或间接损失。
          </li>
          <li>我们将努力提升服务稳定性与准确性，但无法保证所有提醒均能在任何情况下按时送达。</li>
        </ol>
      </section>

      <section>
        <h2>四、用户行为规范</h2>
        <ol>
          <li>您不得利用本服务发布、传输、传播或存储任何违法违规、侵权、骚扰、诽谤、恐吓、淫秽或其他不当内容。</li>
          <li>您不得对本服务进行反向工程、反编译、抓包破解、恶意攻击、批量爬取或以其他方式扰乱服务秩序。</li>
          <li>未经授权，您不得以任何方式使用、复制、修改、传播或公开本服务的源代码、设计和数据。</li>
        </ol>
      </section>

      <section>
        <h2>��、数据与隐私</h2>
        <ol>
          <li>
            您在使用本服务过程中提交的账户信息、学习任务数据及授权的第三方系统凭据，将依据《隐私政策》进行收集、使用与保护。
          </li>
          <li>本服务将尽力保障您的数据安全，但无法完全排除黑客攻击、数据泄露、系统故障等安全风险。</li>
        </ol>
      </section>

      <section>
        <h2>六、责任限制与免责</h2>
        <ol>
          <li>
            本服务按“现状”提供，不包含针对特定目的之适用性、无病毒、无疏忽等任何明示或默示的保证。
          </li>
          <li>
            对于因不可抗力或我们无法控制的原因造成的服务中断或终止，我们不承担赔偿责任。
          </li>
          <li>
            任何情况下，我们对您承担的全部赔偿责任（如有），均不超过您在争议发生前12个月内向我们支付的服务费用总额（如有）。
          </li>
        </ol>
      </section>

      <section>
        <h2>七、条款修改</h2>
        <p>我们有权适时修改本条款，更新后的内容一旦公布即取代原条款。如您不同意新的条款内容，应立即停止使用本服务；继续使用的，视为接受修改后的条款。</p>
      </section>

      <section>
        <h2>八、争议解决</h2>
        <p>本条款的订立、执行和解释适用中华人民共和国法律。如双方发生争议，应通过友好协商解决；协商不成的，应提交至本服务提供方所在地有管辖权的人民法院诉讼解决。</p>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Terms'
}
</script>

<style scoped>
.legal-container {
  min-height: 100vh;
  background-color: #f9fafb;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.legal-card {
  background: white;
  width: 100%;
  max-width: 800px;
  padding: 48px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

h1 {
  font-size: 30px;
  font-weight: 800;
  color: #111827;
  text-align: center;
  margin-bottom: 8px;
}

.update-time {
  text-align: center;
  color: #6b7280;
  margin-bottom: 40px;
  font-size: 14px;
}

section {
  margin-bottom: 32px;
}

h2 {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 16px;
  border-left: 4px solid #3b82f6;
  padding-left: 12px;
}

p, li {
  color: #4b5563;
  line-height: 1.75;
  font-size: 15px;
  margin-bottom: 8px;
}

ol {
  padding-left: 20px;
  margin: 0;
}

li {
  margin-bottom: 8px;
}

@media (max-width: 640px) {
  .legal-card {
    padding: 24px;
  }
}
</style>

