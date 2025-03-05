<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="setInfo()" class="one">信息设置</li>
        <li @click="manageUsers()" class="two">用户管理</li>
        <li class="three">查看信息</li>
        <li @click="feedback()" class="four">用户反馈</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSeeing">查看信息</div>
      <div @click="showLogin()" class="seeingTop" :class="{'active': show_login}">用户登录信息</div>
      <div @click="showError()" class="seeingTop" :class="{'active': !show_login}">系统错误日志</div>
      <div @click="toVipInfo()" class="seeingTop">会员充值信息</div>
    </div>
    <div class="right">
      <form v-show="show_login">
        <div class="rightTop">用户登录信息</div>
        <div class="rightMain">
          <table>
            <tr>
              <th>邮箱</th>
              <th>时间</th>
              <th>登入/登出</th>
            </tr>
            <tr v-for="(item, index) in login_log" :key="index">
              <td>{{ item.mail_account }}</td>
              <td>{{ item.timing }}</td>
              <td>{{ item.type }}</td>
            </tr>
          </table>
        </div>
        <button @click="downloadCSV1()" class="export">导出数据</button>
      </form>
      <form v-show="!show_login">
        <div class="rightTop">系统错误日志</div>
        <div class="rightMain">
          <table>
            <tr>
              <th>时间</th>
              <th>错误码</th>
              <th>错误信息</th>
            </tr>
            <tr v-for="(item, index) in error_log" :key="index">
              <td>{{ item.timing }}</td>
              <td>{{ item.error_code }}</td>
              <td>{{ item.error_description }}</td>
            </tr>
          </table>
        </div>
        <button @click="downloadCSV2()" class="export">导出数据</button>
    </form>
    </div>
  </div>
</template>

<script>
import { saveAs } from 'file-saver'
import axios from 'axios' 
export default {
  name: 'SeeInformation',
  data () {
    return { 
      user_id: this.$route.query.user_id,
      show_login: true, // true显示登录信息
      login_log: [],
      error_log: []
    }
  },

  async created () {
    document.title = '查看信息-chataaa'
    const res1 = await axios.get('http://8.134.178.190:5000/administrator/log/get_all_log')
    this.login_log = res1.data.data
    const res2 = await axios.get('http://8.134.178.190:5000/administrator/log/get_error_log')
    this.error_log = res2.data.data
    console.log(res1)
    console.log(res2)
  },

  methods: {
    setInfo () {
      this.$router.push({
        path: '/setInformation',
        query: {
          user_id: this.user_id
        }
      })
    },
    manageUsers () {
      this.$router.push({
        path: '/manageUsers',
        query: {
          user_id: this.user_id
        }
      })
    },
    feedback () {
      this.$router.push({
        path: '/seeFeedBack',
        query: {
          user_id: this.user_id
        }
      })
    },
    downloadCSV1 () { // 导出登入/登出信息
      const csv = this.convertToCSV(this.login_log); // 将login_log数组转换为CSV字符串
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" }); // 创建一个Blob对象
      saveAs(blob, "login_information.csv"); // 使用FileSaver.js库将Blob对象保存为文件
    },
    downloadCSV2 () { // 导出错误信息
      const csv = this.convertToCSV(this.error_log); // 将error_log数组转换为CSV字符串
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" }); // 创建一个Blob对象
      saveAs(blob, "error_information.csv"); // 使用FileSaver.js库将Blob对象保存为文件
    },
    convertToCSV(arr) {
      const header = Object.keys(arr[0]).join(","); // 获取CSV文件的header
      const rows = arr.map(obj => Object.values(obj).join(",")); // 将数组中的每个对象转换为一个CSV行
      return `${header}\n${rows.join("\n")}`; // 将header和所有行拼接成一个CSV字符串
    },
    showLogin () {
      this.show_login = true
    },
    showError () {
      this.show_login = false
    },
    toVipInfo () {
      this.$router.push({
        path: '/ordersInformation',
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

  .middle {
    position: relative;
    width: 200px;
    background-color: #F6FBFF;
    border: 1px solid #BBBBBB;
    font-size: 17px;
  }

  .middleSeeing {
    padding: 5px 0 10px 20px;
    font-size: 20px;
  }

  .seeingTop {
    text-align: center;
    padding-bottom: 12px;
  }

  .seeingTop:hover {
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
    border-bottom: 1px solid #BBB;
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    padding: 15px;
  }
  .right .rightMain {
    position: absolute;
    left: 150px;
    top: 100px;
    width: 900px;
    height: 570px;
    font-size: 17px;
    background-color: #fff;
    overflow: auto;
    border: 2px solid #BBBBBB;
  }

  .rightMain table {
    border-collapse: collapse;
  }

  .rightMain th, td {
    text-align: center;
    width: 300px;
    height: 50px;
    border: 1px solid #BBBBBB;
  }

  .right .export {
    position: absolute;
    bottom: 60px;
    left: 1070px;
    width: 100px;
    height: 40px;
    border-radius: 6px;
    border: 4px solid #D6ECFF;
    line-height: 30px;
    color: #1990FF;
    font-weight: 700;
  }

  .right .export:hover {
    background-color: #D6ECFF;
    cursor: pointer;
  }
</style>