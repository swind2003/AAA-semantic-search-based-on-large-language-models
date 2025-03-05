<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="setInfo()" class="one">信息设置</li>
        <li class="two">用户管理</li>
        <li @click="seeInfo()" class="three">查看信息</li>
        <li @click="toFeedback()" class="four">用户反馈</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <h2>用户管理</h2>
      <div class="inp1">
      <span>用户邮箱： </span><input v-model="mail_account" type="text" placeholder="请输入用户邮箱">
      </div>
      <div class="inp2">
        <span>用户昵称： </span><input v-model="nickname" type="text" placeholder="请输入用户昵称">
      </div>
      <button @click="search()" class="query">查询</button>
      <div class="Table">
        <table>
          <thead>
            <tr>
              <th style="width: 100px;">头像</th>
              <th style="width: 300px;">用户邮箱</th>
              <th style="width: 250px;">用户昵称</th>
              <th style="width: 100px;">性别</th>
              <th style="width: 100px;">VIP</th>
              <th style="width: 400px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(info, index1) in user_information" :key="index1">
              <td v-for="(picture, index2) in pictures" :key="index2" v-show="index1 === index2" class="imgWrapped">
                <img :src="picture" alt="">
              </td>
              <td>{{ info.mail_account }}</td>
              <td>{{ info.nickname }}</td>
              <td>{{ info.sex }}</td>
              <td>{{ info.is_vip }}</td>
              <td>
                <button v-if="info.if_login_limit === 'false'" class="operation" @click="limitLogin(index1, info.user_id)">限制登录</button>
                <button v-else-if="info.if_login_limit === 'true'" class="operation active" @click="allowLogin(index1, info.user_id)">允许登录</button>
                <button v-if="info.if_times_limit === 'false'" class="operation" @click="limitTimes(index1, info.user_id)">限制次数</button>
                <button v-else-if="info.if_times_limit === 'true'" class="operation active" @click="allowTimes(index1, info.user_id)">解除限次</button>
                <button @click="isDel(info.user_id)" class="operation" >删除用户</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="limitWindow" v-show="showLoginLimit">
        <h3>限制登录</h3>
        <span>限制时间：</span>
        <select v-model="limitDays" name="" id="">
          <option value="1">1天</option>
          <option value="3">3天</option>
          <option value="5">5天</option>
          <option value="7">7天</option>
          <option value="14">14天</option>
        </select>
        <br>
        <button @click="yesLogin()">确定</button> <button @click="noLogin()">取消</button>
      </div>
      <div class="limitWindow" v-show="showTimesLimit">
        <h3>限制次数</h3>
        <span>限制每小时次数：</span>
        <select v-model="limittimes" name="" id="">
          <option value="1">1次/h</option>
          <option value="3">3次/h</option>
          <option value="5">5次/h</option>
        </select>
        <br>
        <button @click="yesTimes()">确定</button> <button @click="noTimes()">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ManageUsers',
  data () {
    return {
      user_id_administrators: this.$route.query.user_id, // 管理员的user_id
      user_id: '',
      // loginShow: true, // 显示限制登录/允许登录
      showLoginLimit: false, // 是否显示选择限制登录天数窗口
      // timesShow: true, // 显示限制次数/解除限次
      showTimesLimit: false, // 是否显示选择限制次数窗口
      user_information: [], // 存储用户信息
      index: 0,
      limitDays: '1', // 获取限制登录的天数
      limittimes: '1', // 获取限制的次数
      mail_account: '', // 搜索输入的邮箱
      nickname: '', // 搜索输入的昵称
      pictures: [], // 头像
    }
  },

  created () {
    document.title = '用户管理-chataaa'
    this.getInfo()
  },

  // mounted () {
  //   this.getPictures(this.user_id)
  // },

  methods: {
    setInfo () {
      this.$router.push({
        path: '/setInformation',
        query : {
          user_id: this.user_id_administrators
        }
      })
    },
    seeInfo () {
      this.$router.push({
        path: '/seeInformation',
        query : {
          user_id: this.user_id_administrators
        }
      })
    },
    toFeedback () {
      this.$router.push({
        path: '/seeFeedBack',
        query: {
          user_id: this.user_id_administrators
        }
      })
    },
    async exit () {
      const res = await axios.post('http://8.134.178.190:5000/login_system/log_out', {
        user_id: this.user_id_administrators
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
    async getInfo () {
      const res = await axios.get('http://8.134.178.190:5000/administrator/get_all_user')
      this.user_information = res.data.data
      // console.log(res)
      this.getPictures(this.user_information)
    },
    async getPictures (user_information) {
      this.pictures = []
      let length = user_information.length
      for (let i = 0 ; i < length; i++) {
        const res = await axios.get('http://8.134.178.190:5000/user/information/get_head_portrait', {
          params: {
            user_id: user_information[i].user_id
          },
          responseType: 'blob'
        })
        if (res.data.code === '400') {
          alert('获取图片失败')
          return
        }
        const imgUrl = URL.createObjectURL(res.data)
        this.pictures.push(imgUrl)
      }
    },
    async search () { // 查询
      const res = await axios.get('http://8.134.178.190:5000/administrator/search_user', {
        params: {
          mail_account: this.mail_account,
          nickname: this.nickname
        }
      })
      console.log(res)
      this.user_information = res.data.data
      this.mail_account = ''
      this.nickname = ''
      this.getPictures(this.user_information)
    },
    limitLogin (index, user_id) { // 点击限制次数登录
      this.showLoginLimit = true
      this.index = index
      this.user_id = user_id
    },
    async yesLogin () { // 确定限制登录
      this.showLoginLimit = false
      this.user_information
      this.user_information[this.index].if_login_limit = 'true'
      const res = await axios.post('http://8.134.178.190:5000/administrator/restrict_login', {
        user_id: this.user_id,
        number_time: this.limitDays,
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
    },
    noLogin () { // 取消限制登录选择
      this.showLoginLimit = false
    },
    async allowLogin (index, user_id) { // 解除登录限制
      this.loginShow = true
      this.index = index
      this.user_id = user_id
      this.user_information[this.index].if_login_limit = 'false'
      const res = await axios.post('http://8.134.178.190:5000/administrator/restrict_login', {
        user_id: this.user_id,
        number_time: '0',
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
    },
    limitTimes (index, user_id) { // 点击限制次数
      this.showTimesLimit = true
      this.index = index
      this.user_id = user_id
    },
    async yesTimes () { // 确定限制次数
      this.showTimesLimit = false
      this.user_information[this.index].if_times_limit = 'true'
      const res = await axios.post('http://8.134.178.190:5000/administrator/restrict_query', {
        user_id: this.user_id,
        query_times: this.limittimes,
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
    },
    noTimes () { // 取消限制次数选择
      this.showTimesLimit = false
    },
    async allowTimes (index, user_id) { // 解除次数限制
      // this.timesShow = true
      this.index = index
      this.user_id = user_id
      this.user_information[this.index].if_times_limit = 'false'
      const res = await axios.post('http://8.134.178.190:5000/administrator/restrict_query', {
        user_id: this.user_id,
        query_times: '8',
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
    },
    async del(user_id) {
      const res = await axios.delete(`http://8.134.178.190:5000/administrator/delete_user?user_id=${user_id}`)
      if (res.data.code === '400') {
        alert('删除失败')
        return
      }
      this.getInfo()
    },
    isDel (user_id) { // 确认是否删除用户
      const isConfirmed = window.confirm('确定要删除该用户吗？')
      if (isConfirmed) {
        this.del(user_id)
      } else {
        console.log('取消删除用户')
      }
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
    color: #1990FF;
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
    position: relative;
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

  .right input {
    width: 300px;
    height: 30px;
    padding: 5px;
    font-size: 18px;
  }

  .right .inp1 {
    position: absolute;
    top: 130px;
    left: 180px;
    font-size: 18px;
  }

  .right .inp2 {
    position: absolute;
    top: 130px;
    left: 600px;
    font-size: 18px;
  }

  .right .query {
    position: absolute;
    top: 130px;
    left: 1050px;
    font-size: 18px;
    width: 100px;
    height: 30px;
    background-color: #809CFF;
    border: none;
  }

  .right .query:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .Table {
    position: absolute;
    top: 200px;
    left: 100px;
    width: 1250px;
    height: 450px;
    background-color: #fff;
    border: 2px solid #BBBBBB;
    overflow: auto;
  }

  table {
    border-collapse: collapse;
  }

  .Table th, td {
    text-align: center;
    height: 50px;
    border: 1px solid #BBBBBB;
  }

  .imgWrapped {
    position: relative;
  }

  .Table img {
    position: absolute;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    top: 5px;
    left: 30px;
  }

  .Table .operation {
    width: 90px;
    height: 30px;
    margin-right: 15px;
    background-color: #9CBFFB;
    border: none;
  }

  .operation.active {
  background-color: orange;
}

  .Table button:hover {
    opacity: 0.7;
    cursor: pointer;
  }

  .limitWindow {
    position: absolute;
    width: 500px;
    height: 200px;
    background-color: #F6FBFF;
    border: 3px solid #000;
    text-align: center;
    top: 220px;
    left: 475px;
    border-radius: 15px;
  }

  .limitWindow h3 {
    width: 500px;
    height: 40px;
    line-height: 40px;
    margin-bottom: 20px;
    border-bottom: 1px solid #BBBBBB;
  }

  .limitWindow span {
    font-size: 17px;
  }

  .limitWindow button {
    width: 100px;
    height: 40px;
    background-color: #fff;
    margin-top: 30px;
    margin-right: 60px;
    margin-left: 60px;
    border-radius: 5px;
  }

  .limitWindow button:hover {
    opacity: 0.6;
    cursor: pointer;
  }
</style>