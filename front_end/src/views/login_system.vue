<template>
  <div class="first">
    <div class="second">
      <img src="../assets/login_computer.png" alt="">
      <h3 class="sysName">欢迎使用<br>ChatAAA</h3>
      <div class="text">
        <h3>欢迎登录</h3>
        <input type="text" v-model="mail_account" class="inp inp1" placeholder="请输入邮箱账号">
        <input type="password" v-model="password" class="inp inp2" placeholder="请输入密码">
        <span class="error" v-show="isError">账号或密码有误</span>
        <div class="forget" @click="$router.push('/login_system/retrieve_password')">忘记密码</div>
        <br>
        <div class="login" @click="login">登录</div>
        <br>
        <div class="register" @click="$router.push('/login_system/register')">还没有账号？点击注册</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'LoginSystem',
  data () {
    return {
      isError: false, // 密码错误显示
      mail_account: '',
      password: '',
      advertise_state: false // 是否关闭广告
    }
  },

  created () {
    document.title = '登录-chataaa'
    this.cookie.clearCookie('remember_token')
    this.cookie.clearCookie('session')
    this.cookie.clearCookie('user_id')
  },

  methods: {
    async login () {
      const res = await axios.post('http://8.134.178.190:5000/login_system/log_in', {
        mail_account: this.mail_account,
        password: this.password
      })
      this.mail_account=''
      this.password=''
      if (res.data.code === '400') {
        this.$message.error('登陆失败');
        return
      }
      if (res.data.code === "400") {
        this.isError = true
      } else if (res.data.code === "401") {
        this.$message.error(`您已被限制登录，${res.data.restriction_time}天后解除限制`);
        // alert(`您已被限制登录，${res.data.restriction_time}天后解除限制`)
        return
      } else if (res.data.code === "200") {
        if (res.data.user_type_id === 3) {
          // let loginInfo = {
          //   remember_token:this.mail_account,
          //   session:"asfafsfsfsdfsdfsdfdsf",
          //   user_id: res.data.user_id
          // }
          // this.cookie.setCookie(loginInfo,7)
          this.$router.push({
            path: '/chatInterface',
            query: {
              user_id: res.data.user_id // 用户标识id
            }
          })
        } else if (res.data.user_type_id === 1) {
          // let loginInfo={
          //   remember_token:this.mail_account,
          //   session:"asfafsfsfsdfsdfsdfdsf",
          //   user_id: res.data.user_id
          // }
          // this.cookie.setCookie(loginInfo,7)
          this.$router.push({
            path: '/setInformation',
            query: {
              user_id: res.data.user_id
            }
          })
        } else if (res.data.user_type_id === 2) {
          // let loginInfo={
          //   remember_token:this.mail_account,
          //   session:"asfafsfsfsdfsdfsdfdsf",
          //   user_id: res.data.user_id
          // }
          // this.cookie.setCookie(loginInfo,7)
          this.$router.push({
            path: '/ChangeRole',
            query: {
              user_id: res.data.user_id
            }
          })
        } else if (res.data.user_type_id === 4) {
          // let loginInfo={
          //   remember_token:this.mail_account,
          //   session:"asfafsfsfsdfsdfsdfdsf",
          //   user_id: res.data.user_id
          // }
          // this.cookie.setCookie(loginInfo,7)
          // 假设 str 是你的字符串
          this.$router.push({
            path: '/chatInterface',
            query: {
              user_id: res.data.user_id, // 用户标识id
              advertise_state: res.data.advertise_state
            }
          })
        }
      }
    },

    // loginTest() {
    //   console.log('1');
    //   if(this.password&&this.mail_account){
          // let loginInfo={
          //   LoginName:this. mail_account,
          //   openId:"asfafsfsfsdfsdfsdfdsf"
          // }
    //       // 调用setCookie方法，同时传递需要存储的数据，保存天数
    //       this.cookie.setCookie(loginInfo,7)
    //       alert("登录成功")
    //       // 跳转到首页
    //       this.$router.push('/ChangeRole')
    //     }
    // }
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
  width: 300px;
  height: 30px;
  margin: 50px;
  padding: 5px;
  border: none;
  border-bottom: 1px solid #000;
}

.inp:focus {
  outline: none;
}

.inp1 {
  position: absolute;
  left: 20px;
  top: 130px;
}

.inp2 {
  position: absolute;
  left: 20px;
  top: 200px;
}

.text .error {
  position: absolute;
  color: red;
  font-size: 13px;
  top: 300px;
  left: 70px;
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

.text .forget:hover {
  font-size: 15px;
  transition: 0.2s;
}

.text .login {
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

.text .login:hover {
  border-radius: 10px;
  width: 345px;
  height: 50px;
  text-align: center;
  line-height: 50px;
  opacity: 0.7;
  transition: 0.2s;
}

.text .register {
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

.text .register:hover {
  border-radius: 10px;
  width: 345px;
  height: 50px;
  text-align: center;
  line-height: 50px;
  opacity: 0.7;
  transition: 0.2s;
}
</style>