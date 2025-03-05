<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="setInfo()" class="one">信息设置</li>
        <li @click="manageUsers()" class="two">用户管理</li>
        <li @click="seeInfo()" class="three">查看信息</li>
        <li @click="feedback()" class="four">用户反馈</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSeeing">查看信息</div>
      <div @click="toInfo()" class="seeingTop">日志信息</div>
      <div class="seeingTop active">会员充值信息</div>
    </div>
    <div class="right">
      <div class="rightTop">会员充值订单</div>
      <div class="dateBegin">
        <select id="year" v-model="selectedYear1" @change="updateMonths1">
          <option v-for="year in availableYears1" :key="year" :value="year">{{ year }}</option>
        </select>
        <label for="year"> 年 </label>

        <select id="month" v-model="selectedMonth1" @change="updateDays1">
          <option v-for="month in availableMonths1" :key="month" :value="month">{{ month }}</option>
        </select>
        <label for="month"> 月 </label>

        <select id="day" v-model="selectedDay1">
          <option v-for="day in availableDays1" :key="day" :value="day">{{ day }}</option>
        </select>
        <label for="day"> 日 </label>
      </div>
      <div class="transition">————</div>
      <div class="dateEnd">
        <select id="year" v-model="selectedYear2" @change="updateMonths2">
          <option v-for="year in availableYears2" :key="year" :value="year">{{ year }}</option>
        </select>
        <label for="year"> 年 </label>

        <select id="month" v-model="selectedMonth2" @change="updateDays2">
          <option v-for="month in availableMonths2" :key="month" :value="month">{{ month }}</option>
        </select>
        <label for="month"> 月 </label>

        <select id="day" v-model="selectedDay2">
          <option v-for="day in availableDays2" :key="day" :value="day">{{ day }}</option>
        </select>
        <label for="day"> 日 </label>
      </div>
      <button @click="query()" class="query">查询</button>
      <button @click="showAll()" class="showAll">显示全部</button>
      <div class="rightMain">
        <table>
          <tr>
            <th>邮箱</th>
            <th>日期时间</th>
            <th>充值类型</th>
            <th>充值金额</th>
          </tr>
          <tr v-for="(item, index) in orders" :key="index">
            <td>{{ item.mail_account }}</td>
            <td>{{ item.order_time }}</td>
            <td>{{ item.type }}</td>
            <td>{{ item.price }}</td>
          </tr>
        </table>
      </div>
      <button @click="downloadCSV1()" class="export">导出数据</button>
    </div>
  </div>
</template>

