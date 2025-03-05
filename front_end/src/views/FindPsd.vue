<template>
  <div class="first">
    <div class="second">
      <img src="../assets/login_computer.png" alt="">
      <h3 class="sysName">欢迎使用<br>ChatAAA</h3>
      <div class="text">
        <h3>重置密码</h3>
        <input v-model="mail_account" type="text" class="inp inp1" placeholder="请输入您的邮箱">
        <input v-model="code_input" type="text" class="inp inp2" placeholder="请输入验证码">
        <button @click="sendCode()"  :disabled="isWaiting" class="sendCode">{{ isWaiting ? `${remainingTime}s` : '发送验证码' }}</button>
        <input v-model="password" type="password" class="inp inp3" placeholder="请输入密码10-12位，必须包含字母和数字，不能有空格">
        <input v-model="password2" type="password" class="inp inp4" placeholder="请再次输入密码">
        <br>
        <button @click="chess()" class="chess">确定</button>
        <br>
        <div class="backToLogin" @click="back()">返回登录</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'FindPassword',
  data () {
    return {
      mail_account: '',
      mail_check: '', // 保存发送验证码的邮箱
      password:'',
      password2:'',
      code:'',
      code_input:'',
      validPassword: true,
      isWaiting: false, // 判断发送验证码按钮是否处于等待状态，false为没有处于等待状态，可点击
      remainingTime: 60 // 发送验证码后的时间限制，60秒
    }
  },

  created () {
    document.title = '找回密码-chataaa'
    if (localStorage.getItem('mail_check')) {
      this.mail_check = localStorage.getItem('mail_check')
      this.mail_account = this.mail_check
    }
    this.code = localStorage.getItem('code')
    const endTime = localStorage.getItem('endTime2') // 获取浏览器存储的发送验证码时间限制的结束时间
    if (endTime && endTime > Date.now()) { // 还未达到结束时间
      this.remainingTime = Math.ceil((endTime - Date.now()) / 1000) // 计算还有多少秒
      this.isWaiting = true
      this.startTimer() // 启动计时器
    }
  },

  methods: {
    checkPassword() {
      const regex = /^(?=.*[a-zA-Z])(?=.*\d)(?!.*\s).{10,12}$/;
      this.validPassword = regex.test(this.password);
    },
    async sendCode () {
      if (this.mail_account.trim() === '') {
        alert(`邮箱不能为空`)
        return
      }
      if (!this.isWaiting) { // 没有处于等待状态
        const res = await axios.post('http://8.134.178.190:5000/login_system/retrieve_verification_code', {
          mail_account: this.mail_account,
        })
        this.mail_check = res.data.mail_account
        localStorage.setItem('mail_check', this.mail_account)
        localStorage.setItem('code', res.data.verification_code)
        if (res.data.code === '400') {
          alert('发送验证码失败')
          return
        }
        if (res.data.code === '401') {
          alert(`该用户邮箱未注册`)
          return
        }
        if (res.data.code === '400') {
          alert(`验证码发送失败，请稍后重试`)
          return
        }
        this.code = res.data.verification_code

        const endTime = Date.now() + 60000 // 60秒后的时间戳
        localStorage.setItem('endTime2', endTime) // 存入浏览器
        //启动计时器
        this.isWaiting = true
        this.startTimer()
      }
    },
    startTimer () {
      const timer = setInterval(() => {
        if (this.remainingTime > 0) {
          this.isWaiting = true
          this.remainingTime--
        } else {
          this.isWaiting = false
          this.remainingTime = 60
          localStorage.removeItem('endTime2')
          clearInterval(timer)
        }
      }, 1000);
    },
    async chess () {
      this.checkPassword()
      if (this.mail_account.trim() === '') {
        alert('邮箱不能为空')
        return
      }
      if (this.code_input.trim() === '') {
        alert('验证码不能为空')
        return
      }
      if (this.password.trim() === '') {
        alert(`密码不能为空`)
        return
      }
      if (this.password2.trim() === '') {
        alert(`请再次输入确认密码`)
        return
      }
      if (this.mail_check !== this.mail_account) {
        alert(`修改密码的邮箱账号必须与获取验证码邮箱一致！`)
        console.log(this.mail_account)
        console.log(this.mail_check)
        return
      }
      if (this.code !== this.code_input) {
        alert(`验证码有误`)
        return
      } else 
      if (this.validPassword === false) {
        alert(`输入的密码不符合格式要求`)
        return
      } else if (this.password !== this.password2) {
        alert(`两次密码输入不一致`)
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/login_system/retrieve_password', {
        mail_account: this.mail_account,
        password: this.password
      })
      if (res.data.code === '400') {
          alert('操作失败')
          return
        }
      alert(`密码重置成功`)
      localStorage.removeItem('mail_check')
      localStorage.removeItem('code')
      this.mail_check = ''
      this.$router.push('/login_system')
    },
    back () {
      this.$router.push('/login_system')
      localStorage.removeItem('mail_check')
      localStorage.removeItem('code')
    }
  }
}
</script>

