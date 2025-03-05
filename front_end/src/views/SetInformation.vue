<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li class="one">信息设置</li>
        <li @click="manageUsers()" class="two">用户管理</li>
        <li @click="seeInfo()" class="three">查看信息</li>
        <li @click="feedback()" class="four">用户反馈</li>
        <li class="five" @click="exit">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <div v-if="noModify" class="display">
        <h2>信息设置</h2>
        <div class="contactUs">
          <span class="contactUsLeft">“联系我们”：</span>
          <span>{{ contact_way_show }}</span>
        </div>
        <div class="userMustKnow">
          <span>“用户须知”：</span>
          <textarea v-model="user_agreement_show" disabled></textarea>
        </div>
        <div class="advertisement">
          <span>广告图片：</span>
          <button @click="seePicture()" class="seePicture">查看图片</button>
        </div>
        <div class="jump">
          <span>广告链接：</span>
          <span class="link">{{ link_show }}</span>
        </div>
        <div class="edit" @click="edit()">编辑</div>
        <div class="picture" v-show="picture_show !== null">
          <img :src="picture_show" alt="">
          <div @click="closePic()" class="closePic">❎</div>
        </div>
      </div>
      <div v-else class="modifying">
        <h2>信息设置</h2>
        <div class="contactUs">
          <span class="contactUsLeft">“联系我们”内容设置：</span>
          <input v-model="contact_way" type="text" name="" id="">
        </div>
        <div class="userMustKnow">
          <span>“用户须知”内容设置：</span>
          <textarea v-model="user_agreement"></textarea>
        </div>
        <div class="advertisement">
          <span>广告图片设置：</span>
          <input ref="pictureInput" type="file" style="display: none;" name="image" accept="image/*" @change="handlePictureChange">
          <button @click="triggerPictureInput()" class="upload">上传图片</button>
          <span>{{ picture_name }}</span>
        </div>
        <div class="jump">
          <span>广告链接设置：</span>
          <input v-model="link" type="text">
        </div>
        <div class="cancel" @click="cancel()">取消</div>
        <div class="chess" @click="chess()">确定</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'SetInformation',
  data () {
    return {
      user_id: this.$route.query.user_id,
      noModify: true,
      contact_way: '', // 联系我们编辑
      user_agreement: '', // 用户须知编辑
      contact_way_show: '', // 联系我们展示
      user_agreement_show: '', // 用户须知展示
      picture_temp: null, // 暂时存储广告图片url
      picture_show: null, // 展示广告图片url
      picture_get: null, // 获取上传的广告图片
      picture_name: '', // 显示上传图片名称
      link: '', // 广告链接编辑
      link_show: '', // 广告链接展示
    }
  },

  created () {
    document.title = '设置信息-chataaa'
    this.getInfo()
  },

  methods: {
    manageUsers () {
      this.$router.push({
        path: '/manageUsers',
        query : {
          user_id: this.user_id
        }
      })
    },
    seeInfo () {
      this.$router.push({
        path: '/seeInformation',
        query: {
          user_id: this.user_id
        }
      })
    },
    feedback () {
      this.$router.push({
        path: '/seeFeedBack',
        query : {
          user_id: this.user_id
        }
      })
    },
    edit () {
      this.contact_way = this.contact_way_show
      this.user_agreement = this.user_agreement_show
      this.picture_name = this.picture_name_show
      this.link = this.link_show
      this.noModify = false
      console.log('edit')
    },
    async getInfo () {
      const res1 = await axios.get('http://8.134.178.190:5000/administrator/get_company_info')
      console.log(res1)
      this.contact_way_show = res1.data.data.contact_way
      this.user_agreement_show = res1.data.data.user_agreement

      const res2 = await axios.get('http://8.134.178.190:5000/administrator/get_old_advertise', {
        params: {

        },
        responseType: 'blob'
      })
      if (res2.data.code === '400') {
          alert('获取图片失败')
          return
        }
      const imgUrl = URL.createObjectURL(res2.data)
      this.picture_temp = imgUrl

      const res3 = await axios.get('http://8.134.178.190:5000/administrator/get_url_link')
      if (res3.data.code === '400') {
        alert('上传链接错误')
        return
      }
      this.link_show = res3.data.data.url
      console.log(res3)
    },
    seePicture () {
      this.picture_show = this.picture_temp
    },
    closePic () {
      this.picture_show = null
    },
    triggerPictureInput () {
      this.$refs.pictureInput.click()
    },
    handlePictureChange (event) {
      const picture_temp = event.target.files[0]
      if (picture_temp && picture_temp.type.startsWith('image/')) {
        this.picture_get = picture_temp
        this.picture_name = this.picture_get.name
      } else {
        alert('请选择图片文件')
        event.target.value = null
      }
    },
    cancel () {
      this.noModify = true
    },
    async chess () {
      const res1 = await axios.post('http://8.134.178.190:5000/administrator/set_company_info', {
        contact_way: this.contact_way,
        user_agreement: this.user_agreement
      })
      if (res1.data.code === '400') {
        alert('上传信息错误')
        return
      }
      this.contact_way_show = this.contact_way
      this.user_agreement_show = this.user_agreement

      if (this.picture_get !== null) {
        let picture = new FormData()
        picture.append('advertise', this.picture_get)
        const res2 = await axios.post('http://8.134.178.190:5000/administrator/set_advertising', picture)
        if (res2.data.code === '400') {
          alert('上传图片错误')
          return
        }
        this.picture_temp = URL.createObjectURL(this.picture_get)
        this.picture_get = null
      }

      const res3 = await axios.post('http://8.134.178.190:5000/administrator/change_url_link', {
        url: this.link
      })
      if (res3.data.code === '400') {
        alert('上传链接错误')
        return
      }
      this.link_show = this.link

      this.noModify = !this.noModify
      alert('设置成功！')
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
    color: #1990FF;
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
  }

  .leftText .five {
    position: absolute;
    top: 570px;
  }

  .right {
    width: 1450px;
    background-color: #F2F5F8;
  }

  .right h2 {
    width: 1400px;
    height: 70px;
    text-align: center;
    line-height: 70px;
    margin: 0 auto;
    border-bottom: 1px solid #BBBBBB;
  }

  .right .display {
    position: relative;
    font-size: 18px;
  }

  .contactUs {
    position: absolute;
    left: 30px;
    top: 120px;
  }

  .contactUsLeft {
    padding-right: 40px;
  }

  .userMustKnow {
    display: flex;
    position: absolute;
    left: 30px;
    top: 190px;
  }

  .userMustKnow span {
    padding-right: 40px;
  }

  .userMustKnow textarea {
    width: 1000px;
    height: 400px;
    background-color: #fff;
    border-radius: 15px;
    padding: 10px;
    font-size: 18px;
    resize: none;
  }

  .display .edit {
    position: absolute;
    top: 100px;
    right: 100px;
    width: 100px;
    height: 50px;
    border-radius: 6px;
    border: 2px solid skyblue;
    line-height: 50px;
    text-align: center;
    font-size: 20px;
    color: #1990FF;
    font-weight: 700;
  }

  .display .edit:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }

  .right .modifying {
    position: relative;
    font-size: 18px;
  }

  .contactUs input {
    width: 300px;
    height: 30px;
    padding: 5px;
    font-size: 18px;
  }

  .advertisement {
    position: absolute;
    top: 610px;
    left: 100px;
  }

  .advertisement span {
    padding-right: 40px;
  }

  .advertisement .seePicture {
    width: 150px;
    height: 35px;
    background: #94cbff;
    border-radius: 10px;
    border: none;
    font-size: 18px;
    margin-right: 10px;
  }

  .advertisement .seePicture:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .advertisement .upload {
    width: 150px;
    height: 35px;
    background: #94cbff;
    border-radius: 10px;
    border: none;
    font-size: 18px;
    margin-right: 10px;
  }

  .advertisement .upload:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .jump {
    position: absolute;
    top: 670px;
    left: 100px;
  }

  .jump span {
    padding-right: 40px;
  }

  .jump input {
    width: 500px;
    height: 30px;
    padding: 5px;
    font-size: 18px;
  }

  .jump .link {
    width: 500px;
    height: 30px;
    padding: 5px;
    font-size: 18px;
  }

  .modifying .cancel {
    position: absolute;
    top: 660px;
    right: 170px;
    width: 100px;
    height: 50px;
    border-radius: 6px;
    border: 2px solid skyblue;
    line-height: 50px;
    text-align: center;
    font-size: 20px;
    color: #1990FF;
    font-weight: 700;
  }

  .modifying .cancel:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }

  .modifying .chess {
    position: absolute;
    top: 660px;
    right: 60px;
    width: 100px;
    height: 50px;
    border-radius: 6px;
    border: 2px solid skyblue;
    line-height: 50px;
    text-align: center;
    font-size: 20px;
    color: #1990FF;
    font-weight: 700;
  }

  .modifying .chess:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }

  .picture {
    position: absolute;
    width: 800px;
    height: 500px;
    left: 400px;
    top: 120px;
    z-index: 1005;
  }

  .picture img {
    width: 800px;
    height: 500px;
  }

  .picture .closePic {
    position: absolute;
    right: 10px;
    top: 10px;
    cursor: pointer;
  }
</style>