<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="toChat()" class="one">聊天框</li>
        <li @click="manageRoles()" class="two">角色管理</li>
        <li @click="createRoles()" class="three">新建角色</li>
        <li @click="setting()" class="four">设置</li>
        <li @click="exit()" class="five">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSetting">设置</div>
      <div @click="setting()" class="settingTop">个人信息</div>
      <div @click="changePsd()" class="settingTop">修改密码</div>
      <div class="settingTop active">提交反馈</div>
    </div>
    <div class="right">
      <div class="rightTop">提交反馈</div>
      <textarea v-model="content" name="" id="" cols="30" rows="10" placeholder="请输入反馈内容"></textarea>
      <button @click="submit()" class="submit">提交</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'FeedBack',
  data () {
    return {
      user_id: this.$route.query.user_id,
      noModify: true,
      content: '', // 反馈内容
      is_limit: false, // true表示该用户目前处于被限制登录状态
      isVip: false // true为VIP
    }
  },

  async created () {
    document.title = '提交反馈-chataaa'
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
    async submit () {
      if (this.content.trim() === '') {
        alert('反馈内容不能为空')
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/user/feedback', {
        user_id: this.user_id,
        content: this.content
      })
      if (res.data.code === '200') {
        this.content = ''
        alert('提交成功！')
      }
      if (res.data.code === '400') {
        alert('提交失败')
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
    changePsd () {
      this.$router.push({
        path: '/changePassword',
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
  }
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

  .right {
    position: relative;
    width: 1250px;
    background-color: #F2F5F8;
  }

  .right .rightTop {
    /* width: 1250px; */
    height: 70px;
    border-bottom: 1px solid #BBB;
    font-size: 25px;
    line-height: 70px;
    text-align: center;
    font-weight: 700;
  }
  .right textarea {
    position: absolute;
    left: 120px;
    top: 140px;
    width: 900px;
    height: 450px;
    background-color: #f3f3f4;
    border-radius: 15px;
    padding: 10px;
    font-size: 18px;
    resize: none;
  }

  .right .submit {
    position: absolute;
    right: 120px;
    bottom: 70px;
    width: 75px;
    height: 35px;
    background-color: #94cbff;
    color: #fff;
    font-weight: 700;
    border: none;
    border-radius: 7px;
  }

  .right .submit:hover {
    width: 80px;
    height: 40px;
    cursor: pointer;
    opacity: 0.7;
    transition: 0.2s;
  }
</style>