<style scoped>
.first {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 985px;
  background-image: url(../assets/login.jpg);
  background-size: cover;
}

.first .second {
  width: 1050px;
  height: 500px;
  position: relative;
  display: flex;
}

.second img {
  border-radius: 10px 0 0 10px;
  width: 600px;
  height: 500px;
  opacity: 0.5;
}

.second .sysName {
  position: absolute;
  left: 40px;
  top: 50px;
  font-size: 40px;
  color: #fff;
}

.second .text {
  position: relative;
  width: 450px;
  height: 500px;
  background-color: #fff;
  border-radius: 0 10px 10px 0;
}

.text h3 {
  text-align: center;
  padding: 40px 40px 70px 40px;
  color: #3A62D7;
  font-size: 30px;
}

.second .text .inp {
  display: inline-block;
  position: absolute;
  width: 340px;
  height: 30px;
  margin: 50px;
  padding: 5px;
  border: none;
  border-bottom: 1px solid #DCDCDC;
}

.inp:focus {
  outline: none;
}

.inp1 {
  position: absolute;
  left: 20px;
  top: 100px;
}

.inp2 {
  position: absolute;
  left: 20px;
  top: 145px;
}

.inp3 {
  position: absolute;
  left: 20px;
  top: 190px;
}

.inp4 {
  position: absolute;
  left: 20px;
  top: 235px;
}

.sendCode {
  position: absolute;
  width: 90px;
  height: 35px;
  background-color: #1990FF;
  color: #fff;
  font-size: 12px;
  border-radius: 30px;
  text-align: center;
  line-height: 35px;
  top: 190px;
  right: 40px;
  cursor: pointer;
}

.sendCode:hover {
  width: 93px;
  height: 37px;
  text-align: center;
  line-height: 37px;
  opacity: 0.7;
  transition: 0.2s;
}

.text .forget {
  position: absolute;
  right: 80px;
  top: 300px;
  font-size: 12px;
  color: #3A62D7;
  font-weight: 700;
  cursor: pointer;
}

.text .chess {
  position: absolute;
  display: block;
  width: 340px;
  height: 45px;
  background-color: #3A62D7;
  text-align: center;
  line-height: 45px;
  color: #fff;
  font-size: 16px;
  margin: 0 auto;
  top: 350px;
  left: 55px;
  cursor: pointer;
}

.text .chess:hover {
  border-radius: 10px;
  width: 345px;
  height: 50px;
  text-align: center;
  line-height: 50px;
  opacity: 0.7;
  transition: 0.2s;
}

.text .backToLogin {
  position: absolute;
  display: block;
  width: 340px;
  height: 45px;
  background-color: #3A62D7;
  text-align: center;
  line-height: 45px;
  color: #fff;
  font-size: 16px;
  margin: 0 auto;
  top: 420px;
  left: 55px;
  cursor: pointer;
}

.text .backToLogin:hover {
  border-radius: 10px;
  width: 345px;
  height: 50px;
  text-align: center;
  line-height: 50px;
  opacity: 0.7;
  transition: 0.2s;
}
</style>