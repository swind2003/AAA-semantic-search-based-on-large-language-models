<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="toChat()" class="one">聊天框</li>
        <li @click="manageRoles()" class="two">角色管理</li>
        <li @click="createRoles()" class="three">新建角色</li>
        <li @click="setting()" class="four">设置</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSetting">设置</div>
      <div @click="setting()" class="settingTop">个人信息</div>
      <div class="settingTop active">修改密码</div>
      <div @click="toFeedback()" class="settingTop">提交反馈</div>
      <!-- <div class="back">返回</div> -->
    </div>
    <div class="right">
      <div class="rightLeft">ChatAAA</div>
      <div class="rightRight">
        <h3>修改密码</h3>
        <input v-model="old_password" class="inp inp1" type="password" placeholder="请输入原密码">
        <input v-model="new_password" class="inp inp2" type="password" placeholder="请输入新密码10-12位，需包含字母和数字，不能有空格">
        <input v-model="new_password2" class="inp inp3" type="password" placeholder="请再次输入新密码">
        <div @click="chess()" class="chess">确认</div>
        <div @click="$router.back()" class="back">返回</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ChangePassword',
  data () {
    return {
      noModify: true,
      user_id: this.$route.query.user_id,
      old_password: '',
      new_password: '',
      new_password2: '',
      validPassword: true, // 判断密码格式是否符合规范
      isVip: false, // true为VIP
      is_limit: false, // true表示该用户目前处于被限制登录状态
    }
  },

  async created () {
    document.title = '修改密码-chataaa'
    const res = await axios.get('http://8.134.178.190:5000/user/get_vip_state', {
      params: {
        user_id: this.user_id
      }
    })
    if (res.data.code === '400') {
      alert('获取vip身份失败')
      return
    }
    this.isVip = res.data.state

    const res2 = await axios.get('http://8.134.178.190:5000/user/is_limit_login', {
        params: {
          user_id: this.user_id
        }
      })
      if (res2.data.code === '400') {
        alert('信息获取失败')
        return
      }
      this.is_limit = res2.data.is_limit
      if (this.is_limit === true) {
        alert('您已被限制登录')
        this.exit()
      }
  },
  

  methods: {
    checkPassword() {
      const regex = /^(?=.*[a-zA-Z])(?=.*\d)(?!.*\s).{10,12}$/;
      this.validPassword = regex.test(this.new_password);
    },
    async chess () {
      this.checkPassword()
      if (this.old_password.trim() === '') {
        alert(`请输入原密码`)
        return
      } else if (this.new_password.trim() === '') {
        alert(`请输入新密码`)
        return
      } else if (this.validPassword === false) {
        alert(`输入密码格式有误`)
        return
      }else if (this.new_password2.trim() === '') {
        alert(`请再次输入新密码确认`)
        return
      } else if (this.new_password !== this.new_password2) {
        alert(`两次密码输入不一致`)
        return
      }

      const res = await axios.post('http://8.134.178.190:5000/user/information/change', {
        user_id: this.user_id,
        old_password: this.old_password,
        new_password: this.new_password
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      if (res.data.code === '200') {
        alert(`密码修改成功`)
        // this.$router.push({
        //   path: '/setting',
        //   query: {
        //     user_id: this.user_id
        //   }
        // })
      } else if (res.data.code === '400') {
        alert(`修改失败`)
        return
      } else if (res.data.code === '401') {
        alert(`原密码输入错误`)
        return
      }
    },
    setting() {
      this.$router.push({
        path: '/setting',
        query: {
          user_id: this.user_id
        }
      })
    },
    toChat () {
      this.$router.push({
        path: '/chatInterface',
        query: {
          user_id: this.user_id
        }
      })
    },
    manageRoles() {
      if(this.isVip) {
        this.$router.push({
          path: '/ManageRoles',
          query: {
            user_id: this.user_id
          }
        })
      } else {
        alert('该功能为VIP用户专享，快去升级会员吧！')
      }
    },
    createRoles () {
      if (this.isVip) {
        this.$router.push({
          path: '/createRoles',
          query: {
            user_id: this.user_id
          }
        })
      } else {
        alert('该功能为VIP用户专享，快去升级会员吧！')
      }
    },
    toFeedback () {
      this.$router.push({
        path: '/feedback',
        query: {
          user_id: this.user_id
        }
      })
    },
    async exit () {
      const res = await axios.post('http://8.134.178.190:5000/login_system/log_out', {
        user_id: this.user_id
      })
      if (res.data.code === '400') {
        this.$message.error('退出登录失败');
        return
      }
      this.cookie.clearCookie('remember_token')
      this.cookie.clearCookie('session')
      this.cookie.clearCookie('user_id')
      this.$router.push('/login_system')
    },
  },
}
</script>

<style scoped>
  .wrapped {
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #465069;
    opacity: 0.9;
  }

  .left {
    width: 90px;
    height: 100%;
    background-color: #D6ECFF;
    border-radius: 10px 0 0 10px;
  }

  .leftText {
    position: relative;
    color: #9CBFFB;
    font-weight: 700;
    font-size: 18px;
    text-align: center;
  }

  .leftText li {
    width: 90px;
    height: 50px;
    line-height: 50px;
    border: 2px solid #9CBFFB;
    border-radius: 10px;
  }

  .leftText li:hover {
    background-color: #a0bff5;
    color: #1990FF;
    cursor: pointer;
  }

  .leftText .one {
    position: absolute;
    top: 90px;
  }

  .leftText .two {
    position: absolute;
    top: 210px;
  }

  .leftText .three {
    position: absolute;
    top: 330px;
  }

  .leftText .four {
    position: absolute;
    top: 450px;
    color: #1990FF;
  }

  .leftText .five {
    position: absolute;
    top: 570px;
  }

  .middle {
    position: relative;
    width: 200px;
    background-color: #F6FBFF;
    border: 1px solid #BBBBBB;
    font-size: 17px;
  }

  .middleSetting {
    padding: 5px 0 10px 20px;
    font-size: 20px;
  }

  .settingTop {
    text-align: center;
    padding-bottom: 12px;
  }

  .settingTop:hover {
    color: #1990FF;
    font-weight: 700;
    cursor: pointer;
  }

  .active {
    color: #1990FF;
    font-weight: 700;
  }

  .middle .back {
    width: 120px;
    position: absolute;
    height: 50px;
    /* background-color: pink; */
    text-align: center;
    line-height: 50px;
    bottom: 10px;
    left: 40px;
    border-radius: 6px;
    border: 2px solid #D6ECFF;
  }

  .back:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }

  .right {
    display: flex;
    width: 1250px;
    background-color: #D2D7EF;
    justify-content: center;
    align-items: center;
  }

  .rightLeft {
    width: 400px;
    height: 400px;
    background-color: #7F88BB;
    border-radius: 10px 0 0 10px;
    font-size: 60px;
    text-align: center;
    line-height: 400px;
    color: #93D2F3;
    font-weight: 700;
  }

  .rightRight {
    position: relative;
    width: 400px;
    height: 400px;
    background-color: #fff;
    border-radius: 0 10px 10px 0;
    text-align: center;
  }

  .right h3 {
    text-align: center;
    padding: 27px 40px 70px 40px;
    color: #3A62D7;
    font-size: 30px;
  }

  .right .inp {
    width: 350px;
    height: 40px;
    border: 1px solid #BBBBBB;
    border-radius: 15px;
    padding: 10px;
  }

  .right .inp1 {
    position: absolute;
    left: 30px;
    top: 100px;
  }

  .right .inp2 {
    position: absolute;
    left: 30px;
    top: 150px;
  }

  .right .inp3 {
    position: absolute;
    left: 30px;
    top: 200px;
  }
  
  .right .chess {
    position: absolute;
    display: block;
    width: 300px;
    height: 45px;
    background-color: #3291F8;
    text-align: center;
    line-height: 45px;
    color: #fff;
    font-size: 16px;
    margin: 0 auto;
    top: 260px;
    left: 50px;
    border-radius: 15px;
    cursor: pointer;
  }

  .right .back {
    position: absolute;
    display: block;
    width: 300px;
    height: 45px;
    background-color: #3291F8;
    text-align: center;
    line-height: 45px;
    color: #fff;
    font-size: 16px;
    margin: 0 auto;
    top: 325px;
    left: 50px;
    border-radius: 15px;
    cursor: pointer;
  }
</style>