<script>
import { saveAs } from 'file-saver'
import axios from 'axios' 
export default {
  name: 'OrdersInformation',
  data () {
    return {
      user_id: this.$route.query.user_id,

      selectedYear1: '', // 开始选择年份
      selectedMonth1: '', // 开始选择月份
      selectedDay1: '', // 开始选择天数
      availableYears1: [],   // 存储可选的年份（开始）
      availableMonths1: [],  // 存储可选的月份（开始）
      availableDays1: [],   // 存储可选的天数（开始）

      selectedYear2: '', // 结束选择年份
      selectedMonth2: '', // 结束选择月份
      selectedDay2: '', // 结束选择天数
      availableYears2: [],   // 存储可选的年份（结束）
      availableMonths2: [],  // 存储可选的月份（结束）
      availableDays2: [],   // 存储可选的天数（结束）

      orders: [],
    }
  },

  async created () {
    document.title = '查看订单-chataaa'
    this.getInfo()
  },

  mounted () {
    this.updateYears1(); // 初始化开始年份
    this.updateMonths1(); // 初始开始化月份
    this.updateDays1(); // 初始化开始天数
    this.updateYears2(); // 初始化结束年份
    this.updateMonths2(); // 初始化结束月份
    this.updateDays2(); // 初始化结束天数
  },

  methods: {
    async getInfo () {
      const res = await axios.get('http://8.134.178.190:5000/administrator/check_order')
      this.orders = res.data.data
    },
    updateYears1() {
      const currentYear = new Date().getFullYear();
      // 如果当前年份不在availableYears中，则添加
      for (let Year = 2023; Year <= currentYear; Year++) {
        this.availableYears1.push(Year)
      }
    },
    updateMonths1() {
      const months = Array.from({ length: 12 }, (_, index) => index + 1);
      this.availableMonths1 = months;
      this.selectedMonth1 = ''; // 重置月份
      this.updateDays1(); // 更新天数
    },
    updateDays1() {
      const selectedYear = parseInt(this.selectedYear1);
      const selectedMonth = parseInt(this.selectedMonth1);
      const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
      const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
      this.availableDays1 = days;

      // 如果当前选择的天数超过新的天数范围，则重置为最大天数
      if (parseInt(this.selectedDay1) > daysInMonth) {
      this.selectedDay1 = '';
      }
    },
    updateYears2() {
      const currentYear = new Date().getFullYear();
      // 如果当前年份不在availableYears中，则添加
      for (let Year = 2023; Year <= currentYear; Year++) {
        this.availableYears2.push(Year)
      }
    },
    updateMonths2() {
      const months = Array.from({ length: 12 }, (_, index) => index + 1);
      this.availableMonths2 = months;
      this.selectedMonth2 = ''; // 重置月份
      this.updateDays2(); // 更新天数
    },
    updateDays2() {
      const selectedYear = parseInt(this.selectedYear2);
      const selectedMonth = parseInt(this.selectedMonth2);
      const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
      const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
      this.availableDays2 = days;

      // 如果当前选择的天数超过新的天数范围，则重置为最大天数
      if (parseInt(this.selectedDay2) > daysInMonth) {
      this.selectedDay2 = '';
      }
    },
    formatDate (year, month, day) {
      const formatMonth = String(month).padStart(2, '0')
      const formatDay = String(day).padStart(2, '0')
      return `${year}-${formatMonth}-${formatDay}`
    },
    async query () {
      if (this.selectedYear1 > this.selectedYear2 && this.selectedYear1 !== '' && this.selectedYear2 !== '') {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 === this.selectedYear2 && this.selectedMonth1 > this.selectedMonth2) {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 === this.selectedYear2 && this.selectedMonth1 === this.selectedMonth2 && this.selectedDay1 > this.selectedDay2) {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 !== '' && this.selectedMonth1 !== '' && this.selectedDay1 !== '' && this.selectedYear2 !== '' && this.selectedMonth2 !== '' && this.selectedDay2 !== '') {
        const startDate = this.formatDate(this.selectedYear1, this.selectedMonth1, this.selectedDay1)
        const endDate = this.formatDate(this.selectedYear2, this.selectedMonth2, this.selectedDay2)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_order',{
          params: {
            start_date: startDate,
            end_date: endDate
          }
        })
        this.orders = res.data.data
      } else if (this.selectedYear1 === '' && this.selectedMonth1 === '' && this.selectedDay1 === '' && this.selectedYear2 !== '' && this.selectedMonth2 !== '' && this.selectedDay2 !== '') {
        const endDate = this.formatDate(this.selectedYear2, this.selectedMonth2, this.selectedDay2)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_order',{
          params: {
            end_date: endDate
          }
        })
        this.orders = res.data.data
      } else if (this.selectedYear1 !== '' && this.selectedMonth1 !== '' && this.selectedDay1 !== '' && this.selectedYear2 === '' && this.selectedMonth2 === '' && this.selectedDay2 === '') {
        const startDate = this.formatDate(this.selectedYear1, this.selectedMonth1, this.selectedDay1)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_order',{
          params: {
            start_date: startDate,
          }
        })
        this.orders = res.data.data
      } else {
        alert('请输入正确的时间区间！')
        return
      }
    },
    showAll () {
      this.getInfo()
      this.selectedYear1 = ''
      this.selectedYear2 = ''
      this.selectedMonth1 = ''
      this.selectedMonth2 = ''
      this.selectedDay1 = ''
      this.selectedDay2 = ''
    },
    downloadCSV1 () { // 导出会员订单信息
      const csv = this.convertToCSV(this.orders); // 将login_log数组转换为CSV字符串
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" }); // 创建一个Blob对象
      saveAs(blob, "order_information.csv"); // 使用FileSaver.js库将Blob对象保存为文件
    },
    convertToCSV(arr) {
      const header = Object.keys(arr[0]).join(","); // 获取CSV文件的header
      const rows = arr.map(obj => Object.values(obj).join(",")); // 将数组中的每个对象转换为一个CSV行
      return `${header}\n${rows.join("\n")}`; // 将header和所有行拼接成一个CSV字符串
    },
    toInfo () {
      this.$router.push({
        path: '/seeInformation',
        query: {
          user_id: this.user_id
        }
      })
    },
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
    left: 120px;
    top: 140px;
    width: 900px;
    height: 550px;
    font-size: 17px;
    background-color: #fff;
    overflow: auto;
    border: 2px solid #BBBBBB;
  }

  .right .dateBegin {
    position: absolute;
    top: 100px;
    left: 180px;
    font-size: 17px;
  }

  .right .transition {
    position: absolute;
    top: 101px;
    left: 395px;
    font-weight: 700;
  }

  .right .dateEnd {
    position: absolute;
    top: 100px;
    left: 480px;
    font-size: 17px;
  }

  .right .query {
    position: absolute;
    top: 100px;
    left: 710px;
    font-size: 17px;
    width: 100px;
    height: 26px;
    background-color: #809CFF;
    border: none;
  }

  .right .query:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .showAll {
    position: absolute;
    top: 100px;
    left: 850px;
    font-size: 17px;
    width: 100px;
    height: 26px;
    background-color: #809CFF;
    border: none;
  }

  .right .showAll:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .rightMain table {
    border-collapse: collapse;
  }

  .rightMain th, td {
    text-align: center;
    width: 300px;
    height: 40px;
    border: 1px solid #BBBBBB;
  }


  .right .export {
    position: absolute;
    bottom: 20px;
    left: 1060px;
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