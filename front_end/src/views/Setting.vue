<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="toChat()" class="one">聊天框</li>
        <li @click="manageRoles()" class="two">角色管理</li>
        <li @click="createRoles()" class="three">新建角色</li>
        <li class="four">设置</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSetting">设置</div>
      <div class="settingTop active">个人信息</div>
      <div @click="changePsd()" class="settingTop">修改密码</div>
      <div @click="toFeedback()" class="settingTop">提交反馈</div>
      <!-- <div class="back">返回</div> -->
    </div>
    <div class="right">
      <div v-if="noModify" class="display">
          <img :src="file_show1" alt="">
          <!-- <div>头像</div> -->
          <br>
          <span class="email">邮箱： {{ mail_account }}</span>
          <span class="nickname">昵称： {{ nickname_show }}</span>
          <br>
          <span class="sex">性别： {{ sex_show }}</span>
          <br>
          <span class="vip">
            <span v-show="isVip">VIP ： 您已经是VIP用户，剩余<strong>{{ vipDays }}</strong>天，继续</span><span @click="recharge()" v-show="isVip" class="recharge">充值</span>
            <span v-show="!isVip">VIP ： 您还不是VIP用户，快去</span><span @click="recharge()" v-show="!isVip" class="recharge">升级会员</span><span v-show="!isVip">吧</span>
          </span>
          <span v-show="isCloseShow" class="isClose">自动关闭广告<strong>已开启</strong></span>
          <span v-show="!isCloseShow" class="isClose">自动关闭广告<strong>未开启</strong></span>
          <div @click="edit()" class="edit">编辑</div>
      </div>
      <div v-else class="modifying">
        <input ref="fileInput" type="file" style="display: none" @change="handleFileChange">
        <div @click="triggerFileInput()">
          <img :src="file_show2" alt="">
        </div>
        <br>
        <span class="email">邮箱： {{ mail_account }}</span>
        <div class="nickname">
          <span>昵称： </span><input v-model="nickname" type="text" placeholder="请输入您的昵称"> <span>（昵称不能为空）</span>
        </div>
        <br>
        <div class="sex">
          <span>性别： </span><label for="man"><input v-model="sex" type="radio" name="gender" value="男" id="man"> 男 </label><label for="woman"><input v-model="sex" type="radio" name="gender" value="女" id="woman"> 女</label>
        </div>
        <label v-if="isVip" class="closeAdvertisement"><input v-model="isClose" type="checkbox"> 自动关闭广告</label>
        <label v-else @click="noVip()" class="closeAdvertisement"><input type="checkbox" disabled> 自动关闭广告</label>
        <div @click="exitEdit()" class="edit">退出编辑</div>
        <div @click="chessEdit()" class="chess">确定</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'SettingInfo',
  data () {
    return {
      noModify: true,
      user_id: this.$route.query.user_id,
      mail_account: '',
      nickname_show: '',
      nickname: '',
      sex_show: '',
      sex: '',
      file_show1: null, // 初始展示
      file_show2: null, // 编辑展示
      file_get: null, // 上传的图片
      vipDays: 30, //剩余VIP天数
      isVip: false, // true为VIP用户
      isClose: false, // true为自动关闭广告开启
      isCloseShow: false, // 展示时确认关闭广告是否开启
      is_limit: false, // true表示该用户目前处于被限制登录状态
    }
  },

  created () {
    document.title = '设置-chataaa'
    this.getInfo()
  },

  methods: {
    async getInfo () {
      const res1 = await axios.get('http://8.134.178.190:5000/user/information/get', {
        params: {
          user_id: this.user_id
        }
      })
      if (res1.data.code === '400') {
        alert('操作失败')
        return
      }
      this.mail_account = res1.data.mail_account
      this.nickname_show = res1.data.nickname,
      this.nickname = res1.data.nickname,
      this.sex_show = res1.data.sex
      this.sex = res1.data.sex
      this.vipDays = res1.data.vip_time
      this.isCloseShow = res1.data.advertise_state
      this.isClose = res1.data.advertise_state
      if (this.vipDays > 0) {
        this.isVip = true
      }
      const res2 = await axios.get('http://8.134.178.190:5000/user/information/get_head_portrait', {
        params: {
          user_id: this.user_id
        },
        responseType: 'blob'
      })
      if (res2.data.code === '400') {
        alert('操作失败')
        return
      }
      const imgUrl = URL.createObjectURL(res2.data)
      this.file_show1 = imgUrl

      const res3 = await axios.get('http://8.134.178.190:5000/user/get_vip_state', {
        params: {
          user_id: this.user_id
        }
      })
      if (res3.data.code === '400') {
        alert('获取vip身份失败')
        return
      }
      this.isVip = res3.data.state

      const res4 = await axios.get('http://8.134.178.190:5000/user/is_limit_login', {
        params: {
          user_id: this.user_id
        }
      })
      if (res4.data.code === '400') {
        alert('信息获取失败')
        return
      }
      this.is_limit = res4.data.is_limit
      if (this.is_limit === true) {
        alert('您已被限制登录')
        this.exit()
      }
    },
    triggerFileInput () {
      this.$refs.fileInput.click()
    },
    handleFileChange (event) {
      this.file_get = event.target.files[0]
      this.file_show2 = URL.createObjectURL(this.file_get)
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
    recharge () {
      this.$router.push({
        path: '/recharge',
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
    edit () {
      this.noModify = false
      this.file_show2 = this.file_show1
      this.isClose = this.isCloseShow
      this.nickname = this.nickname_show
      this.sex = this.sex_show
      // console.log(this.file_get)
    },
    noVip () {
      alert('“自动关闭广告”功能仅VIP用户可用')
    },
    exitEdit () {
      this.noModify = true
      this.file_show2 = this.file_show1
      this.isClose = this.isCloseShow
      this.nickname = this.nickname_show
      this.sex = this.sex_show
    },
    async chessEdit () {
      if (this.nickname.trim() === '') {
        alert('昵称不能为空！')
        return
      }
      this.noModify = true
      const res1 = await axios.post('http://8.134.178.190:5000/user/information/set', {
        user_id: this.user_id,
        nickname: this.nickname,
        sex: this.sex,
        advertise_state: this.isClose
      })
      if (res1.data.code === '400') {
        alert('操作失败')
        return
      }
      if (this.file_get !== null) {
        let file = new FormData()
        file.append('file', this.file_get)
        file.append('user_id', this.user_id)
        const res2 = await axios.post('http://8.134.178.190:5000/user/information/change_headportrait', file
        // {
        //   headers: {
        //     'Content-Type': 'multipart/form-data',
        //   },
        // }
        )
        if (res2.data.code === '400') {
          alert('头像上传失败')
          return
        }
        this.file_show1 = this.file_show2
      }
      this.isCloseShow = this.isClose
      this.nickname_show = this.nickname
      this.sex_show = this.sex
    },
    changePsd () {
      this.$router.push({
        path: '/changePassword',
        query: {
          user_id: this.user_id
        }
      })
    }
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

  .right {
    width: 1250px;
    background-color: #F2F5F8;
  }

  .right img{
    margin-top: 20px;
    width: 200px;
    height: 200px;
    border-radius: 50%;
  }

  .modifying img {
    cursor: pointer;
  }

  .modifying img:hover {
    opacity: 0.5;
  }

  .right .display {
    position: relative;
    text-align: center;
    font-size: 20px;
  }

  .email {
    position: absolute;
    top: 250px;
    left: 500px;
  }

  .nickname {
    position: absolute;
    top: 310px;
    left: 500px;
  }

  .sex {
    position: absolute;
    top: 370px;
    left: 500px;
  }

  .closeAdvertisement {
    position: absolute;
    top: 430px;
    left: 500px;
  }

  .display .vip {
    position: absolute;
    top: 430px;
    left: 500px;
  }

  .display .vip .recharge {
    color: #1990FF;
    font-weight: 700;
    cursor: pointer;
  }

  .display .vip .recharge:hover {
    font-size: 22px;
    transition: 0.2s;
  }

  .display .isClose {
    position: absolute;
    top: 490px;
    left: 500px;
  }

  .edit {
    position: absolute;
    top: 20px;
    left: 20px;
    width: 100px;
    height: 50px;
    border-radius: 6px;
    border: 2px solid #D6ECFF;
    line-height: 50px;
  }

  .edit:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }

  .modifying {
    position: relative;
    text-align: center;
    font-size: 20px;
  }

  .nickname input {
    width: 230px;
    height: 30px;
    font-size: 20px;
  }

  .chess {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 100px;
    height: 50px;
    border-radius: 6px;
    border: 2px solid #D6ECFF;
    line-height: 50px;
  }

  .chess:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }
</style>