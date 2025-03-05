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
      <div @click="setting()" class="settingTop active">个人信息</div>
      <div @click="changePsd()" class="settingTop">修改密码</div>
      <div @click="toFeedback()" class="settingTop">提交反馈</div>
    </div>
    <div class="right">
      <div @click="setting()" class="iconfont icon-chexiao"></div>
      <div class="out">
        <div class="iconfont icon-huangguan"> &nbsp;&nbsp;&nbsp;升级会员 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;30次/小时</div>
        <div @click="month()" class="month">
          <div class="time">包月</div>
          <div class="price">30元/月</div>
          <div class="iconfont icon-huiyuanhuangguanguanjun-xianxing"></div>
        </div>
        <div @click="quarter()" class="quarter">
          <div class="time">包季</div>
          <div class="price">80元/季</div>
          <div class="iconfont icon-huiyuanhuangguanguanjun-xianxing"></div>
        </div>
        <div @click="year()" class="year">
          <div class="time">包年</div>
          <div class="price">300元/年</div>
          <div class="iconfont icon-huiyuanhuangguanguanjun-xianxing"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'RechargeVip',
  data () {
    return {
      user_id: this.$route.query.user_id,
      is_limit: false, // true表示该用户目前处于被限制登录状态
      isVip: false // true为VIP
    }
  },

  async created () {
    document.title = '充值VIP-chataaa'
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
    async month () {
      const isConfirmed = window.confirm('确定要支付吗？')
      if (isConfirmed) {
        const res = await axios.post('http://8.134.178.190:5000/user/top_up', {
          user_id: this.user_id,
          type: '1'
        })
        if (res.data.code === '200') {
          alert('支付成功！')
        } else {
          alert('充值失败！')
        }
      } else {
        alert('支付被取消！')
      }
    },
    async quarter () {
      const isConfirmed = window.confirm('确定要支付吗？')
      if (isConfirmed) {
        const res = await axios.post('http://8.134.178.190:5000/user/top_up', {
          user_id: this.user_id,
          type: '2'
        })
        if (res.data.code === '200') {
          alert('支付成功！')
        } else {
          alert('充值失败！')
        }
      } else {
        alert('支付被取消！')
      }
    },
    async year () {
      const isConfirmed = window.confirm('确定要支付吗？')
      if (isConfirmed) {
        const res = await axios.post('http://8.134.178.190:5000/user/top_up', {
          user_id: this.user_id,
          type: '3'
        })
        if (res.data.code === '200') {
          alert('支付成功！')
        } else {
          alert('充值失败！')
        }
      } else {
        alert('支付被取消！')
      }
    },
    cancel () {
      this.isShowCode = false
    },
    changePsd () {
      this.$router.push({
        path: '/changePassword',
        query: {
          user_id: this.user_id
        }
      })
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
    async manageRoles() {
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
    async createRoles () {
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
    display: flex;
    position: relative;
    width: 1250px;
    background-color: #F2F5F8;
    justify-content: center;
    align-items: center;

  }

  .right .icon-chexiao {
    position: absolute;
    left: 40px;
    top: 10px;
    font-size: 30px;
    cursor: pointer;
  }

  .right .icon-chexiao:hover {
    font-size: 32px;
    transition: 0.2s;
  }

  .right .out {
    position: relative;
    width: 550px;
    height: 700px;
    background-color: #fff;
    border-radius: 30px;
  }

  .right .icon-huangguan {
    position: absolute;
    top: 20px;
    left: 30px;
    font-size: 25px;
    color: #1990FF;
    font-weight: 700;
  }

  .right .month {
    position: relative;
    width: 500px;
    height: 180px;
    color: #ff82be;
    background: linear-gradient(to bottom, #ffb9e5, #fff3f5);
    margin: 0 auto;
    margin-top: 70px;
    margin-bottom: 30px;
    border-radius: 15px;
    padding-top: 30px;
  }

  .right .month:hover {
    cursor: pointer;
    width: 510px;
    height: 190px;
    background: linear-gradient(to bottom, #ffb9e5, #ffb9e5);
    transition: 0.6s;
  }

  .right .quarter {
    position: relative;
    width: 500px;
    height: 180px;
    color: #1c97e1;
    background: linear-gradient(to bottom, #8fd5f4, #eef9fa);
    margin: 0 auto;
    margin-bottom: 30px;
    border-radius: 15px;
    padding-top: 30px;
  }

  .right .quarter:hover {
    cursor: pointer;
    width: 510px;
    height: 190px;
    background: linear-gradient(to bottom, #8fd5f4, #8fd5f4);
    transition: 0.6s;
  }

  .right .year {
    position: relative;
    width: 500px;
    height: 180px;
    color: #E08870;
    background: linear-gradient(to bottom, #514d63, #adabb0);
    margin: 0 auto;
    border-radius: 15px;
    padding-top: 30px;
  }

  .right .year:hover {
    cursor: pointer;
    width: 510px;
    height: 190px;
    background: linear-gradient(to bottom, #514d63, #514d63);
    transition: 0.6s;
  }

  .right .time {
    font-size: 25px;
    font-weight: 700;
    margin-left: 60px;
    margin-bottom: 30px;
  }

  .right .price {
    font-size: 25px;
    font-weight: 700;
    margin-left: 60px;
  }

  .right .icon-huiyuanhuangguanguanjun-xianxing {
    position: absolute;
    right: 100px;
    top: 0;
    font-size: 100px;
  }

  .right .showCode {
    width: 600px;
    height: 610px;
    background-color: #daeeff;
    position: absolute;
    top: 84px;
    border-radius: 10px;

  }

  .showCode img {
    position: absolute;
    width: 400px;
    height: 400px;
    top: 70px;
    left: 100px;
  }

  .showCode .cancel {
    position: absolute;
    width: 400px;
    height: 50px;
    top: 480px;
    left: 100px;
    background-color: #fff;
    line-height: 50px;
    text-align: center;
    cursor: pointer;
    font-size: 20px;
  }

</style>