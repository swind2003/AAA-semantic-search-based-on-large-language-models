<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="toChat()" class="one">聊天框</li>
        <li @click="manageRoles()" class="two">角色管理</li>
        <li class="three">新建角色</li>
        <li @click="setting()" class="four">设置</li>
        <li @click="exit()" class="five">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <div class="main">
        <div class="title">创建角色</div>
        <div class="prompt">提示词</div>
        <textarea v-model="prompt" name="" id="" cols="30" rows="10" placeholder="    我想要让你作为一位杰出的律师。您将在法律领域展现您的才能，为人们提供准确、明晰的法律建议。您可以选择专攻领域，如刑法、民法、商法等，但您的目标是成为一位擅长处理各类法律问题、具备卓越法律洞察力的律师。"></textarea>
        <input ref="pictureInput" type="file" style="display: none;" @change="handlePictureChange">
        <div class="head_text">角色头像：</div>
        <div v-show="!isModify" @click="triggerPictureInput()" class="head_picture">＋</div>
        <div v-show="isModify" @click="triggerPictureInput()" class="show_picture">
          <img :src="picture_show" alt="">
        </div>
        <div class="name">角色名称：</div>
        <input v-model="role_name" @input="name_input" type="text" placeholder="请输入角色名称" class="nameInput">
        <span class="name_length">{{ name_length }}/25</span>
        <div class="describe">角色描述：</div>
        <input v-model="description" @input="description_input" type="text" placeholder="请输入对创建角色的描述" class="describeInput">
        <span class="description_length">{{ description_length }}/25</span>
        <div class="divergence">发散能力：</div>
        <select name="" id="" class="divergenceSelect">
          <option selected disabled>1.0</option>
        </select>
        <div class="model">使用模型：</div>
        <select name="" id="" class="modelSelect">
          <option selected disabled>ChatGpt3.5</option>
        </select>
        <div class="AI">AI资料库：</div>
        <input ref="fileInput" type="file" style="display: none;" @change="handleFileChange" accept=".txt">
        <button @click="triggerFileInput()" class="AIupload">上传资料</button>
        <button @click="create()" :class="{'disable': !isClickable}" class="create">创建角色</button>
        <div class="show_file">{{ file_show }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'CreateRoles',
  data () {
    return {
      user_id: this.$route.query.user_id,
      isModify: false,
      prompt: '', // 提示词
      role_name: '', // 角色名称
      description: '', // 角色描述
      picture_get: '', // 获取上传的头像图片
      picture_show: '', // 展示上传的头像图片
      file_get: '', // 上传的AI资料
      file_show: '', // 上传的资料名称显示
      name_length: 0, // 角色名称目前输入字数
      description_length: 0, // 角色描述目前输入字数
      isClickable: true,
      is_limit: false, // true表示该用户目前处于被限制登录状态
      isVip: false // true为VIP
    }
  },

  async created () {
    document.title = '创建角色-chataaa'
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
    triggerPictureInput () {
      this.$refs.pictureInput.click()
    },
    handlePictureChange (event) {
      const picture_temp = event.target.files[0]
      if (picture_temp && picture_temp.type.startsWith('image/')) {
        this.picture_get = picture_temp
        this.picture_show = URL.createObjectURL(this.picture_get)
        this.isModify = true
      } else {
        alert('请选择图片文件')
        event.target.value = null
      }
    },
    triggerFileInput () {
      this.$refs.fileInput.click()
    },
    handleFileChange (event) {
      const selectedFile = event.target.files[0]
      if (selectedFile && this.isTxtFile(selectedFile)) {
        this.file_get = event.target.files[0]
        this.file_show = this.file_get ? this.file_get.name : null
      } else {
        alert('请上传txt文件')
      }
    },
    isTxtFile (file) {
      return file.type === 'text/plain'
    },
    name_input () {
      this.name_length = this.role_name.length
      if (this.name_length > 25) {
        this.role_name = this.role_name.slice(0, 25)
        this.name_length = 25
      }
    },
    description_input () {
      this.description_length = this.description.length
      if (this.description_length > 25) {
        this.description = this.description.slice(0, 25)
        this.description_length = 25
      }
    },
    async create () {
      if (this.prompt.trim() === '') {
        alert('请输入提示词！')
        return
      } else if (this.picture_show === '') {
        alert(`请上传角色头像！`)
        return
      } else if (this.role_name.trim() === '') {
        alert(`请输入角色名称！`)
        return
      } else if (this.description.trim() === '') {
        alert(`请输入角色描述！`)
        return
      } else if (this.file_show === '') {
        alert(`请上传资料！`)
        return
      }
      this.isClickable = false
      let file = new FormData()
      file.append('user_id', this.user_id)
      file.append('role_name', this.role_name)
      file.append('description', this.description)
      file.append('prompt', this.prompt)
      file.append('head_portrait', this.picture_get)
      file.append('files', this.file_get)
      const res = await axios.post('http://8.134.178.190:5000/vip_user/create_user_role',file)
      console.log(res)
      if (res.data.code === '200') {
        alert(`创建成功！`)
      } else {
        alert(`创建失败！`)
      }
      this.isClickable = true
      this.role_name = ''
      this.description = ''
      this.prompt = ''
      this.picture_get = null,
      this.picture_show = null,
      this.file_get = null,
      this.file_show = null
      this.isModify = false
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
    setting () {
      this.$router.push({
        path: '/setting',
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
    color: #1990FF;
  }

  .leftText .four {
    position: absolute;
    top: 450px;
  }

  .leftText .five {
    position: absolute;
    top: 570px;
  }

  .right {
    position: relative;
    width: 1450px;
    background-color: #F2F5F8;
    background-image: url('../assets/createRoles.png');
    /* background-repeat: no-repeat; */
    background-size: 1450px 920px;
  }

  .right .main {
    position: relative;
    width: 700px;
    height: 100%;
    background-color: #fff;
    border: 1px solid #BBB;
    margin: 0 auto;
  }

  .right .title {
    width: 700px;
    height: 40px;
    border-bottom: 1px solid #BBB;
    font-size: 17px;
    line-height: 40px;
    text-align: center;
    font-weight: 700;
  }

  .right .prompt {
    position: absolute;
    left: 70px;
    top: 70px;
    font-size: 17px;
    font-weight: 700;
    z-index: 99;
  }
  .right textarea {
    position: absolute;
    left: 60px;
    top: 65px;
    width: 580px;
    height: 200px;
    background-color: #fff;
    border: 1px solid #809CFF;
    border-radius: 15px;
    padding: 10px;
    font-size: 18px;
    resize: none;
    padding-top: 35px;
  }

  .right .head_text {
    position: relative;
    font-size: 17px;
    font-weight: 700;
    top: 280px;
    left: 60px;
  }

  .right .head_picture {
    position: absolute;
    top: 290px;
    left: 150px;
    width: 90px;
    height: 90px;
    background-color: #fff;
    border: 2px dashed #BBB;
    border-radius: 10px;
    color: #BBB;
    font-size: 40px;
    line-height: 75px;
    text-align: center;
  }

  .right .head_picture:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .name {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 410px;
  }
  
  .right .nameInput {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 410px;
    width: 410px;
    height: 27px;
    padding: 2px;
  }

  .right .name_length {
    position: absolute;
    font-size: 16px;
    left: 575px;
    top: 410px;
  }

  .right .describe {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 460px;
  }

  .right .describeInput {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 460px;
    width: 410px;
    height: 27px;
    padding: 2px;
  }

  .right .description_length {
    position: absolute;
    font-size: 16px;
    left: 575px;
    top: 460px;
  }

  .right .divergence {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 510px;
  }

  .right .divergenceSelect {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 510px;
    width: 120px;
    height: 27px;
    padding: 2px;
  }

  .right .model {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 560px;
  }

  .right .modelSelect {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 560px;
    width: 120px;
    height: 27px;
    padding: 2px;
  }

  .right .AI {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 620px;
  }

  .right .AIupload {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 610px;
    width: 100px;
    height: 40px;
    padding: 2px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 10px;
  }

  .right .AIupload:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .create {
    position: absolute;
    font-size: 17px;
    left: 100px;
    bottom: 20px;
    width: 500px;
    height: 40px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 7px;
  }

  .right .create:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .show_picture img {
    position: absolute;
    top: 290px;
    left: 150px;
    width: 90px;
    height: 90px;
    border-radius: 50%;
  }

  .right .show_picture img:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .show_file {
    position: absolute;
    left: 260px;
    top: 620px;
  }

  .disable {
    pointer-events: none;
    opacity: 0.5;
  }
</style>